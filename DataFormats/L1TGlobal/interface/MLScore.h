#ifndef DataFormats_L1TGlobal_MLScore_h
#define DataFormats_L1TGlobal_MLScore_h

/**
* \class MLScore
*
*
* Description: L1 micro Global Trigger - Extra NN score emulation information for ML.
* 
*
* \author: Melissa Quinnan - UC San Diego
*
*
*/

// system include files
#include <vector>
#include <iostream>
#include <iomanip>

// user include files
#include "FWCore/Utilities/interface/typedefs.h"
#include "DataFormats/L1Trigger/interface/L1Candidate.h"
#include "DataFormats/L1Trigger/interface/BXVector.h"
#include "DataFormats/L1Trigger/interface/L1TObjComparison.h"

// forward declarations

// namespace l1t {
class MLScore;
typedef BXVector<MLScore> MLScoreBxCollection;

typedef l1t::ObjectRef<MLScore> MLScoreRef;
typedef l1t::ObjectRefBxCollection<MLScore> MLScoreRefBxCollection;
// typedef l1t::ObjectRefPair<MLScore> MLScoreRefPair;
// typedef l1t::ObjectRefPairBxCollection<MLScore> MLScoreRefPairBxCollection; //dont think pair part is needed

// class interface
class MLScore {
public:
  /// constructors
  MLScore();  //empty constructor

  MLScore(int bxInEvent);

  MLScore(int bxInEvent, float score);

  /// destructor
  virtual ~MLScore();

  ///set/get ml score and other simple members
  void setMLScore(float score) { mlscore_ = score; }
  void setbxInEventNr(int bxNr) { m_bxInEvent = bxNr; }

  inline float const& getMLScore() const { return mlscore_; }
  inline const int getbxInEventNr() const { return m_bxInEvent; }

  void reset();

private:
  /// bunch cross in the GT event record (E,F,0,1,2)
  int m_bxInEvent;

  //ml score value
  float mlscore_;

  //store version or type of network?
  // std::string nnversion;
};
//} l1t namespace
#endif /*DataFormats_L1TGlobal_MLScore_h*/
