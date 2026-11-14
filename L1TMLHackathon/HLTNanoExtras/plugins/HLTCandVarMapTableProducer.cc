// Table of HLT candidates (egamma RecoEcalCandidates or muon RecoChargedCandidates) with every variable map the HLT
// filters cut on, so that the paths can be re-emulated and retuned offline.
//   floatMaps   AssociationMap<OneToValue<std::vector<T>, float>> (RecoEcalCandidateIsolationMap /
//               RecoChargedCandidateIsolationMap): shower shapes, H/E, isolations, pixel match, GSF-track variables
//   doubleMaps  edm::ValueMap<double> keyed on the candidates (e.g. the L3 muon combined relative track isolation)
//   rho         optional double, written as a per-candidate column (the effective-area input of the iso filters)
// A variable that is missing for a candidate (map absent in the event, or candidate not in the map) is -999.
// The column set is fixed by the configuration, so every event has the same branches.
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToValue.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/EgammaReco/interface/SuperCluster.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/RecoCandidate/interface/RecoChargedCandidate.h"
#include "DataFormats/RecoCandidate/interface/RecoEcalCandidate.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

template <typename T>
class HLTCandVarMapTableProducer : public edm::global::EDProducer<> {
  using Coll = std::vector<T>;
  using FloatMap = edm::AssociationMap<edm::OneToValue<Coll, float>>;
  struct Var {
    std::string name, doc;
    int precision;
  };

public:
  explicit HLTCandVarMapTableProducer(const edm::ParameterSet& ps)
      : src_(consumes<Coll>(ps.getParameter<edm::InputTag>("src"))),
        name_(ps.getParameter<std::string>("name")),
        doc_(ps.getParameter<std::string>("doc")),
        precision_(ps.getParameter<int>("precision")) {
    for (const auto& p : ps.getParameter<std::vector<edm::ParameterSet>>("floatMaps")) {
      fTok_.push_back(consumes<FloatMap>(p.getParameter<edm::InputTag>("src")));
      fVar_.push_back({p.getParameter<std::string>("name"), p.getParameter<edm::InputTag>("src").encode(), precision_});
    }
    for (const auto& p : ps.getParameter<std::vector<edm::ParameterSet>>("doubleMaps")) {
      dTok_.push_back(consumes<edm::ValueMap<double>>(p.getParameter<edm::InputTag>("src")));
      dVar_.push_back({p.getParameter<std::string>("name"), p.getParameter<edm::InputTag>("src").encode(), precision_});
    }
    const auto rho = ps.getParameter<edm::InputTag>("rho");
    if (!rho.label().empty())
      rho_ = consumes<double>(rho);
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription var;
    var.add<std::string>("name");
    var.add<edm::InputTag>("src");
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src");
    desc.add<std::string>("name");
    desc.add<std::string>("doc", "");
    desc.add<int>("precision", 12);
    desc.addVPSet("floatMaps", var, {});
    desc.addVPSet("doubleMaps", var, {});
    desc.add<edm::InputTag>("rho", edm::InputTag(""));
    descriptions.addDefault(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    constexpr float kNone = -999.f;
    auto hC = iEvent.getHandle(src_);
    const size_t n = hC.isValid() ? hC->size() : 0;
    std::vector<float> pt(n), eta(n), phi(n), energy(n), scEta(n, kNone), scEnergy(n, kNone), rhoCol(n, kNone);
    std::vector<int16_t> charge(n);
    for (size_t i = 0; i < n; ++i) {
      const auto& c = (*hC)[i];
      pt[i] = c.pt();
      eta[i] = c.eta();
      phi[i] = c.phi();
      energy[i] = c.energy();
      charge[i] = c.charge();
      if constexpr (std::is_same_v<T, reco::RecoEcalCandidate>) {
        if (c.superCluster().isNonnull()) {
          scEta[i] = c.superCluster()->eta();
          scEnergy[i] = c.superCluster()->energy();
        }
      }
    }
    if (!rho_.isUninitialized()) {
      auto hR = iEvent.getHandle(rho_);
      if (hR.isValid())
        std::fill(rhoCol.begin(), rhoCol.end(), float(*hR));
    }
    auto t = std::make_unique<nanoaod::FlatTable>(n, name_, false, false);
    t->setDoc(doc_);
    t->addColumn<float>("pt", pt, "candidate pT (egamma: E_T) (GeV)", precision_);
    t->addColumn<float>("eta", eta, "candidate eta", precision_);
    t->addColumn<float>("phi", phi, "candidate phi", precision_);
    t->addColumn<float>("energy", energy, "candidate energy (GeV)", precision_);
    t->addColumn<int16_t>("charge", charge, "candidate charge");
    if constexpr (std::is_same_v<T, reco::RecoEcalCandidate>) {
      t->addColumn<float>("scEta", scEta, "supercluster eta", precision_);
      t->addColumn<float>("scEnergy", scEnergy, "supercluster energy (GeV)", precision_);
    }
    if (!rho_.isUninitialized())
      t->addColumn<float>("rho", rhoCol, "event rho of the isolation filters (same for all rows)", precision_);
    for (size_t k = 0; k < fTok_.size(); ++k) {
      std::vector<float> v(n, kNone);
      auto hM = iEvent.getHandle(fTok_[k]);
      if (hM.isValid()) {
        for (size_t i = 0; i < n; ++i) {
          auto it = hM->find(edm::Ref<Coll>(hC, i));
          if (it != hM->end())
            v[i] = it->val;
        }
      }
      t->addColumn<float>(fVar_[k].name, v, fVar_[k].doc + " (-999: not computed)", fVar_[k].precision);
    }
    for (size_t k = 0; k < dTok_.size(); ++k) {
      std::vector<float> v(n, kNone);
      auto hM = iEvent.getHandle(dTok_[k]);
      if (hM.isValid() && n > 0 && hM->contains(hC.id())) {
        for (size_t i = 0; i < n; ++i)
          v[i] = (*hM)[edm::Ref<Coll>(hC, i)];
      }
      t->addColumn<float>(dVar_[k].name, v, dVar_[k].doc + " (-999: not computed)", dVar_[k].precision);
    }
    iEvent.put(std::move(t));
  }

private:
  const edm::EDGetTokenT<Coll> src_;
  const std::string name_, doc_;
  const int precision_;
  std::vector<edm::EDGetTokenT<FloatMap>> fTok_;
  std::vector<edm::EDGetTokenT<edm::ValueMap<double>>> dTok_;
  std::vector<Var> fVar_, dVar_;
  edm::EDGetTokenT<double> rho_;
};

typedef HLTCandVarMapTableProducer<reco::RecoEcalCandidate> HLTEgammaVarMapTableProducer;
typedef HLTCandVarMapTableProducer<reco::RecoChargedCandidate> HLTMuonVarMapTableProducer;
DEFINE_FWK_MODULE(HLTEgammaVarMapTableProducer);
DEFINE_FWK_MODULE(HLTMuonVarMapTableProducer);
