// HEADER

#ifndef HLTrigger_Muon_HLTTopoMuonHTPNetBXGBoostProducer_h
#define HLTrigger_Muon_HLTTopoMuonHTPNetBXGBoostProducer_h

#include <memory>
#include <vector>
#include <string>

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"

#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToValue.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/METReco/interface/MET.h"
#include "DataFormats/BTauReco/interface/JetTag.h"

#include "xgboost/c_api.h"


class HLTTopoMuonHTPNetBXGBoostProducer
    : public edm::global::EDProducer<> {

public:

  using RecoChargedCandMap =
      edm::AssociationMap<
        edm::OneToValue<
          std::vector<reco::RecoChargedCandidate>,
          float,
          unsigned int>>;

  explicit HLTTopoMuonHTPNetBXGBoostProducer(edm::ParameterSet const&);
  ~HLTTopoMuonHTPNetBXGBoostProducer() override;

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:

  void produce(edm::StreamID,
               edm::Event&,
               edm::EventSetup const&) const override;

  /* Tokens */

  edm::EDGetTokenT<reco::RecoChargedCandidateCollection>
      chargedCandidatesToken_;

  edm::EDGetTokenT<RecoChargedCandMap> ecalIsoMapToken_;
  edm::EDGetTokenT<RecoChargedCandMap> hcalIsoMapToken_;
  edm::EDGetTokenT<edm::ValueMap<double>> trackIsoMapToken_;

  edm::EDGetTokenT<reco::METCollection> pfhtToken_;
  edm::EDGetTokenT<reco::JetTagCollection> pnetToken_;

  /* Cuts */

  double muonPtCut_;
  double muonEtaCut_;

  /* XGBoost */

  BoosterHandle booster_;
  int bestNTrees_;
  std::string predictConfig_;

  bool debug_;
};

#endif


// MAIN SOURCE

#include "HLTTopoMuonHTPNetBXGBoostProducer.h"

#include <cmath>
#include <sstream>

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/Common/interface/getRef.h"


HLTTopoMuonHTPNetBXGBoostProducer::
HLTTopoMuonHTPNetBXGBoostProducer(edm::ParameterSet const& iConfig)

    : chargedCandidatesToken_(
        consumes(iConfig.getParameter<edm::InputTag>("ChargedCandidates"))),

      ecalIsoMapToken_(
        consumes(iConfig.getParameter<edm::InputTag>("EcalPFClusterIsoMap"))),

      hcalIsoMapToken_(
        consumes(iConfig.getParameter<edm::InputTag>("HcalPFClusterIsoMap"))),

      trackIsoMapToken_(
        consumes(iConfig.getParameter<edm::InputTag>("TrackIsoMap"))),

      pfhtToken_(
        consumes(iConfig.getParameter<edm::InputTag>("PFHT"))),

      pnetToken_(
        consumes(iConfig.getParameter<edm::InputTag>("PNetBscore"))),

      muonPtCut_(iConfig.getParameter<double>("muonPtCut")),
      muonEtaCut_(iConfig.getParameter<double>("muonEtaCut")),

      bestNTrees_(iConfig.getParameter<int>("bestNTrees")),
      debug_(iConfig.getParameter<bool>("debug")) {

  produces<float>("score");


  /* ---------------- Load Model ---------------- */

  edm::FileInPath modelPath(
      iConfig.getParameter<std::string>("modelPath"));

  if (debug_) {
    edm::LogInfo("HLTTopoMuonHTPNetBXGBoostProducer")
        << "Loading XGBoost model from "
        << modelPath.fullPath();
  }

  /* Create booster */

  XGBoosterCreate(nullptr, 0, &booster_);
  XGBoosterLoadModel(booster_, modelPath.fullPath().c_str());

  /* Prediction config */

  std::ostringstream ss;

  ss << "{"
     << "\"type\":0,"
     << "\"iteration_begin\":0,"
     << "\"iteration_end\":" << bestNTrees_
     << "}";

  predictConfig_ = ss.str();
}


/* ------------------------------------------------------------ */


HLTTopoMuonHTPNetBXGBoostProducer::~HLTTopoMuonHTPNetBXGBoostProducer() {

  XGBoosterFree(booster_);
}


/* ------------------------------------------------------------ */


void HLTTopoMuonHTPNetBXGBoostProducer::produce(
    edm::StreamID,
    edm::Event& iEvent,
    edm::EventSetup const&) const {

  float outScore = -999.f;


  /* ---------------- PFHT ---------------- */

  float pfht = 0.f;

  if (auto h = iEvent.getHandle(pfhtToken_); h.isValid()) {
    if (!h->empty())
      pfht = h->front().sumEt();
  }


  /* ---------------- PNetB ---------------- */

  float maxPNetB = -1.f;

  if (auto h = iEvent.getHandle(pnetToken_); h.isValid()) {

    for (auto const& tag : *h)
      maxPNetB = std::max(maxPNetB, tag.second);
  }


  /* ---------------- Muons ---------------- */

  const auto muonsH = iEvent.getHandle(chargedCandidatesToken_);

  if (!muonsH.isValid()) {
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
      bestIdx = i;
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
  const auto trkH  = iEvent.getHandle(trackIsoMapToken_);


  const float ecalIso =
      ecalH.isValid() ? (*ecalH)[muRef] : 10.f;

  const float hcalIso =
      hcalH.isValid() ? (*hcalH)[muRef] : 10.f;

  const float trkIso =
      trkH.isValid() ? (*trkH)[muRef] : 10.f;


  /* ---------------- Features ---------------- */

  constexpr int nFeat = 6;
  float vars[nFeat];

  vars[0] = pfht;
  vars[1] = maxPNetB;
  vars[2] = bestPt;

  vars[3] = 10.f - trkIso / bestPt;
  vars[4] = 10.f - ecalIso / bestPt;
  vars[5] = 10.f - hcalIso / bestPt;


  /* ---------------- XGBoost ---------------- */

  DMatrixHandle dmat;

  XGDMatrixCreateFromMat(
      vars,
      1,
      nFeat,
      -999.9f,
      &dmat);


  uint64_t const* shape;
  uint64_t ndim;
  const float* result = nullptr;


  XGBoosterPredictFromDMatrix(
      booster_,
      dmat,
      predictConfig_.c_str(),
      &shape,
      &ndim,
      &result);


  if (ndim > 0 && result)
    outScore = result[0];


  XGDMatrixFree(dmat);


  /* ---------------- Debug ---------------- */

  if (debug_) {

    std::ostringstream ss;

    ss << "Features: ";

    for (int i = 0; i < nFeat; ++i)
      ss << vars[i] << " ";

    ss << " -> score=" << outScore;

    edm::LogInfo("HLTTopoMuonHTPNetBXGBoostProducer") << ss.str();
  }


  iEvent.put(std::make_unique<float>(outScore), "score");
}


/* ------------------------------------------------------------ */


void HLTTopoMuonHTPNetBXGBoostProducer::fillDescriptions(
    edm::ConfigurationDescriptions& descriptions) {

  edm::ParameterSetDescription desc;


  desc.add<edm::InputTag>(
      "PFHT",
      edm::InputTag("hltPFHTJet30"));

  desc.add<edm::InputTag>(
      "PNetBscore",
      edm::InputTag("hltParticleNetDiscriminatorsJetTags", "BvsAll"));

  desc.add<edm::InputTag>(
      "ChargedCandidates",
      edm::InputTag("hltL3MuonCandidates"));

  desc.add<edm::InputTag>(
      "EcalPFClusterIsoMap",
      edm::InputTag("hltMuonEcalPFClusterIsoForMuons"));

  desc.add<edm::InputTag>(
      "HcalPFClusterIsoMap",
      edm::InputTag("hltMuonHcalPFClusterIsoForMuons"));

  desc.add<edm::InputTag>(
      "TrackIsoMap",
      edm::InputTag("hltMuonTkRelIsolationCut0p09Map",
                    "combinedRelativeIsoDeposits"));


  desc.add<std::string>("modelPath");

  desc.add<int>("bestNTrees", -1);

  desc.add<double>("muonPtCut", 4.0);
  desc.add<double>("muonEtaCut", 2.4);

  desc.add<bool>("debug", false);


  descriptions.add(
      "HLTTopoMuonHTPNetBXGBoostProducer",
      desc);
}


#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(HLTTopoMuonHTPNetBXGBoostProducer);
