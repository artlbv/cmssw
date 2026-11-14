// Extension table for the HLT track table (hltGeneralTrack): impact parameters w.r.t. the leading primary vertex and the
// track-quality variables that the generic table lacks (several need enums, e.g. MISSING_INNER_HITS, which are safer in
// C++ than in the string parser). One row per track, same order as the base table, which must have no cut.
// PV = first vertex of `vertices` (hltOfflinePrimaryVertices, sorted by score); if there is none, the PV columns are -999.
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include <cmath>

class HLTTrackPVExtTableProducer : public edm::global::EDProducer<> {
public:
  explicit HLTTrackPVExtTableProducer(const edm::ParameterSet& ps)
      : tracks_(consumes<reco::TrackCollection>(ps.getParameter<edm::InputTag>("tracks"))),
        vertices_(consumes<reco::VertexCollection>(ps.getParameter<edm::InputTag>("vertices"))),
        name_(ps.getParameter<std::string>("name")),
        precision_(ps.getParameter<int>("precision")) {
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("tracks", edm::InputTag("hltGeneralTracks"));
    desc.add<edm::InputTag>("vertices", edm::InputTag("hltOfflinePrimaryVertices"));
    desc.add<std::string>("name", "hltGeneralTrack");
    desc.add<int>("precision", 10);
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    auto hTk = iEvent.getHandle(tracks_);
    auto hPV = iEvent.getHandle(vertices_);
    const size_t n = hTk.isValid() ? hTk->size() : 0;
    const reco::Vertex* pv = (hPV.isValid() && !hPV->empty()) ? &hPV->front() : nullptr;
    constexpr float kNone = -999.f;

    std::vector<float> dxyPV(n, kNone), dzPV(n, kNone), dxyPVErr(n, kNone), dzPVErr(n, kNone);
    std::vector<float> dxyErr(n), dzErr(n), ptErr(n), normChi2(n), px(n), py(n), pz(n);
    std::vector<int16_t> lostInner(n), nValid(n), nStrip(n), algo(n), originalAlgo(n);
    std::vector<bool> highPurity(n);
    for (size_t i = 0; i < n; ++i) {
      const auto& tk = (*hTk)[i];
      dxyErr[i] = tk.dxyError();
      dzErr[i] = tk.dzError();
      ptErr[i] = tk.ptError();
      normChi2[i] = tk.normalizedChi2();
      px[i] = tk.px();
      py[i] = tk.py();
      pz[i] = tk.pz();
      lostInner[i] = tk.hitPattern().numberOfLostHits(reco::HitPattern::MISSING_INNER_HITS);
      nValid[i] = tk.hitPattern().numberOfValidHits();
      nStrip[i] = tk.hitPattern().numberOfValidStripHits();
      algo[i] = tk.algo();
      originalAlgo[i] = tk.originalAlgo();
      highPurity[i] = tk.quality(reco::TrackBase::highPurity);
      if (pv) {
        dxyPV[i] = tk.dxy(pv->position());
        dzPV[i] = tk.dz(pv->position());
        dxyPVErr[i] = tk.dxyError(pv->position(), pv->covariance());
        dzPVErr[i] = std::hypot(tk.dzError(), pv->zError());
      }
    }
    auto t = std::make_unique<nanoaod::FlatTable>(n, name_, false, true);
    t->addColumn<float>("dxyPV", dxyPV, "dxy w.r.t. the leading primary vertex (cm); -999 if no PV", precision_);
    t->addColumn<float>("dzPV", dzPV, "dz w.r.t. the leading primary vertex (cm); -999 if no PV", precision_);
    t->addColumn<float>("dxyPVErr", dxyPVErr, "dxy error incl. the PV covariance (cm); -999 if no PV", precision_);
    t->addColumn<float>("dzPVErr", dzPVErr, "sqrt(dzError^2 + PV zError^2) (cm); -999 if no PV", precision_);
    t->addColumn<float>("dxyError", dxyErr, "dxy error (cm)", precision_);
    t->addColumn<float>("dzError", dzErr, "dz error (cm)", precision_);
    t->addColumn<float>("ptError", ptErr, "pT error (GeV)", precision_);
    t->addColumn<float>("normalizedChi2", normChi2, "chi2/ndof", precision_);
    t->addColumn<float>("px", px, "px (GeV)", precision_);
    t->addColumn<float>("py", py, "py (GeV)", precision_);
    t->addColumn<float>("pz", pz, "pz (GeV)", precision_);
    t->addColumn<int16_t>("lostInnerHits", lostInner, "hitPattern numberOfLostHits(MISSING_INNER_HITS)");
    t->addColumn<int16_t>("nValidHits", nValid, "number of valid hits");
    t->addColumn<int16_t>("nStripHits", nStrip, "number of valid strip hits");
    t->addColumn<int16_t>("algo", algo, "reco::TrackBase::TrackAlgorithm");
    t->addColumn<int16_t>("originalAlgo", originalAlgo, "reco::TrackBase::TrackAlgorithm before merging");
    t->addColumn<bool>("highPurity", highPurity, "highPurity quality flag");
    iEvent.put(std::move(t));
  }

private:
  const edm::EDGetTokenT<reco::TrackCollection> tracks_;
  const edm::EDGetTokenT<reco::VertexCollection> vertices_;
  const std::string name_;
  const int precision_;
};

DEFINE_FWK_MODULE(HLTTrackPVExtTableProducer);
