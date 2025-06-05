// FWCore includes
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

// File writing includes
// #include "DataFormats/NanoAOD/interface/FlatTable.h"
//#include "TTree.h"
//#include "FWCore/ServiceRegistry/interface/Service.h"
//#include "CommonTools/UtilAlgos/interface/TFileService.h"

// L1T includes
#include "DataFormats/L1Trigger/interface/Muon.h"
#include "DataFormats/L1Trigger/interface/EGamma.h"
#include "DataFormats/L1Trigger/interface/Tau.h"
#include "DataFormats/L1Trigger/interface/Jet.h"
#include "DataFormats/L1Trigger/interface/EtSum.h"

// conifer includes
#include "ap_fixed.h"
#include "conifer.h"

#include <iostream>

class L1TTopoBDTProducer : public edm::global::EDProducer<> {
public:
  explicit L1TTopoBDTProducer(const edm::ParameterSet& cfg);
  ~L1TTopoBDTProducer();

private:
  virtual void beginJob() override;
  virtual void produce(edm::StreamID id, edm::Event& iEvent, const edm::EventSetup& iSetup) const override;
  virtual void endJob() override;

  edm::EDGetToken muToken;
  edm::EDGetToken egToken;
  edm::EDGetToken tauToken;
  edm::EDGetToken jetToken;
  edm::EDGetToken sumToken;

  // number of objects to consider
  // nSums is the number of sums to consider, e.g. HT, MET, etc.
  bool useHT; // whether to use HT or not
  unsigned nSums;
  unsigned nMu;
  unsigned nEG;
  unsigned nTau;
  unsigned nJet;
  unsigned nFeatures;

  // emulator model path
  std::string model_path;
  // std::string name;

};

L1TTopoBDTProducer::L1TTopoBDTProducer(const edm::ParameterSet& cfg){
  // consume
  muToken = consumes<l1t::MuonBxCollection>(cfg.getParameter<edm::InputTag>("muToken"));
  egToken = consumes<l1t::EGammaBxCollection>(cfg.getParameter<edm::InputTag>("egToken"));
  tauToken = consumes<l1t::TauBxCollection>(cfg.getParameter<edm::InputTag>("tauToken"));
  jetToken = consumes<l1t::JetBxCollection>(cfg.getParameter<edm::InputTag>("jetToken"));
  sumToken = consumes<l1t::EtSumBxCollection>(cfg.getParameter<edm::InputTag>("etSumToken"));
  useHT = cfg.getParameter<bool>("useHT");
  nSums = 0; // initialize to 0, will be set later
  nMu = cfg.getParameter<unsigned>("nMu");
  nEG = cfg.getParameter<unsigned>("nEg");
  nTau = cfg.getParameter<unsigned>("nTau");
  nJet = cfg.getParameter<unsigned>("nJet");
  // total number of inputs to NN
  if (useHT) {
    nSums++; // use HT, so add 1 for HT
  }
  nFeatures = nSums + nMu + nEG + nTau + nJet; // only one input for the BDT, the pT 

  // collection name
  // set the collection name to the name of the producer
  // name = cfg.getParameter<std::string>("name");

  // store the path to the .json file
  model_path = cfg.getParameter<edm::FileInPath>("model_path").fullPath();

  // produce
  // produces<nanoaod::FlatTable>(name);
  produces<float>("score"); 
}

L1TTopoBDTProducer::~L1TTopoBDTProducer(){
}

void L1TTopoBDTProducer::produce(edm::StreamID id, edm::Event& iEvent, const edm::EventSetup& iSetup) const {
  using namespace edm;
  // get input collections
  // BXVector: first index is BX, second index is object
  edm::Handle<BXVector<l1t::Muon>> muons;
  edm::Handle<BXVector<l1t::EGamma>> egammas;
  edm::Handle<BXVector<l1t::Tau>> taus;
  edm::Handle<BXVector<l1t::Jet>> jets;
  edm::Handle<BXVector<l1t::EtSum>> sums;
  iEvent.getByToken(muToken, muons);
  iEvent.getByToken(egToken, egammas);
  iEvent.getByToken(tauToken, taus);
  iEvent.getByToken(jetToken, jets);
  iEvent.getByToken(sumToken, sums);

  std::vector<float> features(nFeatures, 0.0f);

  // The unscaled inputs are hwInts
  // ap_fixed<14,13> is wide enough for all the ET, pT, eta, phi
  // ap_fixed<14,13>* X_unscaled = new ap_fixed<14,13>[nFeatures];
  // // initialize to zeros
  // for(unsigned i = 0; i < nFeatures; i++){
  //   X_unscaled[i] = 0;
  // }

  // // fill the inputs
  unsigned ix = 0;
  // // sums first, just find the MET

  // // see https://github.com/cms-sw/cmssw/blob/CMSSW_9_0_X/DataFormats/L1Trigger/interface/EtSum.h#L21

  for(unsigned i = 0; i < sums->size(0); i++){
    if (useHT) {
      if(sums->at(0, i).getType() == l1t::EtSum::EtSumType::kTotalHt){
        features[ix++] = sums->at(0,i).pt();
        // X_unscaled[ix++] = sums->at(0,i).hwPt();
        // X_unscaled[ix++] = sums->at(0,i).hwPhi();
      }
    } else {
      // do not use HT, just skip it
    }
  }
  // jets next
  ix = 1 * ( nSums );
  for(unsigned i = 0; i < std::min(nJet, jets->size(0)); i++){
    features[ix++] = jets->at(0,i).pt();
    // X_unscaled[ix++] = jets->at(0, i).hwPt();
    // X_unscaled[ix++] = jets->at(0, i).hwEta();
    // X_unscaled[ix++] = jets->at(0, i).hwPhi();
  }
  // egammas next
  ix = 1 * ( nSums + nJet );
  for(unsigned i = 0; i < std::min(nEG, egammas->size(0)); i++){
    features[ix++] = egammas->at(0,i).pt();
    // X_unscaled[ix++] = egammas->at(0, i).hwPt();
    // X_unscaled[ix++] = egammas->at(0, i).hwEta();
    // X_unscaled[ix++] = egammas->at(0, i).hwPhi();
  }
  // muons next
  ix = 1 * ( nSums + nJet + nEG );
  for(unsigned i = 0; i < std::min(nMu, muons->size(0)); i++){
    features[ix++] = muons->at(0,i).pt();
    // X_unscaled[ix++] = muons->at(0, i).hwPt();
    // X_unscaled[ix++] = muons->at(0, i).hwEta();
    // X_unscaled[ix++] = muons->at(0, i).hwPhi();
  }
  // taus next
  ix = 1 * ( nSums + nJet + nEG + nMu );
  for(unsigned i = 0; i < std::min(nTau, taus->size(0)); i++){
    // features.push_back(taus->at(0,i).pt());
    features[ix++] = taus->at(0,i).pt();
    // X_unscaled[ix++] = taus->at(0, i).pt();
    // X_unscaled[ix++] = taus->at(0, i).eta();
    // X_unscaled[ix++] = taus->at(0, i).phi();
    // X_unscaled[ix++] = taus->at(0, i).hwPt();
    // X_unscaled[ix++] = taus->at(0, i).hwEta();
    // X_unscaled[ix++] = taus->at(0, i).hwPhi();
  }

  // Print all features if cms log mode is set to DEBUG 
  
  std::cout << "Features: N =";
  std::cout << features.size() << ", ";
  for (const auto& f : features) {
    std::cout << f << " ";
  }
  std::cout << std::endl;

  // inspiration from https://github.com/cms-sw/cmssw/blob/dfb36b819cec568bb2d2334380fabadf75329217/L1Trigger/L1TTrackMatch/plugins/DisplacedVertexProducer.cc

  // load the BDT model
  // conifer::BDT<ap_fixed<10, 5>, ap_fixed<10, 5>> bdt(model_path);
  conifer::BDT<float, float> bdt(model_path);

  // ap_fixed<13,2,AP_RND,AP_SAT> y; // output object

  // run the actual inference

  // collect features and classify using bdt
  // const std::vector<ap_fixed<10, 5>>& output =
  //     // bdt.decision_function({cot, z0, chi2B, nstub, n_missint, chi2rphi, chi2rz});
  //     bdt.decision_function({cot, z0, chi2B, nstub, n_missint, chi2rphi, chi2rz});
  // std::vector<float> output = {0}; // bdt.decision_function(features);

  if (features.size() != 7) {
    throw cms::Exception("L1TTopoBDTProducer") << "Number of features does not match expected size: "
                                               << features.size() << " != " << 7;
  }
  std::vector<float> output = bdt.decision_function(features);

  // print score
  std::cout << "BDT score: " << output.at(0) << std::endl;

  // store score in event
  // iEvent.put(std::make_unique<std::vector<float>>(y_vec), "scores");
  iEvent.put(std::make_unique<float>(output.at(0)), "score");
  // iEvent.put(std::make_unique<float>(output.at(0)));

  // // write the result to the output
  // // note cast from the ap_fixed emulated type to float for convenience
  // std::vector<float> y_vec;
  // y_vec.push_back(output.at(0));

  // // create a FlatTable to store the results
  // auto out = std::make_unique<nanoaod::FlatTable>(1, name, false);
  // out->addColumn<float>("y", y_vec, "model prediction");
  // iEvent.put(std::move(out), name);
}

void L1TTopoBDTProducer::beginJob(){
}

void L1TTopoBDTProducer::endJob(){
}

// // make fillDescriptions
// void L1TTopoBDTProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
//   edm::ParameterSetDescription desc;
//   desc.add<edm::InputTag>("muToken", edm::InputTag("l1tMuons"));
//   desc.add<edm::InputTag>("egToken", edm::InputTag("l1tEGamma"));
//   desc.add<edm::InputTag>("tauToken", edm::InputTag("l1tTau"));
//   desc.add<edm::InputTag>("jetToken", edm::InputTag("l1tJet"));
//   desc.add<edm::InputTag>("etSumToken", edm::InputTag("l1tEtSum"));
//   desc.add<bool>("useHT", true);
//   desc.add<unsigned>("nMu", 5);
//   desc.add<unsigned>("nEg", 5);
//   desc.add<unsigned>("nTau", 5);
//   desc.add<unsigned>("nJet", 5);
//   desc.add<std::string>("name", "L1TTopoBDT");
//   desc.add<edm::FileInPath>("model_path", "L1Trigger/TopoML/data/bdt_model.json");
  
//   descriptions.addWithDefaultLabel(desc);
// }

DEFINE_FWK_MODULE(L1TTopoBDTProducer);
