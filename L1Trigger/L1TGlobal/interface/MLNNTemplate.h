#ifndef L1Trigger_L1TGlobal_MLNNTemplate_h
#define L1Trigger_L1TGlobal_MLNNTemplate_h

/**
 * \class MLNNTemplate
 *
 *
 * Description: L1 Global Trigger MLNN template.
 *
 * \author: Melissa Quinnan (UC San Diego)
 *
 */

// system include files
#include <string>
#include <iosfwd>

// user include files

//   base class
#include "L1Trigger/L1TGlobal/interface/GlobalCondition.h"

// forward declarations

// class declaration
class MLNNTemplate : public GlobalCondition {
public:
  // constructor
  MLNNTemplate();

  // constructor
  MLNNTemplate(const std::string&);

  // constructor
  MLNNTemplate(const std::string&, const l1t::GtConditionType&);

  // copy constructor
  MLNNTemplate(const MLNNTemplate&);

  // destructor
  ~MLNNTemplate() override;

  // assign operator
  MLNNTemplate& operator=(const MLNNTemplate&);

  // typedef for a single object template
  struct ObjectParameter {
    int minMLNNThreshold;
    int maxMLNNThreshold;
  };

public:
  inline const std::vector<ObjectParameter>* objectParameter() const { return &m_objectParameter; }

  inline const std::string& modelVersion() const { return m_modelVersion; }

  /// set functions
  void setConditionParameter(const std::vector<ObjectParameter>& objParameter);

  void setModelVersion(const std::string& modelversion);

  /// print the condition
  void print(std::ostream& myCout) const override;

  /// output stream operator
  friend std::ostream& operator<<(std::ostream&, const MLNNTemplate&);

private:
  /// copy function for copy constructor and operator=
  void copy(const MLNNTemplate& cp);

  /// variables containing the parameters
  std::vector<ObjectParameter> m_objectParameter;

  /// model version
  std::string m_modelVersion;
};

#endif
