// HEADER

#ifndef HLTrigger_Muon_HLTTopoMuonHTPNetBXGBProducer_h
#define HLTrigger_Muon_HLTTopoMuonHTPNetBXGBProducer_h

#include <array>
#include <memory>
#include <sstream>

#include "DataFormats/BTauReco/interface/JetTag.h"
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToValue.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/METReco/interface/METCollection.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidateFwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "xgboost/c_api.h"

class HLTTopoMuonHTPNetBXGBProducer : public edm::stream::EDProducer<> {
 public:
  // using RecoChargedCandMap = edm::AssociationMap
  //   edm::OneToValue<std::vector<reco::RecoChargedCandidate>, float>>;

  static constexpr unsigned int kNFeatures = 6;

  explicit HLTTopoMuonHTPNetBXGBProducer(edm::ParameterSet const&);
  ~HLTTopoMuonHTPNetBXGBProducer() override;

  static void fillDescriptions(edm::ConfigurationDescriptions&);

 private:
  void produce(edm::Event&, edm::EventSetup const&) override;

  /* Tokens */
  edm::EDGetTokenT<reco::RecoChargedCandidateCollection>
      chargedCandidatesToken_;
  edm::EDGetTokenT<edm::ValueMap<float>> ecalIsoMapToken_;
  edm::EDGetTokenT<edm::ValueMap<float>> hcalIsoMapToken_;
  edm::EDGetTokenT<edm::ValueMap<double>> trackIsoMapToken_;
  edm::EDGetTokenT<reco::METCollection> pfhtToken_;
  edm::EDGetTokenT<reco::JetTagCollection> pnetToken_;

  /* Cuts */
  double muonPtCut_;
  double muonEtaCut_;

  /* XGBoost — one instance per stream, no sharing, no locking needed */
  BoosterHandle booster_ = nullptr;
  DMatrixHandle dmat_ = nullptr;

  // Persistent feature buffer; filled each event, then passed to XGBoost
  mutable std::array<float, kNFeatures> buffer_;

  std::string xgbConfig_;

  bool debug_;
};

#endif

// MAIN SOURCE

#include <cmath>
#include <iostream>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/getRef.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

HLTTopoMuonHTPNetBXGBProducer::HLTTopoMuonHTPNetBXGBProducer(
    edm::ParameterSet const& iConfig)

    : chargedCandidatesToken_(
          consumes(iConfig.getParameter<edm::InputTag>("ChargedCandidates"))),
      ecalIsoMapToken_(
          consumes(iConfig.getParameter<edm::InputTag>("EcalPFClusterIsoMap"))),
      hcalIsoMapToken_(
          consumes(iConfig.getParameter<edm::InputTag>("HcalPFClusterIsoMap"))),
      trackIsoMapToken_(
          consumes(iConfig.getParameter<edm::InputTag>("TrackIsoMap"))),
      pfhtToken_(consumes(iConfig.getParameter<edm::InputTag>("PFHT"))),
      pnetToken_(consumes(iConfig.getParameter<edm::InputTag>("PNetBscore"))),
      muonPtCut_(iConfig.getParameter<double>("muonPtCut")),
      muonEtaCut_(iConfig.getParameter<double>("muonEtaCut")),
      buffer_{},
      debug_(iConfig.getParameter<bool>("debug")) {
  produces<float>("score");

  /* Load model */
  const edm::FileInPath modelPath(
      iConfig.getParameter<std::string>("modelPath"));

  if (debug_) {
    edm::LogInfo("HLTTopoMuonHTPNetBXGBProducer")
        << "Loading XGBoost model from " << modelPath.fullPath();
  }

  XGBoosterCreate(nullptr, 0, &booster_);
  XGBoosterLoadModel(booster_, modelPath.fullPath().c_str());

  /* Allocate DMatrix once; buffer_ address is stable for the lifetime of
     the producer since it is a value member, not a pointer.
     NOTE: XGBoost copies the data at creation time, so dmat_ is only used
     as a pre-allocated handle — we recreate it from buffer_ each event via
     XGDMatrixCreateFromMat, which reuses this same allocation. */
  XGDMatrixCreateFromMat(buffer_.data(), 1, kNFeatures, -999.f, &dmat_);

  xgbConfig_ =
      "{\"training\": false, \"type\": 0, "
      "\"iteration_begin\": 0, \"iteration_end\": 0, "
      "\"strict_shape\": false}";
}

/* ------------------------------------------------------------ */

HLTTopoMuonHTPNetBXGBProducer::~HLTTopoMuonHTPNetBXGBProducer() {
  if (dmat_) XGDMatrixFree(dmat_);
  if (booster_) XGBoosterFree(booster_);
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHTPNetBXGBProducer::produce(edm::Event& iEvent,
                                            edm::EventSetup const&) {
  float outScore = -999.f;

  if (debug_) {
    std::cout
        << "HLTTopoMuonHTPNetBXGBProducer: Starting produce method for event "
        << iEvent.id() << std::endl;
  }

  /* ---------------- PFHT ---------------- */

  float pfht = 0.f;

  if (auto h = iEvent.getHandle(pfhtToken_); h.isValid()) {
    if (!h->empty()) pfht = h->front().sumEt();
  } else {
    edm::LogWarning("HLTTopoMuonHTPNetBXGBProducer")
        << "Missing PFHT collection";
  }

  /* ---------------- PNetB ---------------- */

  float maxPNetB = -1.f;

  if (auto h = iEvent.getHandle(pnetToken_); h.isValid()) {
    for (auto const& tag : *h) maxPNetB = std::max(maxPNetB, tag.second);
  } else {
    edm::LogWarning("HLTTopoMuonHTPNetBXGBProducer") << "Missing PNetB JetTags";
  }

  /* ---------------- Muons ---------------- */

  const auto muonsH = iEvent.getHandle(chargedCandidatesToken_);

  if (!muonsH.isValid()) {
    edm::LogError("HLTTopoMuonHTPNetBXGBProducer")
        << "Missing ChargedCandidates";
    iEvent.put(std::make_unique<float>(outScore), "score");
    return;
  }

  int bestIdx = -1;
  float bestPt = -1.f;

  for (size_t i = 0; i < muonsH->size(); ++i) {
    const auto& mu = (*muonsH)[i];
    if (mu.pt() < muonPtCut_) continue;
    if (std::abs(mu.eta()) > muonEtaCut_) continue;
    if (mu.pt() > bestPt) {
      bestPt = mu.pt();
      bestIdx = static_cast<int>(i);
    }
  }

  if (bestIdx < 0) {
    iEvent.put(std::make_unique<float>(outScore), "score");
    return;
  }

  const auto muRef = edm::getRef(muonsH, bestIdx);

  /* ---------------- Isolations ---------------- */

  const auto ecalH = iEvent.getHandle(ecalIsoMapToken_);
  const auto hcalH = iEvent.getHandle(hcalIsoMapToken_);
  const auto trkH = iEvent.getHandle(trackIsoMapToken_);

  const float ecalIso = ecalH.isValid() ? (*ecalH)[muRef] : 10.f;
  const float hcalIso = hcalH.isValid() ? (*hcalH)[muRef] : 10.f;
  const float trkIso = trkH.isValid() ? (*trkH)[muRef] : 10.f;

  /* ---------------- Fill buffer & recreate DMatrix ---------------- */

  buffer_[0] = pfht;
  buffer_[1] = maxPNetB;
  buffer_[2] = bestPt;
  buffer_[3] = 10.f - trkIso / bestPt;
  buffer_[4] = 10.f - ecalIso / bestPt;
  buffer_[5] = 10.f - hcalIso / bestPt;

  // Free the old DMatrix and recreate from the updated buffer_.
  // This is necessary because XGBoost copies data at DMatrix creation time
  // and provides no API to update values in place.
  XGDMatrixFree(dmat_);
  XGDMatrixCreateFromMat(buffer_.data(), 1, kNFeatures, -999.f, &dmat_);

  /* ---------------- XGBoost inference ---------------- */

  uint64_t const* outShape = nullptr;
  uint64_t outDim = 0;
  const float* outResult = nullptr;

  XGBoosterPredictFromDMatrix(booster_, dmat_, xgbConfig_.c_str(), &outShape,
                              &outDim, &outResult);

  if (outResult != nullptr) outScore = outResult[0];

  /* ---------------- Debug ---------------- */

  if (debug_) {
    std::ostringstream ss;
    ss << "Features: ";
    for (float f : buffer_) ss << f << " ";
    ss << " --> score=" << outScore;
    std::cout << ss.str() << std::endl;
  }

  iEvent.put(std::make_unique<float>(outScore), "score");
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHTPNetBXGBProducer::fillDescriptions(
    edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("PFHT", edm::InputTag("hltPFHTJet30"));
  desc.add<edm::InputTag>(
      "PNetBscore",
      edm::InputTag("hltParticleNetDiscriminatorsJetTags", "BvsAll"));
  desc.add<edm::InputTag>("ChargedCandidates",
                          edm::InputTag("hltL3MuonCandidates"));
  desc.add<edm::InputTag>("EcalPFClusterIsoMap",
                          edm::InputTag("hltMuonEcalPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("HcalPFClusterIsoMap",
                          edm::InputTag("hltMuonHcalPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("TrackIsoMap",
                          edm::InputTag("hltMuonTkRelIsolationCut0p09Map",
                                        "combinedRelativeIsoDeposits"));

  desc.add<std::string>(
      "modelPath",
      "L1Trigger/TopoML/data/"
      "HLT_xgb_model_HH2b2W1L_1mu_HLTHT_Mu_pt-iso_PNetB.json");

  desc.add<double>("muonPtCut", 4.0);
  desc.add<double>("muonEtaCut", 2.4);
  desc.add<bool>("debug", false);

  descriptions.add("HLTTopoMuonHTPNetBXGBProducer", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(HLTTopoMuonHTPNetBXGBProducer);