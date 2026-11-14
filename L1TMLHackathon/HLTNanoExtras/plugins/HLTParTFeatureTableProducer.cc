// The HLT ParT AK4 tagger's own input features (HLTParticleTransformerAK4TagInfo), as filled by
// HLTParticleTransformerAK4TagInfoProducer, so that the stored ParT scores can be reproduced exactly from the nano:
//   <name>Cpf  one row per (jet, constituent): jetIdx + the 28 HLTCpfCandidateFeatures, in the C++ (= ONNX input) order
//   <name>SV   one row per (jet, secondary vertex): jetIdx + the 16 HLTVtxFeatures, in the C++ order
// Rows are grouped by jet, in the producer's order (constituents by decreasing pt, SVs by the producer's sorting), and
// truncated to the first maxCpf / maxSV entries, which is what HLTParticleTransformerAK4ONNXJetTagsProducer feeds the
// model (zero-padded beyond). jetIdx is the index of the jet in the tag infos' jet collection (hltAK4PFPuppiJets, i.e.
// the hltAK4PuppiJet table, which has no cut). Jets outside the tagger acceptance (is_filled false) have no rows.
// A third table extends the jet table (one row per jet): acceptance flag, row counts, and the global features (the
// jet's own pt/eta/phi/energy) at full precision.
#include "DataFormats/BTauReco/interface/HLTParticleTransformerAK4TagInfo.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

class HLTParTFeatureTableProducer : public edm::global::EDProducer<> {
public:
  explicit HLTParTFeatureTableProducer(const edm::ParameterSet& ps)
      : tagInfos_(consumes<reco::HLTParticleTransformerAK4TagInfoCollection>(ps.getParameter<edm::InputTag>("tagInfos"))),
        name_(ps.getParameter<std::string>("name")),
        jetName_(ps.getParameter<std::string>("jetName")),
        maxCpf_(ps.getParameter<unsigned>("maxCpf")),
        maxSV_(ps.getParameter<unsigned>("maxSV")),
        precision_(ps.getParameter<int>("precision")) {
    produces<nanoaod::FlatTable>("cpf");
    produces<nanoaod::FlatTable>("sv");
    produces<nanoaod::FlatTable>("global");
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("tagInfos", edm::InputTag("hltParticleTransformerAK4TagInfos"));
    desc.add<std::string>("name", "hltAK4PuppiJetParT");
    desc.add<std::string>("jetName", "hltAK4PuppiJet");
    desc.add<unsigned>("maxCpf", 50);
    desc.add<unsigned>("maxSV", 5);
    desc.add<int>("precision", -1)->setComment("mantissa bits of the feature columns; -1: full float");
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    auto h = iEvent.getHandle(tagInfos_);
    constexpr unsigned nC = 28, nV = 16;
    static const char* cN[nC] = {"deta", "dphi", "pt_log", "energy_log", "charge", "frompv", "nlostinnerhits",
                                 "track_chi2", "track_qual", "dz", "dzsig", "dxy", "dxysig", "etarel", "pperp_ratio",
                                 "ppara_ratio", "trackjet_d3d", "trackjet_d3dsig", "trackjet_dist", "trackjet_decayL",
                                 "npixhits", "nstriphits", "highpurity", "id", "pt", "eta", "phi", "energy"};
    static const char* vN[nV] = {"deta", "dphi", "pt_log", "mass", "ntrack", "chi2", "dxy", "dxysig",
                                 "d3d", "d3dsig", "costhetasvpv", "enratio", "pt", "eta", "phi", "energy"};
    std::vector<int16_t> cJ, vJ;
    std::vector<std::vector<float>> c(nC), v(nV);
    const size_t nTI = h.isValid() ? h->size() : 0;
    std::vector<uint8_t> filled(nTI, 0);
    std::vector<int16_t> nCpf(nTI, 0), nSV(nTI, 0);
    std::vector<float> gPt(nTI, 0), gEta(nTI, 0), gPhi(nTI, 0), gE(nTI, 0);
    for (size_t i = 0; i < nTI; ++i) {
      const auto& ti = (*h)[i];
      // tag infos are made one per jet, in jet-collection order; check, and use the ref's key as the row index
      const int16_t j = ti.jet().isNonnull() ? int16_t(ti.jet().key()) : int16_t(i);
      if (size_t(j) != i)
        throw cms::Exception("HLTParTFeatureTableProducer") << "tag info " << i << " points to jet " << j;
      const auto& f = ti.features();
      gPt[i] = f.global_features.jet_pt;
      gEta[i] = f.global_features.jet_eta;
      gPhi[i] = f.global_features.jet_phi;
      gE[i] = f.global_features.jet_energy;
      if (!f.is_filled)
        continue;
      filled[i] = 1;
      const size_t nc = std::min<size_t>(f.cpf_candidates.size(), maxCpf_);
      const size_t nv = std::min<size_t>(f.vtx_features.size(), maxSV_);
      nCpf[i] = nc;
      nSV[i] = nv;
      for (size_t k = 0; k < nc; ++k) {
        const auto& x = f.cpf_candidates[k];
        const float vals[nC] = {x.jet_pfcand_deta, x.jet_pfcand_dphi, x.jet_pfcand_pt_log, x.jet_pfcand_energy_log,
                                x.jet_pfcand_charge, x.jet_pfcand_frompv, x.jet_pfcand_nlostinnerhits,
                                x.jet_pfcand_track_chi2, x.jet_pfcand_track_qual, x.jet_pfcand_dz, x.jet_pfcand_dzsig,
                                x.jet_pfcand_dxy, x.jet_pfcand_dxysig, x.jet_pfcand_etarel, x.jet_pfcand_pperp_ratio,
                                x.jet_pfcand_ppara_ratio, x.jet_pfcand_trackjet_d3d, x.jet_pfcand_trackjet_d3dsig,
                                x.jet_pfcand_trackjet_dist, x.jet_pfcand_trackjet_decayL, x.jet_pfcand_npixhits,
                                x.jet_pfcand_nstriphits, x.jet_pfcand_highpurity, x.jet_pfcand_id, x.jet_pfcand_pt,
                                x.jet_pfcand_eta, x.jet_pfcand_phi, x.jet_pfcand_energy};
        cJ.push_back(j);
        for (unsigned q = 0; q < nC; ++q)
          c[q].push_back(vals[q]);
      }
      for (size_t k = 0; k < nv; ++k) {
        const auto& x = f.vtx_features[k];
        const float vals[nV] = {x.jet_sv_deta, x.jet_sv_dphi, x.jet_sv_pt_log, x.jet_sv_mass, x.jet_sv_ntrack,
                                x.jet_sv_chi2, x.jet_sv_dxy, x.jet_sv_dxysig, x.jet_sv_d3d, x.jet_sv_d3dsig,
                                x.jet_sv_costhetasvpv, x.jet_sv_enratio, x.jet_sv_pt, x.jet_sv_eta, x.jet_sv_phi,
                                x.jet_sv_energy};
        vJ.push_back(j);
        for (unsigned q = 0; q < nV; ++q)
          v[q].push_back(vals[q]);
      }
    }
    auto tc = std::make_unique<nanoaod::FlatTable>(cJ.size(), name_ + "Cpf", false, false);
    tc->setDoc("HLT ParT AK4 input: constituent features (HLTCpfCandidateFeatures, jet_pfcand_*), first " +
               std::to_string(maxCpf_) + " per jet, grouped by jet");
    tc->addColumn<int16_t>("jetIdx", cJ, "index of the jet in the " + jetName_ + " table");
    for (unsigned q = 0; q < nC; ++q)
      tc->addColumn<float>(cN[q], c[q], std::string("ParT input jet_pfcand_") + cN[q], precision_);
    auto tv = std::make_unique<nanoaod::FlatTable>(vJ.size(), name_ + "SV", false, false);
    tv->setDoc("HLT ParT AK4 input: secondary-vertex features (HLTVtxFeatures, jet_sv_*), first " +
               std::to_string(maxSV_) + " per jet, grouped by jet");
    tv->addColumn<int16_t>("jetIdx", vJ, "index of the jet in the " + jetName_ + " table");
    for (unsigned q = 0; q < nV; ++q)
      tv->addColumn<float>(vN[q], v[q], std::string("ParT input jet_sv_") + vN[q], precision_);
    // extension of the jet table (one row per jet): acceptance flag, row counts, full-precision global features
    auto tg = std::make_unique<nanoaod::FlatTable>(nTI, jetName_, false, true);
    tg->addColumn<uint8_t>("ParT_inputFilled", filled, "jet inside the ParT acceptance (tag-info features filled)");
    tg->addColumn<int16_t>("ParT_nCpf", nCpf, "rows of this jet in the " + name_ + "Cpf table");
    tg->addColumn<int16_t>("ParT_nSV", nSV, "rows of this jet in the " + name_ + "SV table");
    tg->addColumn<float>("ParT_jet_pt", gPt, "ParT global input jet_pt (0 outside the acceptance)", -1);
    tg->addColumn<float>("ParT_jet_eta", gEta, "ParT global input jet_eta", -1);
    tg->addColumn<float>("ParT_jet_phi", gPhi, "ParT global input jet_phi", -1);
    tg->addColumn<float>("ParT_jet_energy", gE, "ParT global input jet_energy", -1);
    iEvent.put(std::move(tc), "cpf");
    iEvent.put(std::move(tv), "sv");
    iEvent.put(std::move(tg), "global");
  }

private:
  const edm::EDGetTokenT<reco::HLTParticleTransformerAK4TagInfoCollection> tagInfos_;
  const std::string name_, jetName_;
  const unsigned maxCpf_, maxSV_;
  const int precision_;
};

DEFINE_FWK_MODULE(HLTParTFeatureTableProducer);
