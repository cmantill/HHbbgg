import ROOT
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer
from TIMBER.Tools.Common import CompileCpp, OpenJSON, CutflowTxt, CutflowDict
from TIMBER.Tools.AutoPU import ApplyPU
from helpers import SplitUp

CompileCpp("TIMBER/Framework/include/common.h")
CompileCpp('HH_modules.cc')

class HHClass:
    def __init__(self,inputfile,year,ijob,njobs,mh=125,silent=False):
        if inputfile.endswith('.txt'): 
            infiles = SplitUp(inputfile, njobs)[ijob-1]
        else:
            infiles = inputfile
        # print(infiles)
        self.a = analyzer(infiles,silent=True)

        if inputfile.endswith('.txt'):
            self.setname = inputfile.split('/')[-1].split('_')[0]
        else:
            self.setname = inputfile.split('/')[-1].split('_')[1]
        self.year = year
        self.ijob = ijob
        self.njobs = njobs
        self.config = OpenJSON('HH_config.json')
        self.cuts = self.config['CUTS']
        self.mh = mh
        self.trigs = {
            16:[
                'HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90',
                # 'HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55',
            ],
            17:[
                'HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90','HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95',
                # 'HLT_Diphoton30_18_PVrealAND_R9Id_AND_IsoCaloId_AND_HE_R9Id_PixelVeto_Mass55','HLT_Diphoton30_18_PVrealAND_R9Id_AND_IsoCaloId_AND_HE_R9Id_NoPixelVeto_Mass55',
            ],
            18:[
                'HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90','HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95',
                # 'HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_NoPixelVeto_Mass55','HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_NoPixelVeto',
            ],
        }
        # HLT Diphoton30 18 R9IdL AND HE AN IsoCaloId NoPixelVeto not included in beginning of 2018
        if 'Data' in inputfile:
            self.a.isData = True
        else:
            self.a.isData = False

    def ApplyKinematicsSnap(self): # For snapshotting only
        self.a.Cut('flags',self.a.GetFlagString())
        self.a.Cut('nphotons',"nPhoton > 1")
        self.a.Cut('njets','nFatJet > 0')

        # fatjets
        # use v9 version of PN names
        self.a.Define('FatJet_Xbb','(FatJet_particleNetMD_Xbb/(1-FatJet_particleNetMD_Xcc-FatJet_particleNetMD_Xqq))')
        self.a.Define('FatJet_mreg','FatJet_particleNet_mass')

        # objects
        self.a.SubCollection('SelFatJet','FatJet', 
                             'FatJet_pt>250 && abs(FatJet_eta)<2.4 && FatJet_msoftdrop>50 && (FatJet_jetId & 2)')
        self.a.SubCollection('SelPhoton', 'Photon', 
                             'Photon_pt>20 && abs(Photon_eta)<2.5 && (abs(Photon_eta)<1.442 || abs(Photon_eta)>1.556) && Photon_r9>0.8 && Photon_sieie<0.035 && Photon_hoe<0.08 && Photon_mvaID>-0.9')
        self.a.SubCollection('SelJet','Jet', 'Jet_pt>30 && abs(Jet_eta)<2.5')
        self.a.SubCollection('SelElectron','Electron','Electron_pt>10 && ((abs(Electron_eta)<1.4442 || abs(Electron_eta)>1.566) && abs(Electron_eta)<2.5) && Electron_mvaFall17V2Iso_WP90 && abs(Electron_dxy) < 0.045 && abs(Electron_dz) < 0.2')
        self.a.SubCollection('SelMuon','Muon','Muon_pt>15 && abs(Muon_eta)<2.4 && abs(Muon_dxy) < 0.045 && abs(Muon_dz) < 0.2 && Muon_isGlobal && Muon_pfRelIso03_all < 0.3 && Muon_mediumId')

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
        self.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")
        diphoton_kin = 'SelPhoton_pt[0]>30 && abs(SelPhoton_eta[0])<2.5 && (abs(SelPhoton_eta[0])<1.442 || abs(SelPhoton_eta[0])>1.556) '
        diphoton_kin += ' && SelPhoton_r9[0]>0.8 && SelPhoton_sieie[0]<0.035 && SelPhoton_hoe[0]<0.08 && SelPhoton_mvaID[0]>-0.9'
        diphoton_kin += ' && SelPhoton_pt[1]>20 && abs(SelPhoton_eta[1])<2.5 && (abs(SelPhoton_eta[1])<1.442 || abs(SelPhoton_eta[1])>1.556)'
        diphoton_kin += ' && SelPhoton_r9[1]>0.8 && SelPhoton_sieie[1]<0.035 && SelPhoton_hoe[1]<0.08 && SelPhoton_mvaID[1]>-0.9'
        diphoton_kin += ' && (SelPhoton_pt[0]/mgg > 1/3) && (SelPhoton_pt[1]/mgg > 1/4)'
        self.a.Cut('diphoton_kin',diphoton_kin)
        self.a.Cut('diphoton_eveto', 'SelPhoton_electronVeto[0]==1 && SelPhoton_electronVeto[1]==1')

        # met
        self.a.Define('metpt', 'MET_pt')
        self.a.Define('metphi', 'MET_phi')

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
            'nSelElectron','SelElectron_pt','SelElectron_eta','SelElectron_phi',
            'nSelMuon','SelMuon_pt','SelMuon_eta','SelMuon_phi',
            'metpt','metphi',
            'event', 'eventWeight', 'luminosityBlock', 'run'
        ]

        if not self.a.isData:
            columns.extend(['genWeight'])
        self.a.SetActiveNode(node)
        self.a.Snapshot(columns,'HHsnapshot_%s_%s_%sof%s.root'%(self.setname,self.year,self.ijob,self.njobs),'Events',saveRunChain=True)
        self.a.SetActiveNode(startNode)

    def GetXsecScale(self):
        lumi = self.config['lumi%s'%self.year]
        if 'NMSSM' in self.setname or 'XHY-' in self.setname:
            xsec = 0.001
        else:
            xsec = self.config['XSECS'][self.setname]
        if self.a.genEventSumw == 0:
            raise ValueError('%s %s: genEventSumw is 0'%(self.setname, self.year))
        return lumi*xsec/self.a.genEventSumw

    def OpenForSelection(self):
        self.ApplyStandardCorrections(snapshot=False)
        return self.a.GetActiveNode()

    def GetCutflow(self,name="cutflow.txt"):
        CutflowTxt(name,self.a.GetActiveNode())

    def GetCutflowDict(self):
        return CutflowDict(self.a.GetActiveNode())

    def Selection(self,xbb_cut=0.9):
        self.OpenForSelection()
        try:
            self.a.Define('lead_photon', "hardware::TLvector(SelPhoton_pt[0],SelPhoton_eta[0],SelPhoton_phi[0],0)")
        except:
            print('no lead photon')
            exit(1)
        self.a.Define("sublead_photon", "hardware::TLvector(SelPhoton_pt[1],SelPhoton_eta[1],SelPhoton_phi[1],0)")
        self.a.Define("pt0", "SelPhoton_pt[0]")
        self.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")
        self.a.Define("pt0_over_mgg", "SelPhoton_pt[0]/mgg")
        self.a.Define("pt1_over_mgg", "SelPhoton_pt[1]/mgg")
        self.a.Define("p0_mva", "SelPhoton_mvaID[0]")
        self.a.Define("p1_mva", "SelPhoton_mvaID[1]")

        self.a.Define("fatjet", "hardware::TLvector(SelFatJet_pt[fatjet_index],SelFatJet_eta[fatjet_index],SelFatJet_phi[fatjet_index],SelFatJet_mreg[fatjet_index])")
        self.a.Define("ptj", "SelFatJet_pt[fatjet_index]")
        self.a.Define("mreg", "SelFatJet_mreg[fatjet_index]")
        self.a.Define("msd", "SelFatJet_msoftdrop[fatjet_index]")
        self.a.Define("pt0_over_mj", "SelFatJet_pt[fatjet_index]/mreg")

        self.a.Define('bjet', 'hardware::TLvector(SelJet_pt[JetAwayFatJet_index],SelJet_eta[JetAwayFatJet_index],SelJet_phi[JetAwayFatJet_index],SelJet_mass[JetAwayFatJet_index])')
        self.a.Define('deltaR_bjet_fatjet','hardware::DeltaR(fatjet,bjet)')
        self.a.Define("bscore_jetaway", "JetAwayFatJet_index>=0? SelJet_btagDeepFlavB[JetAwayFatJet_index]:2")

        self.a.Define('dr_fj_p0','hardware::DeltaR(lead_photon,fatjet)')
        self.a.Define('dr_fj_p1','hardware::DeltaR(sublead_photon,fatjet)')
        self.a.Define('dr_p0_p1','hardware::DeltaR(lead_photon,sublead_photon)')
        self.a.Define('dphi_p0_p1','hardware::DeltaPhi(SelPhoton_phi[0],SelPhoton_phi[1])')
        self.a.Define('deta_p0_p1','SelPhoton_eta[0]-SelPhoton_eta[1]')

        self.a.Define("met", "metpt")

        self.a.Define("invm", "hardware::InvariantMass({fatjet,lead_photon,sublead_photon})")
        self.a.Define("fourm", "invm-mreg-mgg+125+{0}".format(self.mh))
        self.a.Define("ptgg_over_inv", "(lead_photon+sublead_photon).Pt()/invm")
        self.a.Define("ptj_over_inv", "SelFatJet_pt[fatjet_index]/invm")
        
        # Both photons above 20 GeV
        self.a.Cut("pt_photons","SelPhoton_pt[0]>30&&SelPhoton_pt[1]>20")
        self.a.Cut("photonsawayjet", "dr_fj_p0>1. && dr_fj_p1>0.8")
        self.a.Cut("nobtagsaway", "bscore_jetaway < 0.340")

        # Final cuts
        self.a.Cut("SelFatJet_Xbb","SelFatJet_Xbb[0]>%.2f"%xbb_cut)
        self.a.Cut("mbb_window", "SelFatJet_msoftdrop[fatjet_index]>90 && SelFatJet_msoftdrop[fatjet_index]<140")

        # Weights        
        try:
            self.a.MakeWeightCols(extraNominal='' if self.a.isData else 'genWeight*%s'%self.GetXsecScale())
        except:
            print('no xsec for %s'%self.setname)
            exit(1)

    def TemplateSnapshot(self,output_dir,oname):
        self.a.Snapshot(["mreg","msd","deta_p0_p1","dphi_p0_p1","dr_p0_p1","mgg","fourm","weight__nominal",],
                        '%s/%s.root'%(output_dir,oname),
                        'Events',saveRunChain=False)
        
