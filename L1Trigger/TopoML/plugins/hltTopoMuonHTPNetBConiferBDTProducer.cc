/*

This is the producer module for the HLT version of the
TopoMuonHTPNetBConiferBDT, which uses a conifer BDT to combine the following
inputs:

    - PF HT
    - Max PNetB score among jets
    - Leading muon pt
    - Leading muon track isolation
    - Leading muon ecal isolation
    - Leading muon hcal isolation

"feature_names":["PFHT","Max PNetB","hlt 1. Mu pt","hlt 1. Mu tkiso","hlt 1. Mu
ecaliso","hlt 1. Mu hcaliso"]
*/

/*

Muon iso  from the below collections:

  // Inputs for leading muon + isolations
  desc.add<edm::InputTag>("ChargedCandidates",
edm::InputTag("hltL3MuonCandidates"));
  desc.add<edm::InputTag>("EcalPFClusterIsoMap",
edm::InputTag("hltMuonEcalPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("HcalPFClusterIsoMap",
edm::InputTag("hltMuonHcalPFClusterIsoForMuons"));
  desc.add<edm::InputTag>("TrackIsoMap",
                          edm::InputTag("hltMuonTkRelIsolationCut0p09Map",
"combinedRelativeIsoDeposits"));

  // Model JSON (must be in CMSSW search path, e.g. in your package under data/)
  desc.add<std::string>("modelPath",
"L1Trigger/TopoML/data/Jan26_HLT_conif_model_HH2b2W1L_1mu_L1MuTOPOMuHT_Mu_pt-iso.json");
*/

/*
PF HT from this producer:

hltPFHTJet30 = cms.EDProducer("HLTHtMhtProducer",
    excludePFMuons = cms.bool(False),
    jetsLabel = cms.InputTag("hltAK4PFJetsCorrected"),
    maxEtaJetHt = cms.double(2.5),
    maxEtaJetMht = cms.double(999.0),
    minNJetHt = cms.int32(0),
    minNJetMht = cms.int32(0),
    minPtJetHt = cms.double(30.0),
    minPtJetMht = cms.double(0.0),
    pfCandidatesLabel = cms.InputTag("hltParticleFlow"),
    usePt = cms.bool(True)
)
*/

/*
PNet B tag score from this producer:

hltParticleNetDiscriminatorsJetTags =
cms.EDProducer("BTagProbabilityToDiscriminator", discriminators = cms.VPSet(
        cms.PSet(
            denominator = cms.VInputTag("hltParticleNetONNXJetTags:probb",
"hltParticleNetONNXJetTags:probc", "hltParticleNetONNXJetTags:probuds",
"hltParticleNetONNXJetTags:probg"), name = cms.string('BvsAll'), numerator =
cms.VInputTag("hltParticleNetONNXJetTags:probb")
        ),
        ...

    )
)

the corresponding filter is

hltBTagPFPNet0p53Single = cms.EDFilter("HLTPFJetTag",
    JetTags = cms.InputTag("hltParticleNetDiscriminatorsJetTags","BvsAll"),
    Jets = cms.InputTag("hltPFJetForBtag"),
    MatchJetsByDeltaR = cms.bool(False),
    MaxJetDeltaR = cms.double(0.1),
    MaxTag = cms.double(999999.0),
    MinJets = cms.int32(1),
    MinTag = cms.double(0.525),
    TriggerType = cms.int32(86),
    saveTags = cms.bool(True)
)
*/

// HEADER

#ifndef HLTrigger_Muon_HLTTopoMuonHTPNetBConiferBDTProducer_h
#define HLTrigger_Muon_HLTTopoMuonHTPNetBConiferBDTProducer_h

#include <memory>
#include <vector>

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
#include "conifer.h"

class HLTTopoMuonHTPNetBConiferBDTProducer : public edm::global::EDProducer<> {
 public:
  using RecoChargedCandMap = edm::AssociationMap<edm::OneToValue<
      std::vector<reco::RecoChargedCandidate>, float, unsigned int>>;

  using BDT_t = conifer::BDT<float, float, true>;

  explicit HLTTopoMuonHTPNetBConiferBDTProducer(edm::ParameterSet const&);
  ~HLTTopoMuonHTPNetBConiferBDTProducer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions&);

 private:
  void produce(edm::StreamID, edm::Event&,
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

  /* BDT */

  std::unique_ptr<const BDT_t> bdt_;

  bool debug_;
};

#endif

// MAIN SOURCE

#include <cmath>
#include <iostream>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/getRef.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
// #include "HLTTopoMuonHTPNetBConiferBDTProducer.h"

HLTTopoMuonHTPNetBConiferBDTProducer::HLTTopoMuonHTPNetBConiferBDTProducer(
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

      debug_(iConfig.getParameter<bool>("debug")) {
  produces<float>("score");

  /* Load model */

  const edm::FileInPath modelPath(
      iConfig.getParameter<std::string>("modelPath"));

  if (debug_) {
    edm::LogInfo("HLTTopoMuonHTPNetBConiferBDTProducer")
        << "Loading model from " << modelPath.fullPath();
  }

  bdt_ = std::make_unique<BDT_t>(modelPath.fullPath());
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHTPNetBConiferBDTProducer::produce(
    edm::StreamID, edm::Event& iEvent, edm::EventSetup const&) const {
  float outScore = -999.f;

  /* ---------------- PFHT ---------------- */

  float pfht = 0.f;

  if (auto h = iEvent.getHandle(pfhtToken_); h.isValid()) {
    if (!h->empty()) {
      pfht = h->front().sumEt();
    }

  } else {
    edm::LogWarning("HLTTopoMuonHTPNetBConiferBDTProducer")
        << "Missing PFHT collection";
  }

  /* ---------------- PNetB ---------------- */

  float maxPNetB = -1.f;

  if (auto h = iEvent.getHandle(pnetToken_); h.isValid()) {
    for (auto const& tag : *h) {
      maxPNetB = std::max(maxPNetB, tag.second);
    }

  } else {
    edm::LogWarning("HLTTopoMuonHTPNetBConiferBDTProducer")
        << "Missing PNetB JetTags";
  }

  /* ---------------- Muons ---------------- */

  const auto muonsH = iEvent.getHandle(chargedCandidatesToken_);

  if (!muonsH.isValid()) {
    edm::LogError("HLTTopoMuonHTPNetBConiferBDTProducer")
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
  const auto trkH = iEvent.getHandle(trackIsoMapToken_);

  const float ecalIso = ecalH.isValid() ? (*ecalH)[muRef] : 10.f;

  const float hcalIso = hcalH.isValid() ? (*hcalH)[muRef] : 10.f;

  const float trkIso = trkH.isValid() ? (*trkH)[muRef] : 10.f;

  /* ---------------- Features ---------------- */

  std::vector<float> features;
  features.reserve(6);

  // Order matches training

  features.push_back(pfht);
  features.push_back(maxPNetB);
  features.push_back(bestPt);

  features.push_back(10.f - trkIso / bestPt);
  features.push_back(10.f - ecalIso / bestPt);
  features.push_back(10.f - hcalIso / bestPt);

  /* ---------------- BDT ---------------- */

  if (bdt_) {
    const auto out = bdt_->decision_function(features);

    if (!out.empty()) outScore = out[0];
  }

  /* ---------------- Debug ---------------- */

  if (debug_) {
    std::ostringstream ss;

    ss << "Features: ";

    for (float f : features) ss << f << " ";

    ss << " --> score=" << outScore;

    // edm::LogInfo("HLTTopoMuonHTPNetBConiferBDTProducer") << ss.str();
    std::cout << ss.str() << std::endl;
  }

  iEvent.put(std::make_unique<float>(outScore), "score");
}

/* ------------------------------------------------------------ */

void HLTTopoMuonHTPNetBConiferBDTProducer::fillDescriptions(
    edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  /* Inputs */

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

  /* Model */

  desc.add<std::string>(
      "modelPath",
      "L1Trigger/TopoML/data/"
      "HLT_xgb_model_HH2b2W1L_1mu_HLTHT_Mu_pt-iso_PNetB.json");

  /* Cuts */

  desc.add<double>("muonPtCut", 4.0);
  desc.add<double>("muonEtaCut", 2.4);

  desc.add<bool>("debug", false);

  descriptions.add("HLTTopoMuonHTPNetBConiferBDTProducer", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(HLTTopoMuonHTPNetBConiferBDTProducer);
