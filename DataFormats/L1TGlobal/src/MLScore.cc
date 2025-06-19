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
  mlscore_ = 0.0;
  m_bxInEvent = 0;
}

MLScore::MLScore() { reset(); }

MLScore::MLScore(int bxInEvent) : m_bxInEvent(bxInEvent) { mlscore_ = 0.0; }

MLScore::MLScore(int bxInEvent, float score) : m_bxInEvent(bxInEvent), mlscore_(score) {}

//destructor
MLScore::~MLScore() {
  //empty
}
