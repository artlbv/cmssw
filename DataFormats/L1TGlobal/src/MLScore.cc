/**
* \class MLScore
*
*
*
* \author: Melissa Quinnan -- UC San Diego
*
*
*/

// this class header
#include "DataFormats/L1TGlobal/interface/MLScore.h"

void MLScore::reset() {
  axoscore_ = 0.0;
  m_bxInEvent = 0;
}

MLScore::MLScore() { reset(); }

MLScore::MLScore(int bxInEvent) : m_bxInEvent(bxInEvent) { axoscore_ = 0.0; }

MLScore::MLScore(int bxInEvent, float score) : m_bxInEvent(bxInEvent), axoscore_(score) {}

//destructor
MLScore::~MLScore() {
  //empty
}
