import ROOT
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer
from TIMBER.Tools.Common import CompileCpp, OpenJSON, CutflowTxt, CutflowDict
from TIMBER.Tools.AutoPU import ApplyPU
from helpers import SplitUp

CompileCpp("TIMBER/Framework/include/common.h")
CompileCpp('HHmodules.cc')

class HHClass:
    def __init__(self,inputfile,year,ijob,njobs,multiSampleStr='',pfnano=True):
        if inputfile.endswith('.txt'): 
            infiles = SplitUp(inputfile, njobs)[ijob-1]
        else:
            infiles = inputfile
        print(infiles)
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
        self.a.Cut('nphotons',"nPhoton > 1")
        self.a.Cut('njets','nFatJet > 0')

        # fatjets
        if self.pfnano:
            self.a.Define('FatJet_Xbb','(FatJet_particleNetMD_Xbb/(1-FatJet_particleNetMD_Xcc-FatJet_particleNetMD_Xqq))')
            try:
                self.a.Define('FatJet_mreg','FatJet_particleNet_mass')
            except: 
                self.a.Define('FatJet_mreg', 'FatJet_msoftdrop')
        else:
            self.a.Define('FatJet_Xbb','(FatJet_ParticleNetMD_probXbb/(1-FatJet_ParticleNetMD_probXcc-FatJet_ParticleNetMD_probXqq))')
            self.a.Define('FatJet_mreg','FatJet_msoftdrop')

        # objects
        self.a.SubCollection('SelFatJet','FatJet', 'FatJet_pt>250 && abs(FatJet_eta)<2.4 && FatJet_msoftdrop>50 && (FatJet_jetId & 2)')
        self.a.SubCollection('SelPhoton', 'Photon', 'Photon_pt>20 && abs(Photon_eta)<2.5 && (abs(Photon_eta)<1.442 || abs(Photon_eta)>1.556) && Photon_r9>0.8 && Photon_sieie<0.035 && Photon_hoe<0.08 && Photon_mvaID>-0.9')
        self.a.SubCollection('SelJet','Jet', 'Jet_pt>30 && abs(Jet_eta)<2.5')

        # pick fatjet
        self.a.Define('fatjet_index','PickFatJet(SelFatJet_Xbb)')
        self.a.Define('fatjet', "hardware::TLvector(SelFatJet_pt[fatjet_index],SelFatJet_eta[fatjet_index],SelFatJet_phi[fatjet_index],SelFatJet_msoftdrop[fatjet_index])")
        self.a.Cut('fatjet_kin','fatjet_index>=0')
        self.a.Cut('fatjet_xbb','SelFatJet_Xbb[fatjet_index]>{0}'.format(self.cuts['XbbvsQCD']))

        # jets
        self.a.Define('jets', "hardware::TLvector(SelJet_pt,SelJet_eta,SelJet_phi,SelJet_mass)")
        self.a.Define('JetAwayFatJet_index', 'bjets(fatjet, jets, SelJet_btagDeepFlavB)')

        # photons
        self.a.Define('lead_photon', "hardware::TLvector(SelPhoton_pt[0],SelPhoton_eta[0],SelPhoton_phi[0],0)")
        self.a.Define('sublead_photon', "hardware::TLvector(SelPhoton_pt[1],SelPhoton_eta[1],SelPhoton_phi[1],0)")
        diphoton_kin = 'SelPhoton_pt[0]>30 && abs(SelPhoton_eta[0])<2.5 && (abs(SelPhoton_eta[0])<1.442 || abs(SelPhoton_eta[0])>1.556) '
        diphoton_kin += ' && SelPhoton_r9[0]>0.8 && SelPhoton_sieie[0]<0.035 && SelPhoton_hoe[0]<0.08 && SelPhoton_mvaID[0]>-0.9'
        diphoton_kin += ' && SelPhoton_pt[1]>20 && abs(SelPhoton_eta[1])<2.5 && (abs(SelPhoton_eta[1])<1.442 || abs(SelPhoton_eta[1])>1.556)'
        diphoton_kin += ' && SelPhoton_r9[1]>0.8 && SelPhoton_sieie[1]<0.035 && SelPhoton_hoe[1]<0.08 && SelPhoton_mvaID[1]>-0.9'
        self.a.Cut('diphoton_kin',diphoton_kin)
        self.a.Cut('diphoton_eveto', 'SelPhoton_electronVeto[0]==1 && SelPhoton_electronVeto[1]==1')
        self.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")
        self.a.Cut("ptphoton_over_mgg", "(SelPhoton_pt[0]/mgg > 1/3) && (SelPhoton_pt[1]/mgg > 1/4)")

        # electrons and muons
        #self.a.SubCollection('electrons', 'Electron', "Electron_pt>10 && ((abs(Electron_eta)<1.4442 || abs(Electron_eta)>1.566) && abs(Electron_eta)<2.5)")
        #self.a.SubCollection('muons', 'Muon', "Muon_pt>10 && abs(Muon_eta)<2.5")

        # met
        self.a.Define('metpt', 'MET_pt')
        self.a.Define('metphi', 'MET_phi')
        self.a.Cut("metcut", "MET_pt < 150")

        if self.multiSampleStr:
            self.a.Cut('genymass', 'GenModel_YMass_%s==1'%self.multiSampleStr)
        return self.a.GetActiveNode()

    def ApplyGen(self):
        # gen part
        self.a.Define('GenPart_vect','hardware::TLvector(GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass)')
        self.a.Define('GenMatchHJet_idx','MatchToGen(25, fatjet, GenPart_vect, GenPart_pdgId)')
        self.a.Define('GenMatchTopJet_idx','MatchToGen(6, fatjet, GenPart_vect, GenPart_pdgId)')
        self.a.Define('GenMatchTopPhoton_idx','MatchToGen(6, lead_photon, GenPart_vect, GenPart_pdgId, 0.4)')
        self.a.Define('GenMatchBPhoton_idx','MatchToGen(5, lead_photon, GenPart_vect, GenPart_pdgId, 0.4)')
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
            'SelFatJet_pt','SelFatJet_msoftdrop','SelFatJet_mreg','SelFatJet_eta','SelFatJet_phi','SelFatJet_mass','SelFatJet_Xbb',
            'fatjet_index',
            'GenPart*',
            'SelJet_pt','SelJet_eta','SelJet_phi','SelJet_mass','SelJet_btagDeepFlavB',
            'JetAwayFatJet_index',
            'SelPhoton_pt','SelPhoton_eta','SelPhoton_phi','SelPhoton_mvaID','SelPhoton_energyErr',
            'HLT_Diphoton*',
            #'nElectron','nMuon',
            'metpt','metphi',
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

    def GetCutflow(self,name="cutflow.txt"):
        CutflowTxt(name,self.a.GetActiveNode())

    def GetCutflowDict(self):
        return CutflowDict(self.a.GetActiveNode())
