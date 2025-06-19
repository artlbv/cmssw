// this class header
#include "L1Trigger/L1TGlobal/interface/MLNNTemplate.h"

// system include files
#include <iostream>
#include <iomanip>

MLNNTemplate::MLNNTemplate() : GlobalCondition() { m_condCategory = l1t::CondMLNN; }

MLNNTemplate::MLNNTemplate(const std::string& cName) : GlobalCondition(cName) {
  m_condCategory = l1t::CondMLNN;
}

MLNNTemplate::MLNNTemplate(const std::string& cName, const l1t::GtConditionType& cType)  //not sure we need cType
    : GlobalCondition(cName, l1t::CondMLNN, cType) {
  int nObjects = nrObjects();

  if (nObjects > 0) {
    m_objectType.reserve(nObjects);
  }
}

// copy constructor
MLNNTemplate::MLNNTemplate(const MLNNTemplate& cp) : GlobalCondition(cp.m_condName) { copy(cp); }

// destructor
MLNNTemplate::~MLNNTemplate() {
  // empty now
}

// assign operator
MLNNTemplate& MLNNTemplate::operator=(const MLNNTemplate& cp) {
  copy(cp);
  return *this;
}

// setConditionParameter - set the parameters of the condition
void MLNNTemplate::setConditionParameter(const std::vector<ObjectParameter>& objParameter) {
  m_objectParameter = objParameter;
}

//setModelVersion - set the model version of the condition
void MLNNTemplate::setModelVersion(const std::string& modelversion) { m_modelVersion = modelversion; }

void MLNNTemplate::print(std::ostream& myCout) const {
  myCout << "\n  MLNNTemplate print..." << std::endl;

  GlobalCondition::print(myCout);

  int nObjects = nrObjects();

  for (int i = 0; i < nObjects; i++) {
    myCout << std::endl;
    myCout << "  Template for object " << i << " [ hex ]" << std::endl;
    myCout << "    MLNNThreshold   = " << std::hex << m_objectParameter[i].minMLNNThreshold << std::endl;
  }

  // reset to decimal output
  myCout << std::dec << std::endl;
}

void MLNNTemplate::copy(const MLNNTemplate& cp) {
  m_condName = cp.condName();
  m_condCategory = cp.condCategory();
  m_condType = cp.condType();
  m_objectType = cp.objectType();  //not needed for MLNN
  m_condGEq = cp.condGEq();
  m_condChipNr = cp.condChipNr();
  m_condRelativeBx = cp.condRelativeBx();

  m_modelVersion = cp.modelVersion();  // new for utm 0.12.0
  m_objectParameter = *(cp.objectParameter());
}

// output stream operator
std::ostream& operator<<(std::ostream& os, const MLNNTemplate& result) {
  result.print(os);
  return os;
}
