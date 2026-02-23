/** \class HLTTopoMuonHtPNetBXGBProducer
 *
 *  This class is an EDProducer that produces a single float value corresponding to the output score of an XGBoost model
 *  of a "topological trigger" (TOPO) for events with at least one muon + HT and b-tag. 
 *  The model takes as input the PFHT, 
 *  the maximum PNetB score among jets in the event, 
 *  and the pt and isolation variables of up to N muons (configurable).
 *
 *  \author Artur Lobanov – University of Hamburg
 */

#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/getRef.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
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
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "PhysicsTools/XGBoost/interface/XGBooster.h"

class HLTTopoMuonHtPNetBXGBProducer : public edm::global::EDProducer<> {
public:
  using RecoChargedCandMap =
      edm::AssociationMap<edm::OneToValue<std::vector<reco::RecoChargedCandidate>, float, unsigned int>>;

  // 2 global features (PFHT, MaxPNetB) + 4 features per muon
  static constexpr unsigned int kGlobalFeatures = 2;
  static constexpr unsigned int kFeaturesPerMuon = 4;

  explicit HLTTopoMuonHtPNetBXGBProducer(edm::ParameterSet const&);
  ~HLTTopoMuonHtPNetBXGBProducer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override;

  /* Tokens */
  const edm::EDGetTokenT<reco::RecoChargedCandidateCollection> chargedCandidatesToken_;
  const edm::EDGetTokenT<RecoChargedCandMap> ecalIsoMapToken_;
  const edm::EDGetTokenT<RecoChargedCandMap> hcalIsoMapToken_;
  const edm::EDGetTokenT<edm::ValueMap<double>> trackIsoMapToken_;
  const edm::EDGetTokenT<reco::METCollection> pfhtToken_;
  const edm::EDGetTokenT<reco::JetTagCollection> pnetToken_;

  /* Cuts */
  const double muonPtCut_;
  const double muonEtaCut_;

  /* Config */
  const unsigned int nMuons_;    // number of muons used as input features
  const unsigned int nFeatures;  // kGlobalFeatures + kFeaturesPerMuon * nMuons_
  const bool muonSortByTkIso_;   // if true: ascending tkiso; if false: descending pt

  /* XGBoost */
  std::unique_ptr<pat::XGBooster> booster_;
  edm::EDPutTokenT<float> scoreToken_;

  const bool debug_;
};

using namespace edm;

HLTTopoMuonHtPNetBXGBProducer::HLTTopoMuonHtPNetBXGBProducer(edm::ParameterSet const& iConfig)

    : chargedCandidatesToken_(consumes(iConfig.getParameter<edm::InputTag>("ChargedCandidates"))),
      ecalIsoMapToken_(consumes(iConfig.getParameter<edm::InputTag>("EcalPFClusterIsoMap"))),
      hcalIsoMapToken_(consumes(iConfig.getParameter<edm::InputTag>("HcalPFClusterIsoMap"))),
      trackIsoMapToken_(consumes(iConfig.getParameter<edm::InputTag>("TrackIsoMap"))),
      pfhtToken_(consumes(iConfig.getParameter<edm::InputTag>("PFHT"))),
      pnetToken_(consumes(iConfig.getParameter<edm::InputTag>("PNetBscore"))),
      muonPtCut_(iConfig.getParameter<double>("muonPtCut")),
      muonEtaCut_(iConfig.getParameter<double>("muonEtaCut")),
      nMuons_(iConfig.getParameter<unsigned int>("nMuons")),
      nFeatures(kGlobalFeatures + kFeaturesPerMuon * nMuons_),
      muonSortByTkIso_(iConfig.getParameter<bool>("muonSortByTkIso")),
      debug_(iConfig.getParameter<bool>("debug")) {
  scoreToken_ = produces<float>("score");

  /* Load model */
  const edm::FileInPath modelPath(iConfig.getParameter<std::string>("modelPath"));

  if (debug_) {
    std::cout << "Loading XGBoost model from " << modelPath.fullPath() << std::endl
              << " nMuons=" << nMuons_ << " nFeatures=" << nFeatures << " muonSortByTkIso=" << muonSortByTkIso_
              << std::endl;
  }

  booster_ = std::make_unique<pat::XGBooster>(modelPath.fullPath());

  booster_->addFeature("pfht");
  booster_->addFeature("maxPNetB");
  // add muon featured in the order defined in the buffer: pt, tkIso, ecalIso, hcalIso for each muon
  for (unsigned int imu = 0; imu < nMuons_; ++imu) {
    booster_->addFeature("muon" + std::to_string(imu) + "_pt");
    booster_->addFeature("muon" + std::to_string(imu) + "_tkIso");
    booster_->addFeature("muon" + std::to_string(imu) + "_ecalIso");
    booster_->addFeature("muon" + std::to_string(imu) + "_hcalIso");
  }
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHtPNetBXGBProducer::produce(edm::StreamID, edm::Event& iEvent, edm::EventSetup const& setup) const {
  float outScore = -1.f;
  std::vector<float> features(
      nFeatures, 0.f);  // buffer for features to be fed to XGBoost; zero-padding for missing/empty features

  /* ---------------- Muons: collect passing cuts ---------------- */

  const auto& muonsH = iEvent.getHandle(chargedCandidatesToken_);

  if (!muonsH.isValid()) {
    LogError("HLTTopoMuonHtPNetBXGBProducer") << "Missing ChargedCandidates";
    iEvent.emplace(scoreToken_, outScore);
    return;
  }

  // Fetch track iso map once — needed for sorting and feature filling
  const auto& trkH = iEvent.getHandle(trackIsoMapToken_);

  std::vector<size_t> muonIndices;
  muonIndices.reserve(muonsH->size());

  for (size_t i = 0; i < muonsH->size(); ++i) {
    const auto& mu = (*muonsH)[i];
    if (mu.pt() < muonPtCut_)
      continue;
    if (std::abs(mu.eta()) > muonEtaCut_)
      continue;
    muonIndices.push_back(i);
  }

  if (muonIndices.empty()) {
    iEvent.emplace(scoreToken_, outScore);
    return;
  }

  /* ---------------- Sort ---------------- */

  if (muonSortByTkIso_) {
    // Ascending track iso — tightest isolation first.
    // Muons with missing track iso map are pushed to the back.
    std::sort(muonIndices.begin(), muonIndices.end(), [&](size_t a, size_t b) {
      const float isoA =
          trkH.isValid() ? static_cast<float>((*trkH)[edm::getRef(muonsH, a)]) : std::numeric_limits<float>::max();
      const float isoB =
          trkH.isValid() ? static_cast<float>((*trkH)[edm::getRef(muonsH, b)]) : std::numeric_limits<float>::max();
      // get pt of muons too to make relative isolation sorting
      const float ptA = (*muonsH)[a].pt();
      const float ptB = (*muonsH)[b].pt();

      // if iso is 0 for both then sort by descending pt to have a deterministic order, otherwise sort by ascending relative isolation
      if (isoA == 0.f && isoB == 0.f)
        return ptA > ptB;
      return (isoA / ptA) < (isoB / ptB);
    });
  } else {
    // Descending pt
    std::sort(muonIndices.begin(), muonIndices.end(), [&](size_t a, size_t b) {
      return (*muonsH)[a].pt() > (*muonsH)[b].pt();
    });
  }

  /* ---------------- Isolations (ECAL/HCAL) ---------------- */

  const auto& ecalH = iEvent.getHandle(ecalIsoMapToken_);
  const auto& hcalH = iEvent.getHandle(hcalIsoMapToken_);

  /* ---------------- PFHT ---------------- */

  float pfht = 0.f;

  if (const auto& h = iEvent.getHandle(pfhtToken_); h.isValid()) {
    if (!h->empty())
      pfht = h->front().sumEt();
  } else {
    LogWarning("HLTTopoMuonHtPNetBXGBProducer") << "Missing PFHT collection";
  }

  /* ---------------- PNetB ---------------- */

  float maxPNetB = -1.f;

  if (const auto& h = iEvent.getHandle(pnetToken_); h.isValid()) {
    for (auto const& tag : *h)
      maxPNetB = std::max(maxPNetB, tag.second);
  } else {
    LogWarning("HLTTopoMuonHtPNetBXGBProducer") << "Missing PNetB JetTags";
  }

  /* ---------------- Fill buffer ---------------- */

  features[0] = pfht;
  features[1] = maxPNetB;

  const unsigned int nFill = std::min(muonIndices.size(), static_cast<size_t>(nMuons_));

  for (unsigned int m = 0; m < nFill; ++m) {
    const size_t idx = muonIndices[m];
    const auto& mu = (*muonsH)[idx];
    const float pt = mu.pt();
    const auto muRef = edm::getRef(muonsH, idx);

    const float ecalIso = ecalH.isValid() ? (*ecalH)[muRef] : 10.f;
    const float hcalIso = hcalH.isValid() ? (*hcalH)[muRef] : 10.f;
    const float trkIso = trkH.isValid() ? static_cast<float>((*trkH)[muRef]) : 10.f;

    const unsigned int base = kGlobalFeatures + m * kFeaturesPerMuon;
    features[base + 0] = pt;
    features[base + 1] = trkIso;
    features[base + 2] = ecalIso;
    features[base + 3] = hcalIso;
  }

  /* ---------------- XGBoost inference ---------------- */

  outScore = booster_->predict(features, 0);  // best_ntree_limit_ can be added as a second argument if needed

  /* ---------------- Debug ---------------- */

  if (debug_) {
    std::ostringstream ss;
    ss << "HLTTopoMuonHtPNetBXGBProducer: nMuons(found)=" << muonIndices.size() << std::endl;
    ss << " Features: ";
    for (float f : features)
      ss << f << " ";
    ss << " --> score=" << outScore;
    std::cout << ss.str() << std::endl;
  }

  iEvent.emplace(scoreToken_, outScore);
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHtPNetBXGBProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("PFHT", edm::InputTag("hltPFHTJet30"));
  desc.add<edm::InputTag>("PNetBscore", edm::InputTag("hltParticleNetDiscriminatorsJetTags", "BvsAll"));
  desc.add<edm::InputTag>("ChargedCandidates", edm::InputTag("hltL3MuonCandidates"));
  desc.add<edm::InputTag>("EcalPFClusterIsoMap", edm::InputTag("hltMuonEcalMFPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("HcalPFClusterIsoMap", edm::InputTag("hltMuonHcalRegPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("TrackIsoMap",
                          edm::InputTag("hltMuonTkRelIsolationCut0p3Map", "combinedRelativeIsoDeposits"));
  desc.add<std::string>("modelPath",
                        "HLTrigger/HLTfilters/data/HLT_xgb_model_HH2b2W1L_1mu_HLTHT_sorttkisoMupt-absiso_PNetB.json");

  desc.add<unsigned int>("nMuons", 1);
  desc.add<double>("muonPtCut", 10.0);
  desc.add<double>("muonEtaCut", 2.4);
  desc.add<bool>("muonSortByTkIso", true)->setComment("false: sort by descending pt, true:  sort by ascending tkiso");
  desc.add<bool>("debug", false);

  descriptions.addWithDefaultLabel(desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(HLTTopoMuonHtPNetBXGBProducer);
