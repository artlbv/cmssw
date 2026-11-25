// Extension table for the HLT AK4 PUPPI jet table (hltAK4PuppiJet, src hltAK4PFPuppiJets, no cut):
//   jecFactor      the HLT's own correction (hltAK4PFPuppiJetCorrector: L1FastJet x L2Relative x L3Absolute), so that
//                  corrected pT = pt * jecFactor, as in hltAK4PFPuppiJetsCorrected
//   hadronFlavour, partonFlavour, nBHadrons, nCHadrons   from JetFlavourClustering run on these jets (optional, MC)
//   genJetIdx      index in the GenJet table of the closest gen jet within maxDR (-1: none); the gen-jet collection and
//                  cut must be those of the GenJet table, so that the index matches its rows
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "JetMETCorrections/JetCorrector/interface/JetCorrector.h"
#include "DataFormats/JetMatching/interface/JetFlavourInfoMatching.h"

class HLTJetExtTableProducer : public edm::global::EDProducer<> {
public:
  explicit HLTJetExtTableProducer(const edm::ParameterSet& ps)
      : jets_(consumes<edm::View<reco::Jet>>(ps.getParameter<edm::InputTag>("jets"))),
        corrector_(consumes<reco::JetCorrector>(ps.getParameter<edm::InputTag>("corrector"))),
        name_(ps.getParameter<std::string>("name")),
        genJetCut_(ps.getParameter<std::string>("genJetCut"), true),
        maxDR_(ps.getParameter<double>("maxDR")) {
    const auto fl = ps.getParameter<edm::InputTag>("flavourInfos");
    if (!fl.label().empty())
      flavour_ = consumes<reco::JetFlavourInfoMatchingCollection>(fl);
    const auto gj = ps.getParameter<edm::InputTag>("genJets");
    if (!gj.label().empty())
      genJets_ = consumes<edm::View<reco::GenJet>>(gj);
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("jets", edm::InputTag("hltAK4PFPuppiJets"));
    desc.add<edm::InputTag>("corrector", edm::InputTag("hltAK4PFPuppiJetCorrector"));
    desc.add<edm::InputTag>("flavourInfos", edm::InputTag(""));
    desc.add<edm::InputTag>("genJets", edm::InputTag(""));
    desc.add<std::string>("genJetCut", "pt > 10");
    desc.add<double>("maxDR", 0.4);
    desc.add<std::string>("name", "hltAK4PuppiJet");
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    auto hJ = iEvent.getHandle(jets_);
    const size_t n = hJ.isValid() ? hJ->size() : 0;
    std::vector<float> jec(n, -1.f);
    std::vector<int16_t> hadFl(n, -1), partFl(n, -1), nB(n, -1), nC(n, -1), genIdx(n, -1);
    if (n > 0) {
      auto hCorr = iEvent.getHandle(corrector_);
      if (hCorr.isValid())
        for (size_t i = 0; i < n; ++i)
          jec[i] = hCorr->correction((*hJ)[i]);
      if (!flavour_.isUninitialized()) {
        auto hF = iEvent.getHandle(flavour_);
        if (hF.isValid()) {
          for (size_t i = 0; i < n; ++i) {
            const auto& info = (*hF)[hJ->refAt(i)];
            hadFl[i] = info.getHadronFlavour();
            partFl[i] = info.getPartonFlavour();
            nB[i] = info.getbHadrons().size();
            nC[i] = info.getcHadrons().size();
          }
        }
      }
      if (!genJets_.isUninitialized()) {
        auto hG = iEvent.getHandle(genJets_);
        if (hG.isValid()) {
          std::vector<const reco::GenJet*> sel;  // rows of the GenJet table: collection order after the cut
          for (const auto& g : *hG)
            if (genJetCut_(g))
              sel.push_back(&g);
          for (size_t i = 0; i < n; ++i) {
            float best = maxDR_;
            for (size_t k = 0; k < sel.size(); ++k) {
              const float dr = reco::deltaR(*sel[k], (*hJ)[i]);
              if (dr < best) {
                best = dr;
                genIdx[i] = k;
              }
            }
          }
        }
      }
    }
    auto t = std::make_unique<nanoaod::FlatTable>(n, name_, false, true);
    t->addColumn<float>("jecFactor", jec, "HLT JEC factor (L1FastJet x L2Relative x L3Absolute); -1 if unavailable", 12);
    t->addColumn<int16_t>("hadronFlavour", hadFl, "hadron flavour (JetFlavourClustering, ghost B/C hadrons); -1 if unavailable");
    t->addColumn<int16_t>("partonFlavour", partFl, "parton flavour (JetFlavourClustering); -1 if unavailable");
    t->addColumn<int16_t>("nBHadrons", nB, "number of clustered B hadrons; -1 if unavailable");
    t->addColumn<int16_t>("nCHadrons", nC, "number of clustered C hadrons; -1 if unavailable");
    t->addColumn<int16_t>("genJetIdx", genIdx, "index of the closest GenJet within dR < maxDR; -1 if none");
    iEvent.put(std::move(t));
  }

private:
  const edm::EDGetTokenT<edm::View<reco::Jet>> jets_;
  const edm::EDGetTokenT<reco::JetCorrector> corrector_;
  edm::EDGetTokenT<reco::JetFlavourInfoMatchingCollection> flavour_;
  edm::EDGetTokenT<edm::View<reco::GenJet>> genJets_;
  const std::string name_;
  const StringCutObjectSelector<reco::GenJet> genJetCut_;
  const double maxDR_;
};

DEFINE_FWK_MODULE(HLTJetExtTableProducer);
