#ifndef HLTrigger_Muon_HLTTopoMuonHTConiferBDTProducer_h
#define HLTrigger_Muon_HLTTopoMuonHTConiferBDTProducer_h

#include <memory>

#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToValue.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidateFwd.h"
#include "DataFormats/Scouting/interface/ScoutingMuon.h"
#include "DataFormats/TrackReco/interface/HitPattern.h"
#include "DataFormats/TrackReco/interface/Track.h"
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

class HLTTopoMuonHTConiferBDTProducer : public edm::global::EDProducer<> {
 public:
  using RecoChargedCandMap = edm::AssociationMap<edm::OneToValue<
      std::vector<reco::RecoChargedCandidate>, float, unsigned int>>;

  explicit HLTTopoMuonHTConiferBDTProducer(edm::ParameterSet const&);
  ~HLTTopoMuonHTConiferBDTProducer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

 private:
  void produce(edm::StreamID, edm::Event&,
               edm::EventSetup const&) const override;

  edm::EDGetTokenT<float> l1tTopoScoreToken_;
  edm::EDGetTokenT<reco::RecoChargedCandidateCollection>
      chargedCandidatesToken_;
  edm::EDGetTokenT<RecoChargedCandMap> ecalIsoMapToken_;
  edm::EDGetTokenT<RecoChargedCandMap> hcalIsoMapToken_;
  edm::EDGetTokenT<edm::ValueMap<double>> trackIsoMapToken_;

  double muonPtCut_;
  double muonEtaCut_;

  /// BDT model
  using BDT_t = conifer::BDT<float, float, true>;
  std::unique_ptr<const BDT_t> bdt_;

  bool debug_;
};

#endif

// cpp /src below
// #include "L1Trigger/TopoML/plugins/HLTTopoMuonHTConiferBDTProducer.h"

#include <cmath>
#include <memory>
#include <utility>

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/getRef.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

HLTTopoMuonHTConiferBDTProducer::HLTTopoMuonHTConiferBDTProducer(
    edm::ParameterSet const& iConfig)
    : l1tTopoScoreToken_(
          consumes<float>(iConfig.getParameter<edm::InputTag>("l1tTopoScore"))),
      chargedCandidatesToken_(consumes<reco::RecoChargedCandidateCollection>(
          iConfig.getParameter<edm::InputTag>("ChargedCandidates"))),
      ecalIsoMapToken_(consumes<RecoChargedCandMap>(
          iConfig.getParameter<edm::InputTag>("EcalPFClusterIsoMap"))),
      hcalIsoMapToken_(consumes<RecoChargedCandMap>(
          iConfig.getParameter<edm::InputTag>("HcalPFClusterIsoMap"))),
      trackIsoMapToken_(consumes<edm::ValueMap<double>>(
          iConfig.getParameter<edm::InputTag>("TrackIsoMap"))),
      muonPtCut_(iConfig.getParameter<double>("muonPtCut")),
      muonEtaCut_(iConfig.getParameter<double>("muonEtaCut")),
      debug_(iConfig.getParameter<bool>("debug")) {
  produces<float>("score");

  // Load conifer model from JSON located via FileInPath
  const edm::FileInPath modelPath(
      iConfig.getParameter<std::string>("modelPath"));
  // print model path
  if (debug_)
    std::cout << "HLTTopoMuonHTConiferBDTProducer: loading model from "
              << modelPath.fullPath() << std::endl;

  // Load BDT model
  try {
    bdt_ = std::make_unique<BDT_t>(modelPath.fullPath());
  } catch (const std::exception& e) {
    throw cms::Exception("HLTTopoMuonHTConiferBDTProducer")
        << "Error loading BDT model from " << modelPath.fullPath() << ": "
        << e.what();
  }
}

void HLTTopoMuonHTConiferBDTProducer::produce(edm::StreamID, edm::Event& iEvent,
                                              edm::EventSetup const&) const {
  // Always put a product, even if inputs missing
  float outScore = -999.f;

  if (!bdt_) {
    edm::LogError("HLTTopoMuonHTConiferBDTProducer")
        << "Conifer BDT pointer is null.";
    iEvent.put(std::make_unique<float>(outScore), "score");
    return;
  }

  // default value for external L1Topo score (feature[0])
  float extScore = -999.f;

  // Get external score
  {
    const auto extH = iEvent.getHandle(l1tTopoScoreToken_);
    if (extH.isValid()) {
      extScore = *extH;
    } else {
      edm::LogError("HLTTopoMuonHTConiferBDTProducer")
          << "Missing external l1tTopoScore product.";
      iEvent.put(std::make_unique<float>(outScore), "score");
    }
  }

  // Handles for muon collection & iso maps
  const auto chargedCandidatesH = iEvent.getHandle(chargedCandidatesToken_);
  const auto ecalIsoMapH = iEvent.getHandle(ecalIsoMapToken_);
  const auto hcalIsoMapH = iEvent.getHandle(hcalIsoMapToken_);
  const auto trackIsoMapH = iEvent.getHandle(trackIsoMapToken_);

  if (!chargedCandidatesH.isValid()) {
    edm::LogError("HLTTopoMuonHTConiferBDTProducer")
        << "Missing ChargedCandidates input.";
    iEvent.put(std::make_unique<float>(outScore), "score");
    return;
  }

  // Find leading muon-candidate passing cuts
  int bestIdx = -1;
  float bestPt = -1.f;

  for (int i = 0, n = static_cast<int>(chargedCandidatesH->size()); i < n;
       ++i) {
    const auto& mu = (*chargedCandidatesH)[i];

    if (mu.pt() < muonPtCut_) continue;
    if (std::abs(mu.eta()) > muonEtaCut_) continue;

    if (mu.pt() > bestPt) {
      bestPt = mu.pt();
      bestIdx = i;
    }
  }

  // If we found a muon, build features and evaluate
  if (bestIdx >= 0) {
    const reco::RecoChargedCandidateRef muonRef =
        edm::getRef(chargedCandidatesH, bestIdx);

    // Get isolations (invert to match training: iso -> 10 - iso with 10 being
    // the default for missing)
    const float ecalIso =
        ecalIsoMapH.isValid() ? (*ecalIsoMapH)[muonRef] : 10.f;
    const float hcalIso =
        hcalIsoMapH.isValid() ? (*hcalIsoMapH)[muonRef] : 10.f;
    const float trkIso =
        trackIsoMapH.isValid() ? (*trackIsoMapH)[muonRef] : 10.f;

    // Feature order as requested:
    // [0] external score (from l1tTopoBDTProducer:score)
    // [1] leading muon pt
    // [2] leading muon track iso
    // [3] leading muon ecal iso
    // [4] leading muon hcal iso
    std::vector<float> features;
    features.reserve(5);
    features.push_back(extScore);
    features.push_back(bestPt);
    features.push_back(10 - (trkIso) / bestPt);
    features.push_back(10 - (ecalIso) / bestPt);
    features.push_back(10 - (hcalIso) / bestPt);

    const std::vector<float> output = bdt_->decision_function(features);
    if (!output.empty()) outScore = output[0];

    // print debug info
    if (debug_) {
      // print out features for debugging
      std::cout << "HLTTopoMuonHTConiferBDTProducer: features: ";
      for (const auto& f : features) {
        std::cout << f << " ";
      }

      std::cout << " extScore: " << extScore << " muPt: " << bestPt
                << " ecalIso: " << ecalIso << " hcalIso: " << hcalIso
                << " trkIso: " << trkIso << std::endl;

      std::cout << "HLTTopoMuonHTConiferBDTProducer: "
                //  << " extScore: " << extScore << " muPt: " << bestPt << "
                //  ecalIso: " << ecalIso
                //  << " hcalIso: " << hcalIso << " trkIso: " << trkIso
                << " --> BDT score: " << outScore << std::endl;
    }
  }
  iEvent.put(std::make_unique<float>(outScore), "score");
}

void HLTTopoMuonHTConiferBDTProducer::fillDescriptions(
    edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  // External float from earlier producer
  desc.add<edm::InputTag>("l1tTopoScore",
                          edm::InputTag("l1tTopoBDTProducer", "score"));

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
  desc.add<std::string>(
      "modelPath",
      "L1Trigger/TopoML/data/"
      "Jan26_HLT_conif_model_HH2b2W1L_1mu_L1MuTOPOMuHT_Mu_pt-iso.json");

  desc.add<double>("muonPtCut", 4.0);
  desc.add<double>("muonEtaCut", 2.4);

  desc.add<bool>("debug", false)->setComment("Enable debug printouts");

  descriptions.add("HLTTopoMuonHTConiferBDTProducer", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(HLTTopoMuonHTConiferBDTProducer);
