// Jet -> constituent links for the HLT nano, adapted from PhysicsTools/NanoAOD/plugins/SimpleJetConstituentTableProducer.cc
// (the producer of the offline FatJetPFCand table), which is instantiated only for pat::Jet / reco::GenJet.
// Changes w.r.t. the original:
//   - works on any reco::Jet view with constituents from any reco::Candidate view (here hltAK4PFPuppiJets and
//     hltParticleFlowTmp), so no per-type initptr() specialisation is needed;
//   - a constituent not found in the candidate collection gets candIdx = -1 instead of being dropped, so that a
//     mismatch between the jet constituents and the candidate table is visible;
//   - no side collection of constituent Ptrs (no dictionary for std::vector<edm::Ptr<reco::PFCandidate>>);
//   - candidates are looked up through a (ProductID, key) -> index map instead of std::find.
// One row per (jet passing jetCut, constituent passing jetConstCut). jetIdx is the index among ALL jets, so it matches
// the jet table only if that table has no cut (hltJetTable: cut "").
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include <unordered_map>

class HLTJetConstituentTableProducer : public edm::global::EDProducer<> {
public:
  explicit HLTJetConstituentTableProducer(const edm::ParameterSet& iConfig)
      : name_(iConfig.getParameter<std::string>("name")),
        candIdxName_(iConfig.getParameter<std::string>("candIdxName")),
        candIdxDoc_(iConfig.getParameter<std::string>("candIdxDoc")),
        jet_token_(consumes<edm::View<reco::Jet>>(iConfig.getParameter<edm::InputTag>("jets"))),
        cand_token_(consumes<reco::CandidateView>(iConfig.getParameter<edm::InputTag>("candidates"))),
        jetCut_(iConfig.getParameter<std::string>("jetCut"), true),
        jetConstCut_(iConfig.getParameter<std::string>("jetConstCut"), true),
        skip_(iConfig.getParameter<bool>("skipNonExistingSrc")) {
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<std::string>("name", "hltAK4PuppiJetPFCand");
    desc.add<std::string>("candIdxName", "pfCandIdx");
    desc.add<std::string>("candIdxDoc", "Index in the hltPFCandidate table (-1: not in that collection)");
    desc.add<edm::InputTag>("jets", edm::InputTag("hltAK4PFPuppiJets"));
    desc.add<edm::InputTag>("candidates", edm::InputTag("hltParticleFlowTmp"));
    desc.add<std::string>("jetCut", "");
    desc.add<std::string>("jetConstCut", "");
    desc.add<bool>("skipNonExistingSrc", true);
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    std::vector<int> parentJetIdx, candIdx;
    auto jets = iEvent.getHandle(jet_token_);
    auto cands = iEvent.getHandle(cand_token_);
    if (jets.isValid() && cands.isValid()) {
      // (ProductID, key) of every candidate -> its index in the candidate view
      std::unordered_map<uint64_t, int> index;
      index.reserve(cands->size());
      auto ptrKey = [](const reco::CandidatePtr& p) {
        return (uint64_t(p.id().processIndex()) << 48) ^ (uint64_t(p.id().productIndex()) << 32) ^ uint64_t(p.key());
      };
      const auto candPtrs = cands->ptrs();
      for (size_t i = 0; i < candPtrs.size(); ++i)
        index.emplace(ptrKey(candPtrs[i]), int(i));
      for (unsigned jetIdx = 0; jetIdx < jets->size(); ++jetIdx) {
        const auto& jet = (*jets)[jetIdx];
        if (!jetCut_(jet))
          continue;
        for (const auto& dauPtr : jet.daughterPtrVector()) {
          if (dauPtr.isNull() || !jetConstCut_(*dauPtr))
            continue;
          auto it = index.find(ptrKey(dauPtr));
          parentJetIdx.push_back(jetIdx);
          candIdx.push_back(it == index.end() ? -1 : it->second);
        }
      }
    } else if (!skip_) {
      throw cms::Exception("ProductNotFound") << "HLTJetConstituentTableProducer: jets or candidates missing";
    }
    auto candTable = std::make_unique<nanoaod::FlatTable>(candIdx.size(), name_, false);
    candTable->setDoc("HLT jet constituents: one row per (jet, constituent) pair");
    candTable->addColumn<int>(candIdxName_, candIdx, candIdxDoc_);
    candTable->addColumn<int>("jetIdx", parentJetIdx, "Index of the parent jet");
    iEvent.put(std::move(candTable));
  }

private:
  const std::string name_, candIdxName_, candIdxDoc_;
  const edm::EDGetTokenT<edm::View<reco::Jet>> jet_token_;
  const edm::EDGetTokenT<reco::CandidateView> cand_token_;
  const StringCutObjectSelector<reco::Jet> jetCut_;
  const StringCutObjectSelector<reco::Candidate> jetConstCut_;
  const bool skip_;
};

DEFINE_FWK_MODULE(HLTJetConstituentTableProducer);
