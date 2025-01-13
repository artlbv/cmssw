// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"
#include "DataFormats/Common/interface/OrphanHandle.h"

class Run3ScoutingVertexToRecoVertexProducer : public edm::stream::EDProducer<> {
public:
    explicit Run3ScoutingVertexToRecoVertexProducer(const edm::ParameterSet &);
    ~Run3ScoutingVertexToRecoVertexProducer() override;

    static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);
    void beginStream(edm::StreamID) override {}
    void produce(edm::Event &iEvent, edm::EventSetup const &setup) override;
    void endStream() override {}

    reco::Vertex createVertex(Run3ScoutingVertex scoutingvertex);
    void createVertices(edm::Handle<std::vector<Run3ScoutingVertex>> scoutingvertexHandle,
                        std::unique_ptr<reco::VertexCollection> &vertices);

private:
    const edm::EDGetTokenT<std::vector<Run3ScoutingVertex>> input_scoutingvertex_token_; 
};

Run3ScoutingVertexToRecoVertexProducer::Run3ScoutingVertexToRecoVertexProducer(
    const edm::ParameterSet &iConfig)
    : input_scoutingvertex_token_(consumes(iConfig.getParameter<edm::InputTag>("scoutingvertex"))){
    
    //register products
    produces<reco::VertexCollection>();
}

Run3ScoutingVertexToRecoVertexProducer::~Run3ScoutingVertexToRecoVertexProducer() = default;

reco::Vertex Run3ScoutingVertexToRecoVertexProducer::createVertex(Run3ScoutingVertex scoutingvertex){

    reco::Vertex::Point point(scoutingvertex.x(), scoutingvertex.y(), scoutingvertex.z());
    reco::Vertex::Error error;
    // error[0][0] = scoutingvertex.xError();
    // error[1][1] = scoutingvertex.yError();
    // error[2][2] = scoutingvertex.zError();
    // https://github.com/cms-sw/cmssw/blob/master/DataFormats/VertexReco/interface/Vertex.h#L138
    error(0,0) = scoutingvertex.xError();
    error(1,1) = scoutingvertex.yError();
    error(2,2) = scoutingvertex.zError();

    // https://github.com/cms-sw/cmssw/blob/a3ba3791d7c94ef9484543a28f05b13b15c06bbd/HLTrigger/JetMET/plugins/HLTScoutingPFProducer.cc#L129
    error(0,1) = scoutingvertex.xyCov();
    error(0,2) = scoutingvertex.xyCov();
    error(1,2) = scoutingvertex.xyCov();

    return scoutingvertex.isValidVtx() ? reco::Vertex(point, error, scoutingvertex.chi2(), scoutingvertex.ndof(), scoutingvertex.tracksSize()): reco::Vertex(point, error);
}

void Run3ScoutingVertexToRecoVertexProducer::createVertices(
    edm::Handle<std::vector<Run3ScoutingVertex>> scoutingvertexHandle,
    std::unique_ptr<reco::VertexCollection> &vertices) {

    for (unsigned int ivertex = 0; ivertex < scoutingvertexHandle->size(); ++ivertex) {
        auto &scoutingvertex = (*scoutingvertexHandle)[ivertex];
        vertices->push_back(createVertex(scoutingvertex));
    } 
}

void Run3ScoutingVertexToRecoVertexProducer::produce(edm::Event &iEvent, edm::EventSetup const &setep){
    using namespace edm;
    Handle<std::vector<Run3ScoutingVertex>> scoutingvertexHandle;
    iEvent.getByToken(input_scoutingvertex_token_, scoutingvertexHandle);

    auto vertices = std::make_unique<reco::VertexCollection>();
    createVertices(scoutingvertexHandle, vertices);
    //std::cout << "populate vertices" << std::endl;
    iEvent.put(std::move(vertices));
}

void Run3ScoutingVertexToRecoVertexProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("scoutingvertex", edm::InputTag("hltScoutingPrimaryVertexPacker"));
  descriptions.addWithDefaultLabel(desc);
}

// declare this class as a framework plugin
DEFINE_FWK_MODULE(Run3ScoutingVertexToRecoVertexProducer);