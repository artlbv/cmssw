// FWCore includes
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Utilities/interface/ESGetToken.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

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

//============================================================
// L1 collections wrapper (zero-overhead)
//============================================================
struct L1Collections {
  const BXVector<l1t::Muon>&   mu;
  const BXVector<l1t::EGamma>& eg;
  const BXVector<l1t::Tau>&    tau;
  const BXVector<l1t::Jet>&    jet;
  const BXVector<l1t::EtSum>&  sum;
};

//============================================================
// Object reference (type-safe)
//============================================================
using ObjectRef = std::variant<
  std::monostate,
  const l1t::Muon*,
  const l1t::EGamma*,
  const l1t::Tau*,
  const l1t::Jet*,
  const l1t::EtSum*
>;

//============================================================
// Object getter function type
//============================================================
using ObjectGetterFn = ObjectRef (*)(
  int bx, unsigned idx,
  const L1Collections&
);

//============================================================
// Concrete object getters
//============================================================
static ObjectRef getMu(int bx, unsigned i, const L1Collections& c) {
  return c.mu.size(bx) > i ? ObjectRef(&c.mu.at(bx, i)) : ObjectRef{};
}

static ObjectRef getEG(int bx, unsigned i, const L1Collections& c) {
  return c.eg.size(bx) > i ? ObjectRef(&c.eg.at(bx, i)) : ObjectRef{};
}

static ObjectRef getTau(int bx, unsigned i, const L1Collections& c) {
  return c.tau.size(bx) > i ? ObjectRef(&c.tau.at(bx, i)) : ObjectRef{};
}

static ObjectRef getJet(int bx, unsigned i, const L1Collections& c) {
  return c.jet.size(bx) > i ? ObjectRef(&c.jet.at(bx, i)) : ObjectRef{};
}

static ObjectRef getHT(int bx, unsigned, const L1Collections& c) {
  for (unsigned i = 0; i < c.sum.size(bx); ++i) {
    if (c.sum.at(bx, i).getType() == l1t::EtSum::kTotalHt)
      return ObjectRef(&c.sum.at(bx, i));
  }
  return ObjectRef{};
}

//============================================================
// Variable visitors (NOT constexpr)
//============================================================
struct GetPt {
  float operator()(const l1t::Muon*   o) const { return o->pt(); }
  float operator()(const l1t::EGamma* o) const { return o->pt(); }
  float operator()(const l1t::Tau*    o) const { return o->pt(); }
  float operator()(const l1t::Jet*    o) const { return o->pt(); }
  float operator()(const l1t::EtSum*  o) const { return o->pt(); }
  float operator()(std::monostate)    const { return 0.f; }
};

struct GetHwIso {
  float operator()(const l1t::EGamma* o) const { return o->hwIso(); }
  float operator()(std::monostate)    const { return 0.f; }
  template<typename T> float operator()(const T*) const { return 0.f; }
};

struct GetHwQual {
  float operator()(const l1t::Muon* o) const { return o->hwQual(); }
  float operator()(std::monostate)  const { return 0.f; }
  template<typename T> float operator()(const T*) const { return 0.f; }
};

//============================================================
// Variable map (RESTORED)
//============================================================
using VarFn = float (*)(const ObjectRef&);

static float varPt(const ObjectRef& r)     { return std::visit(GetPt{}, r); }
static float varHwIso(const ObjectRef& r)  { return std::visit(GetHwIso{}, r); }
static float varHwQual(const ObjectRef& r) { return std::visit(GetHwQual{}, r); }

static const std::unordered_map<std::string, VarFn> kVarMap = {
  {"pt",     &varPt},
  {"hwIso",  &varHwIso},
  {"hwQual", &varHwQual}
};

//============================================================

class L1TTopoBDTProducer : public edm::stream::EDProducer<> {
public:
  explicit L1TTopoBDTProducer(const edm::ParameterSet& cfg);
  ~L1TTopoBDTProducer() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;

  // config parameters
  edm::EDGetTokenT<BXVector<l1t::Muon>> muToken_;
  edm::EDGetTokenT<BXVector<l1t::EGamma>> egToken_;
  edm::EDGetTokenT<BXVector<l1t::Tau>> tauToken_;
  edm::EDGetTokenT<BXVector<l1t::Jet>> jetToken_;
  edm::EDGetTokenT<BXVector<l1t::EtSum>> sumToken_;

  // std::string modelPath;
  int bx_;

  /// BDT model
  using BDT_t = conifer::BDT<float, float, true>;
  std::unique_ptr<BDT_t> bdt_;

  // feature accessors
  struct Feature {
    ObjectGetterFn getObj;
    VarFn          getVar;
    unsigned       index;
  };
  static const std::unordered_map<std::string, ObjectGetterFn> kObjectGetters_;

  std::vector<Feature> features_;
  unsigned nFeatures_;

};

//============================================================
// Object getter registry
//============================================================
const std::unordered_map<std::string, ObjectGetterFn>
L1TTopoBDTProducer::kObjectGetters_ = {
  {"L1Mu",  &getMu},
  {"L1EG",  &getEG},
  {"L1Tau", &getTau},
  {"L1Jet", &getJet},
  {"L1HT",  &getHT}
};

// =====================================================
// Constructor
// =====================================================

L1TTopoBDTProducer::L1TTopoBDTProducer(const edm::ParameterSet& cfg) {
  muToken_ = consumes<l1t::MuonBxCollection>(cfg.getParameter<edm::InputTag>("muToken"));
  egToken_ = consumes<l1t::EGammaBxCollection>(cfg.getParameter<edm::InputTag>("egToken"));
  tauToken_ = consumes<l1t::TauBxCollection>(cfg.getParameter<edm::InputTag>("tauToken"));
  jetToken_ = consumes<l1t::JetBxCollection>(cfg.getParameter<edm::InputTag>("jetToken"));
  sumToken_ = consumes<l1t::EtSumBxCollection>(cfg.getParameter<edm::InputTag>("etSumToken"));
  bx_ = cfg.getParameter<int>("bx");

  edm::FileInPath modelPath(cfg.getParameter<std::string>("model_path"));
  
  produces<float>("score");
  // produces<nanoaod::FlatTable>("scores");

  // ---- Load JSON: Model and feature names --------------------------------------------

  // print model path for debugging
  std::cout << "Loading BDT model from: " << modelPath.fullPath() << std::endl;

  // Load BDT model
  try {
    bdt_ = std::make_unique<BDT_t>(modelPath.fullPath());
  } catch (const std::exception& e) {
    throw cms::Exception("L1TTopoBDTProducer") << "Error loading BDT model from " << modelPath << ": " << e.what();
  }
  
  // read the model json to get feature names
  std::ifstream ifs(modelPath.fullPath());
  nlohmann::json json;
  ifs >> json;

  const auto& fmap = json.at("feature_map");
  nFeatures_ = fmap.size();
  features_.resize(nFeatures_);

  for (auto& [name, idx] : fmap.items()) {
    auto p1 = name.find('_');
    auto p2 = name.find('_', p1 + 1);

    std::string obj  = name.substr(0, p1);
    unsigned index   = std::stoi(name.substr(p1 + 1, p2 - p1 - 1));
    std::string var  = name.substr(p2 + 1);

    auto itObj = kObjectGetters_.find(obj);
    if (itObj == kObjectGetters_.end()) {
        throw cms::Exception("Configuration")
          << "Unknown object type in feature map: '" << obj
          << "' for feature '" << name << "'.\n"
          << "Available object types: ";
        for (const auto& kv : kObjectGetters_) std::cout << kv.first << " ";
        std::cout << "\nPlease prefix with L1 if needed (e.g. 'L1HT_0_pt').";
    }

    auto itVar = kVarMap.find(var);
    if (itVar == kVarMap.end()) {
        throw cms::Exception("Configuration")
          << "Unknown variable in feature map: '" << var
          << "' for feature '" << name << "'.\n"
          << "Available variable names: ";
        for (const auto& kv : kVarMap) std::cout << kv.first << " ";
        std::cout << "\n";
    }

    // assign safely
    auto og = itObj->second;
    auto vf = itVar->second;

    features_[idx] = {og, vf, index};
  }

  // print loaded features name, type and index for debugging
  std::cout << "Loaded features: " << std::endl;
  for (unsigned i = 0; i < features_.size(); ++i) {
    const auto& f = features_[i];
    std::string objName;
    for (const auto& [name, fn] : kObjectGetters_) {
      if (fn == f.getObj) {
        objName = name;
        break;
      }
    }
    std::string var;
    for (const auto& [name, fn] : kVarMap) {
      if (fn == f.getVar) {
        var = name;
        break;
      }
    }
    std::cout << "  Feature " << i << ": object type '" << objName << "', index " << f.index << ", variable '" << var << "'" << std::endl;
  }
}

L1TTopoBDTProducer::~L1TTopoBDTProducer() {}

void L1TTopoBDTProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  // get input collections
  // BXVector: first index is BX_, second index is object
  edm::Handle<BXVector<l1t::Muon>> muons;
  edm::Handle<BXVector<l1t::EGamma>> egammas;
  edm::Handle<BXVector<l1t::Tau>> taus;
  edm::Handle<BXVector<l1t::Jet>> jets;
  edm::Handle<BXVector<l1t::EtSum>> sums;
  iEvent.getByToken(muToken_, muons);
  iEvent.getByToken(egToken_, egammas);
  iEvent.getByToken(tauToken_, taus);
  iEvent.getByToken(jetToken_, jets);
  iEvent.getByToken(sumToken_, sums);

  L1Collections cols{*muons, *egammas, *taus, *jets, *sums};

  std::vector<float> features_x(nFeatures_, 0.f);

  for (unsigned i = 0; i < nFeatures_; ++i) {
    const auto& f = features_[i];
    ObjectRef ref = f.getObj(bx_, f.index, cols);
    features_x[i] = f.getVar(ref);
  }

  // print features for debugging
  std::cout << "Features: ";
  for (const auto& f : features_x) {
    std::cout << f << " ";
  } 
  std::cout << std::endl;

  std::vector<float> output = bdt_->decision_function(features_x);

  // print score
  std::cout << "BDT score: " << output.at(0) << std::endl;

  // store score in event
  iEvent.put(std::make_unique<float>(output.at(0)), "score");
  // iEvent.put(std::make_unique<float>(output.at(0)));
}

// make fillDescriptions

void L1TTopoBDTProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("muToken", edm::InputTag("l1tMuons"));
  desc.add<edm::InputTag>("egToken", edm::InputTag("l1tEGamma"));
  desc.add<edm::InputTag>("tauToken", edm::InputTag("l1tTau"));
  desc.add<edm::InputTag>("jetToken", edm::InputTag("l1tJet"));
  desc.add<edm::InputTag>("etSumToken", edm::InputTag("l1tEtSum"));
  desc.add<int>("bx", 0);
  desc.add<std::string>("model_path", "L1Trigger/TopoML/data/bdt_model.json");
  
  descriptions.addWithDefaultLabel(desc);
}

DEFINE_FWK_MODULE(L1TTopoBDTProducer);
