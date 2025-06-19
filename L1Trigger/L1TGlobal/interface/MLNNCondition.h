#ifndef L1Trigger_L1TGlobal_MLNNCondition_h
#define L1Trigger_L1TGlobal_MLNNCondition_h

/**
 * \class MLNNCondition
 *
 * Description: evaluation of a CondMLNN condition.
 */

#include <iosfwd>
#include <string>
#include <utility>

#include "L1Trigger/L1TGlobal/interface/ConditionEvaluation.h"
#include "DataFormats/L1Trigger/interface/L1Candidate.h"

#include "hls4ml/emulator.h"

// forward declarations
class GlobalCondition;
class MLNNTemplate;

namespace l1t {

  class L1Candidate;
  class GlobalBoard;

  // class declaration
  class MLNNCondition : public ConditionEvaluation {
  public:
    /// constructors
    ///     default
    MLNNCondition();

    ///     from base template condition (from event setup usually)
    MLNNCondition(const GlobalCondition*, const GlobalBoard*);

    // copy constructor
    MLNNCondition(const MLNNCondition&);
    // destructor
    ~MLNNCondition() override;

    // assign operator
    MLNNCondition& operator=(const MLNNCondition&);

    /// the core function to check if the condition matches
    const bool evaluateCondition(const int bxEval) const override;

    /// print condition
    void print(std::ostream& myCout) const override;

    ///   get / set the pointer to a Condition
    inline const MLNNTemplate* gtMLNNTemplate() const { return m_gtMLNNTemplate; }

    void setGtMLNNTemplate(const MLNNTemplate*);

    ///   get / set the pointer to GTL
    inline const GlobalBoard* gtGTB() const { return m_gtGTB; }

    void setuGtB(const GlobalBoard*);

    /// get/set score value
    void setScore(const float scoreval) const;

    inline float getScore() const { return m_savedscore; }

    void loadModel();

    inline hls4mlEmulator::ModelLoader const& model_loader() const { return m_model_loader; }

  private:
    /// copy function for copy constructor and operator=
    void copy(const MLNNCondition& cp);

    /// pointer to a MLNNTemplate
    const MLNNTemplate* m_gtMLNNTemplate;

    /// pointer to uGt GlobalBoard, to be able to get the trigger objects
    const GlobalBoard* m_gtGTB;

    static constexpr char const* kModelNamePrefix = "";

    // NN models based on hls4ml
    hls4mlEmulator::ModelLoader m_model_loader;
    std::shared_ptr<hls4mlEmulator::Model> m_model;

    // BDT models based on conifer
    // typedef ap_fixed<21, 12, AP_RND_CONV, AP_SAT> bdt_feature_t;
    // typedef ap_fixed<12, 3, AP_RND_CONV, AP_SAT> bdt_score_t;
    // std::unique_ptr<conifer::BDT<bdt_feature_t, bdt_score_t, false>> model_;

    ///mlnn score for possible score saving
    mutable float m_savedscore;
  };

}  // namespace l1t
#endif
