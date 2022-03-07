import ROOT
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer
from TIMBER.Tools.Common import CompileCpp, OpenJSON, CutflowTxt
from TIMBER.Tools.AutoPU import ApplyPU
from helpers import SplitUp

CompileCpp("TIMBER/Framework/include/common.h")
CompileCpp('btag.cc')

class HHClass:
    def __init__(self,inputfile,year,ijob,njobs,multiSampleStr='',pfnano=True):
        if inputfile.endswith('.txt'): 
            infiles = SplitUp(inputfile, njobs)[ijob-1]
        else:
            infiles = inputfile
        if multiSampleStr!='':
            self.multiSampleStr = multiSampleStr
            self.a = analyzer(infiles,multiSampleStr=multiSampleStr)
        else:
            self.multiSampleStr = None
            self.a = analyzer(infiles)

        if inputfile.endswith('.txt'):
            self.setname = inputfile.split('/')[-1].split('_')[0]
        else:
            self.setname = inputfile.split('/')[-1].split('_')[1]
        self.year = year
        self.ijob = ijob
        self.njobs = njobs
        self.config = OpenJSON('HHConfig.json')
        self.cuts = self.config['CUTS']
        self.mh = 125
        self.trigs = {
            16:['HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90'],
            17:['HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90'],
            18:['HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90'],
        }
        if 'Data' in inputfile:
            self.a.isData = True
        else:
            self.a.isData = False
        self.pfnano = pfnano

    def ApplyKinematicsSnap(self): # For snapshotting only
        self.a.Cut('flags',self.a.GetFlagString())
        self.a.Cut('n_photon',"nPhoton > 1")
        self.a.Cut('njets','nFatJet > 0')

        self.a.Define('lead_photon', "hardware::TLvector(Photon_pt[0],Photon_eta[0],Photon_phi[0],0)")
        self.a.Define('sublead_photon', "hardware::TLvector(Photon_pt[1],Photon_eta[1],Photon_phi[1],0)")
        self.a.Define('lead_fatjet', "hardware::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_mass[0])")

        self.a.Define('jetaway_bscore', 'hemispherize(FatJet_pt[0], Jet_phi, Jet_btagDeepFlavB)')

        self.a.Define('deltaR_fatjet_photon0','hardware::DeltaR(lead_photon,lead_fatjet)')
        self.a.Define('deltaR_fatjet_photon1','hardware::DeltaR(sublead_photon,lead_fatjet)')
        self.a.Cut('photon0_away',"deltaR_fatjet_photon0>0.4")
        self.a.Cut('photon1_away',"deltaR_fatjet_photon1>0.4")
        self.a.Cut('photon0_pt','Photon_pt[0]>30 && abs(Photon_eta[0])<2.5 && (abs(Photon_eta[0])<1.442 || abs(Photon_eta[0])>1.556) && Photon_r9[0]>0.8 && Photon_sieie[0]<0.035 && Photon_hoe[0]<0.08 && Photon_mvaID[0]>-0.9')
        self.a.Cut('photon1_pt','Photon_pt[1]>20 && abs(Photon_eta[1])<2.5 && (abs(Photon_eta[1])<1.442 || abs(Photon_eta[1])>1.556) && Photon_r9[1]>0.8 && Photon_sieie[1]<0.035 && Photon_hoe[1]<0.08 && Photon_mvaID[1]>-0.9')

        if self.pfnano:
            self.a.Cut('fatjet_pt','FatJet_pt[0]>250 && abs(FatJet_eta[0])<2.4 && FatJet_msoftdrop[0]>50 && (FatJet_particleNetMD_Xbb[0]/(1-FatJet_particleNetMD_Xcc[0]-FatJet_particleNetMD_Xqq[0]))>{0}'.format(self.cuts['XbbvsQCD']))
            self.a.SubCollection('SelFatJet','FatJet', 'FatJet_pt>250 && abs(FatJet_eta)<2.4 && FatJet_msoftdrop>50 && (FatJet_particleNetMD_Xbb/(1-FatJet_particleNetMD_Xcc-FatJet_particleNetMD_Xqq))>{0}'.format(self.cuts['XbbvsQCD']))
            self.a.Define('SelFatJet_Xbb','(SelFatJet_particleNetMD_Xbb/(1-SelFatJet_particleNetMD_Xcc-SelFatJet_particleNetMD_Xqq))')
        else:
            self.a.Cut('fatjet_pt','FatJet_pt[0]>250 && abs(FatJet_eta[0])<2.4 && FatJet_msoftdrop[0]>50 && (FatJet_ParticleNetMD_probXbb[0]/(1-FatJet_ParticleNetMD_probXcc[0]-FatJet_ParticleNetMD_probXqq[0]))>{0}'.format(self.cuts['XbbvsQCD']))
            self.a.SubCollection('SelFatJet','FatJet', 'FatJet_pt>250 && abs(FatJet_eta)<2.4 && FatJet_msoftdrop>50 && (FatJet_ParticleNetMD_probXbb/(1-FatJet_ParticleNetMD_probXcc-FatJet_ParticleNetMD_probXqq))>{0}'.format(self.cuts['XbbvsQCD']))
            self.a.Define('SelFatJet_Xbb','(SelFatJet_ParticleNetMD_probXbb/(1-SelFatJet_ParticleNetMD_probXcc-SelFatJet_ParticleNetMD_probXqq))')
        self.a.Define('SelFatJet_awaybjet', 'jetaway_bscore')

        self.a.SubCollection('SelPhoton', 'Photon', 'Photon_pt>20 && abs(Photon_eta)<2.5 && (abs(Photon_eta)<1.442 || abs(Photon_eta)>1.556) && Photon_r9>0.8 && Photon_sieie<0.035 && Photon_hoe<0.08 && Photon_mvaID>-0.9')

        if self.multiSampleStr:
            self.a.Cut('genymass', 'GenModel_YMass_%s==1'%self.multiSampleStr)
        return self.a.GetActiveNode()

    def ApplyStandardCorrections(self,snapshot=False):
        if snapshot:
            if self.a.isData:
                lumiFilter = ModuleWorker('LumiFilter','TIMBER/Framework/include/LumiFilter.h',[self.year])
                self.a.Cut('lumiFilter',lumiFilter.GetCall(evalArgs={"lumi":"luminosityBlock"}))
            self.a.MakeWeightCols(extraNominal='genWeight' if not self.a.isData else '')                
        return self.a.GetActiveNode()

    def Snapshot(self,node=None):
        startNode = self.a.GetActiveNode()
        if node == None: node = self.a.GetActiveNode()

        columns = [
            'SelFatJet_pt','SelFatJet_msoftdrop','SelFatJet_eta','SelFatJet_phi','SelFatJet_mass','SelFatJet_Xbb',
            'SelFatJet_awaybjet',
            'SelPhoton_pt','SelPhoton_eta','SelPhoton_phi','SelPhoton_mvaID','SelPhoton_energyErr',
            'HLT_Diphoton*',
            'MET_pt','MET_phi',
            'event', 'eventWeight', 'luminosityBlock', 'run'
        ]

        if not self.a.isData:
            columns.extend(['genWeight'])
        self.a.SetActiveNode(node)
        if self.multiSampleStr:
            self.a.Snapshot(columns,'HHsnapshot_%sMY%s_%s_%sof%s.root'%(self.setname,self.multiSampleStr,self.year,self.ijob,self.njobs),'Events',saveRunChain=True)
        else:
            self.a.Snapshot(columns,'HHsnapshot_%s_%s_%sof%s.root'%(self.setname,self.year,self.ijob,self.njobs),'Events',saveRunChain=True)
        self.a.SetActiveNode(startNode)

    def GetXsecScale(self):
        lumi = self.config['lumi%s'%self.year]
        xsec = self.config['XSECS'][self.setname]
        print(self.a.genEventSumw)
        if self.a.genEventSumw == 0:
            #print('%s %s: genEventSumw is 0'%(self.setname, self.year)))
            #return 0
            raise ValueError('%s %s: genEventSumw is 0'%(self.setname, self.year))
        return lumi*xsec/self.a.genEventSumw

    def OpenForSelection(self):
        self.ApplyStandardCorrections(snapshot=False)
        return self.a.GetActiveNode()

    def GetCutflow(self,name):
        CutflowTxt("text",self.a.GetActiveNode())
