#define _USE_MATH_DEFINES

#include <cmath>
#include <tuple>
#include "ROOT/RVec.hxx"

/**
   Checks for AK4 jets in opposite hemisphere than fixed AK8 jet.
   Returns btagging score of jet away from AK8 jet with highest b jet score.
**/
float hemispherize(float FatJet_phi, RVec<float> Jet_phi, RVec<float> Jet_bjetScore) {

  RVec<int> LoopIndex{}; /** Index that we actually want to loop over (ordered in real pt) */
  int nJets;
  std::vector<int> v(Jet_phi.size());
  nJets = Jet_phi.size(); // Set nJets
  std::iota (std::begin(v), std::end(v), 0);
  LoopIndex = v;
  
  // select jets away from FatJet
  float bjetScore = -1;
  int thisIdx;
  //int bIdx = -1;
  for (int i = 0; i < nJets; ++i) {
    thisIdx = LoopIndex[i];
    if (abs(ROOT::VecOps::DeltaPhi(FatJet_phi,Jet_phi[thisIdx])) > M_PI/2.0) {
      if(Jet_bjetScore[thisIdx] > bjetScore) {
	bjetScore = Jet_bjetScore[thisIdx];
	//bIdx = thisIdx;
      }
    }
  }
 
  return bjetScore;
}
