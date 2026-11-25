// Extension table for the HLT PF-candidate table (hltPFCandidate, src hltParticleFlowTmp, no cut):
//   trackIdx    index of the candidate's track in hltGeneralTracks (-1: no track, or a track of another collection).
//               Replaces the stock trackIndex = trackRef().key() stored as uint8, which wraps above 255 and does not
//               check which collection the track belongs to.
//   puppiWeight the PUPPI weight used to build hltAK4PFPuppiJets (ValueMap<float> of hltPFPuppi)
//   pvIdx, pvQuality  vertex association of hltPrimaryVertexAssociation ("original"): index in hltOfflinePrimaryVertices
//               (-1: none) and the PrimaryVertexAssignment quality, as used for ParT's "frompv" input.
#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

class HLTPFCandidateExtTableProducer : public edm::global::EDProducer<> {
public:
  explicit HLTPFCandidateExtTableProducer(const edm::ParameterSet& ps)
      : cands_(consumes<reco::PFCandidateCollection>(ps.getParameter<edm::InputTag>("candidates"))),
        tracks_(consumes<reco::TrackCollection>(ps.getParameter<edm::InputTag>("tracks"))),
        puppi_(consumes<edm::ValueMap<float>>(ps.getParameter<edm::InputTag>("puppiWeights"))),
        pvAssoc_(consumes<edm::Association<reco::VertexCollection>>(ps.getParameter<edm::InputTag>("vertexAssociation"))),
        pvQual_(consumes<edm::ValueMap<int>>(ps.getParameter<edm::InputTag>("vertexAssociation"))),
        name_(ps.getParameter<std::string>("name")) {
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("candidates", edm::InputTag("hltParticleFlowTmp"));
    desc.add<edm::InputTag>("tracks", edm::InputTag("hltGeneralTracks"));
    desc.add<edm::InputTag>("puppiWeights", edm::InputTag("hltPFPuppi"));
    desc.add<edm::InputTag>("vertexAssociation", edm::InputTag("hltPrimaryVertexAssociation", "original"));
    desc.add<std::string>("name", "hltPFCandidate");
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const override {
    auto hC = iEvent.getHandle(cands_);
    const size_t n = hC.isValid() ? hC->size() : 0;
    auto hTk = iEvent.getHandle(tracks_);
    auto hPu = iEvent.getHandle(puppi_);
    auto hPV = iEvent.getHandle(pvAssoc_);
    auto hQ = iEvent.getHandle(pvQual_);
    std::vector<int32_t> trackIdx(n, -1);
    std::vector<float> puppiW(n, -1.f);
    std::vector<int16_t> pvIdx(n, -1);
    std::vector<int16_t> pvQ(n, -1);
    for (size_t i = 0; i < n; ++i) {
      const auto& c = (*hC)[i];
      if (hTk.isValid() && c.trackRef().isNonnull() && c.trackRef().id() == hTk.id())
        trackIdx[i] = c.trackRef().key();
      reco::PFCandidateRef ref(hC, i);
      if (hPu.isValid() && hPu->contains(ref.id()))
        puppiW[i] = (*hPu)[ref];
      if (hPV.isValid()) {
        auto v = (*hPV)[ref];
        if (v.isNonnull())
          pvIdx[i] = v.key();
      }
      if (hQ.isValid() && hQ->contains(ref.id()))
        pvQ[i] = (*hQ)[ref];
    }
    auto t = std::make_unique<nanoaod::FlatTable>(n, name_, false, true);
    t->addColumn<int32_t>("trackIdx", trackIdx, "index in the hltGeneralTrack table (-1: no track or another collection)");
    t->addColumn<float>("puppiWeight", puppiW, "PUPPI weight of hltPFPuppi (-1: unavailable)", 10);
    t->addColumn<int16_t>("pvIdx", pvIdx, "associated vertex in hltPrimaryVertex (hltPrimaryVertexAssociation:original), -1: none");
    t->addColumn<int16_t>("pvQuality", pvQ, "PrimaryVertexAssignment quality (hltPrimaryVertexAssociation:original), -1: unavailable");
    iEvent.put(std::move(t));
  }

private:
  const edm::EDGetTokenT<reco::PFCandidateCollection> cands_;
  const edm::EDGetTokenT<reco::TrackCollection> tracks_;
  const edm::EDGetTokenT<edm::ValueMap<float>> puppi_;
  const edm::EDGetTokenT<edm::Association<reco::VertexCollection>> pvAssoc_;
  const edm::EDGetTokenT<edm::ValueMap<int>> pvQual_;
  const std::string name_;
};

DEFINE_FWK_MODULE(HLTPFCandidateExtTableProducer);
