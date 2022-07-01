#define _USE_MATH_DEFINES

#include <cmath>
#include <tuple>
#include <iostream>
#include <sstream>
#include "ROOT/RVec.hxx"

/** 
    Picks FatJet with
**/
int PickFatJet(RVec<float> FatJet_Xbb) {
  int nFatJets = FatJet_Xbb.size();
  float xbbScore = -1;

  std::vector<int> v(FatJet_Xbb.size());

  int fidx = -1;
  for (int i = 0; i < nFatJets; ++i) {
    if(FatJet_Xbb[i] > xbbScore){
      xbbScore = FatJet_Xbb[i];
      fidx = i;
    }
  }
  return fidx;
}

/**
   Checks for AK4 jets away from the AK8 jet.
   Returns index of AK4 jet w maximum btagging score and away from AK8 jet.
**/
int bjets(ROOT::Math::PtEtaPhiMVector FatJet,
	    RVec<ROOT::Math::PtEtaPhiMVector> Jet_vect,
	    RVec<float> Jet_bjetScore) {
  RVec<int> LoopIndex{}; /** Index that we actually want to loop over (ordered in real pt) */
  int nJets;
  std::vector<int> v(Jet_vect.size());
  nJets = Jet_vect.size(); // Set nJets
  std::iota (std::begin(v), std::end(v), 0);
  LoopIndex = v;
  
  // select jets away from FatJet
  float bjetScore = -1;
  int thisIdx;
  int bIdx = -1;
  for (int i = 0; i < nJets; ++i) {
    thisIdx = LoopIndex[i];
    if (hardware::DeltaR(FatJet,Jet_vect[thisIdx]) > 0.8) {
      if(Jet_bjetScore[thisIdx] > bjetScore) {
	bjetScore = Jet_bjetScore[thisIdx];
	bIdx = thisIdx;
      }
    }
  }
 
  return bIdx;
}

int MatchToGen(int pdgID, 
	       ROOT::Math::PtEtaPhiMVector obj,
	       RVec<ROOT::Math::PtEtaPhiMVector> GenPart_vect,
	       RVec<int> GenPart_pdgId,
	       float dR=0.8) {
  int idx=-1;
  for (int igp = 0; igp<GenPart_vect.size(); igp++) {
    if (abs(GenPart_pdgId[igp]) == pdgID) {
      if (hardware::DeltaR(obj,GenPart_vect[igp]) < dR) {
	idx=igp;
	break;
      }
    }
  }
  return idx;
}
