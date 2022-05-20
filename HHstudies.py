import ROOT, time

from TIMBER.Analyzer import HistGroup, Correction
from TIMBER.Tools.Common import CompileCpp
ROOT.gROOT.SetBatch(True)

import os

from HHClass import HHClass
from collections import OrderedDict

# Not for use with data
def HHstudies(args):
    print ('PROCESSING: %s %s'%(args.setname, args.era))
    ROOT.ROOT.EnableImplicitMT(args.threads)
    os.system('mkdir -p selfiles/%s'%args.tag)
    os.system('mkdir -p rootfiles/%s'%args.tag)
    os.system('mkdir -p gg_cutflow/%s'%args.tag)

    start = time.time()
    # Base setup
    selection = HHClass('gg_nano/%s_%s_snapshot.txt'%(args.setname,args.era),int(args.era),1,1,args.samplestr)
    selection.OpenForSelection()
    
    try:
        selection.a.Define('lead_photon', "hardware::TLvector(SelPhoton_pt[0],SelPhoton_eta[0],SelPhoton_phi[0],0)")
    except:
        print('no lead photon')
        exit(1)

    selection.a.Define("sublead_photon", "hardware::TLvector(SelPhoton_pt[1],SelPhoton_eta[1],SelPhoton_phi[1],0)")
    selection.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")
    selection.a.Define("fatjet", "hardware::TLvector(SelFatJet_pt[fatjet_index],SelFatJet_eta[fatjet_index],SelFatJet_phi[fatjet_index],SelFatJet_msoftdrop[fatjet_index])")
    selection.a.Define('bjet', 'hardware::TLvector(SelJet_pt[JetAwayFatJet_index],SelJet_eta[JetAwayFatJet_index],SelJet_phi[JetAwayFatJet_index],SelJet_mass[JetAwayFatJet_index])')

    selection.a.Define('deltaR_bjet_fatjet','hardware::DeltaR(fatjet,bjet)')
    selection.a.Define("bscore_jetaway", "JetAwayFatJet_index>=0? SelJet_btagDeepFlavB[JetAwayFatJet_index]:2")
    selection.a.Define('dr_fj_p0','hardware::DeltaR(lead_photon,fatjet)')
    selection.a.Define('dr_fj_p1','hardware::DeltaR(sublead_photon,fatjet)')
    selection.a.Define('dr_p0_p1','hardware::DeltaR(lead_photon,sublead_photon)')
    selection.a.Define('dphi_p0_p1','hardware::DeltaPhi(SelPhoton_phi[0],SelPhoton_phi[1])')
    selection.a.Define('deta_p0_p1','SelPhoton_eta[0]-SelPhoton_eta[1]')
    selection.a.Define("met", "metpt")
    selection.a.Define("pt0_over_mgg", "SelPhoton_pt[0]/mgg")
    selection.a.Define("pt1_over_mgg", "SelPhoton_pt[1]/mgg")
    selection.a.Define("p0_mva", "SelPhoton_mvaID[0]")
    selection.a.Define("p1_mva", "SelPhoton_mvaID[1]")
    selection.a.Define("ptj", "SelFatJet_pt[fatjet_index]")
    selection.a.Define("pt0", "SelPhoton_pt[0]")
    # selection.a.Define("mreg", "SelFatJet_mreg[fatjet_index]")
    selection.a.Define("mjet", "SelFatJet_msoftdrop[fatjet_index]")
    selection.a.Define("invm", "hardware::InvariantMass({fatjet,lead_photon,sublead_photon})")
    selection.a.Define("redm", "invm-mjet-mgg+{0}".format(selection.mh))
    selection.a.Define("pt0_over_mj", "SelFatJet_pt[fatjet_index]/mjet")
    selection.a.Define("ptgg_over_inv", "(lead_photon+sublead_photon).Pt()/invm")
    selection.a.Define("ptj_over_inv", "SelFatJet_pt[fatjet_index]/invm")
        
    selection.a.Cut("photonsawayjet", "dr_fj_p0>1. && dr_fj_p1>0.8")
    selection.a.Cut("nobtagsaway", "bscore_jetaway < 0.340")
    selection.a.Cut("SelFatJet_Xbb_tight","SelFatJet_Xbb[0]>0.9")
    
    #if selection.a.isData:
    # selection.a.Cut("mbb_veto", "SelFatJet_mreg[fatjet_index]<90 || SelFatJet_mreg[fatjet_index]>150")
    #selection.a.Cut("mbb_veto", "SelFatJet_msoftdrop[fatjet_index]<90 || SelFatJet_msoftdrop[fatjet_index]>150")

    selection.a.Cut("mbb_window", "SelFatJet_msoftdrop[fatjet_index]>90 && SelFatJet_msoftdrop[fatjet_index]<150")
    if selection.a.isData:
        selection.a.Cut("mgg_veto", "(mgg < %s) || (mgg > %s)"%(args.mass-20,args.mass+20))

    #else:
    # selection.a.Cut("mbb_window", "SelFatJet_mreg[fatjet_index]>90 && SelFatJet_mreg[fatjet_index]<150")
    #selection.a.Cut("mbb_window", "SelFatJet_msoftdrop[fatjet_index]>90 && SelFatJet_msoftdrop[fatjet_index]<150")

    try:
        selection.a.MakeWeightCols(extraNominal='' if selection.a.isData else 'genWeight*%s'%selection.GetXsecScale())
    except:
        print('no xsec')
        exit(1)
        
    selection.a.Snapshot(["mjet","deta_p0_p1","dphi_p0_p1","dr_p0_p1","mgg","weight__nominal",],'selfiles/%s/%s_%s.root'%(args.tag,args.setname,args.era),'Events',saveRunChain=False)
    
    # Kinematic plots
    kinPlots = HistGroup('kinPlots')
    kinPlots.Add('mgg',selection.a.DataFrame.Histo1D(('mgg',';M_{#gamma#gamma} [GeV];Events',100,40,450),'mgg','weight__nominal'))
    kinPlots.Add('pt0',selection.a.DataFrame.Histo1D(('pt0',r';p_{T}(#gamma_{0}) [GeV];Events',60,30,500),'pt0','weight__nominal'))
    kinPlots.Add('pt0_over_mgg',selection.a.DataFrame.Histo1D(('pt0_over_mgg',';p_{T}(#gamma^{1})/M_{#gamma#gamma};Events',40,0,6),'pt0_over_mgg','weight__nominal'))
    kinPlots.Add('pt1_over_mgg',selection.a.DataFrame.Histo1D(('pt1_over_mgg',';p_{T}(#gamma^{2})/M_{#gamma#gamma};Events',40,0,6),'pt1_over_mgg','weight__nominal'))
    kinPlots.Add('dr_p0_p1',selection.a.DataFrame.Histo1D(('dr_p0_p1',';#Delta R(#gamma_{0},#gamma_{1});Events',40,0,2),'dr_p0_p1','weight__nominal'))
    kinPlots.Add('invm',selection.a.DataFrame.Histo1D(('invm',';M_{j#gamma#gamma} [GeV];Events',60,100,1400),'invm','weight__nominal'))
    kinPlots.Add('redm',selection.a.DataFrame.Histo1D(('redm',';M_{j#gamma#gamma}-M_{j}-M_{#gamma#gamma}+M_{H};Events',60,0,2000),'redm','weight__nominal'))
    kinPlots.Add('ptj',selection.a.DataFrame.Histo1D(('ptj',r';p_{T}(j) [GeV];Events',60,250,1000),'ptj','weight__nominal'))
    kinPlots.Add('met',selection.a.DataFrame.Histo1D(('met',r';MET [GeV];Events',60,0,150),'met','weight__nominal'))
    kinPlots.Add('mjet',selection.a.DataFrame.Histo1D(('mjet',r';m_{SD}(j) [GeV];Events',60,50,250),'mjet','weight__nominal'))
    kinPlots.Add('ptgg_over_inv',selection.a.DataFrame.Histo1D(('ptgg_over_inv',r';p_{T}(#gamma#gamma)/M_{X};Events',30,0,2),'ptgg_over_inv','weight__nominal'))
    kinPlots.Add('ptj_over_inv',selection.a.DataFrame.Histo1D(('ptj_over_inv',r';p_{T}(j)/M_{X};Events',30,0,3),'ptj_over_inv','weight__nominal'))
    kinPlots.Add('pt0_over_mj',selection.a.DataFrame.Histo1D(('pt0_over_mj',r';p_{T}(j)/m_{SD};Events',30,1.5,8),'pt0_over_mj','weight__nominal'))
    kinPlots.Add('bscore_jetaway',selection.a.DataFrame.Histo1D(('bscore_jetaway',r';Jet.btagDeep;Events',30,0,1),'bscore_jetaway','weight__nominal'))
    kinPlots.Add('dr_fj_p0',selection.a.DataFrame.Histo1D(('dr_fj_p0',r';#Delta R(fj,#gamma^0);Events',30,0.,4),'dr_fj_p0','weight__nominal'))
    kinPlots.Add('dr_fj_p1',selection.a.DataFrame.Histo1D(('dr_fj_p1',r';#Delta R(fj,#gamma^1);Events',30,0.,4),'dr_fj_p1','weight__nominal'))
    kinPlots.Add('deta_p0_p1',selection.a.DataFrame.Histo1D(('deta_p0_p1',r';#Delta#eta(#gamma_{0},#gamma_{1});Events',40,-5,5),'deta_p0_p1','weight__nominal'))
    kinPlots.Add('dphi_p0_p1',selection.a.DataFrame.Histo1D(('dphi_p0_p1',r';#Delta#phi(#gamma_{0},#gamma_{1});Events',40,-5,5),'dphi_p0_p1','weight__nominal'))
    kinPlots.Add('p0_mva',selection.a.DataFrame.Histo1D(('p0_mva',r';MVA #gamma_{0};Events',40,-1,1),'p0_mva','weight__nominal'))
    kinPlots.Add('p1_mva',selection.a.DataFrame.Histo1D(('p1_mva',r';MVA #gamma_{0};Events',40,-1,1),'p1_mva','weight__nominal'))
    #kinPlots.Add('deltaR_bjet_fatjet',selection.a.DataFrame.Histo1D(('deltaR_bjet_fatjet',r';#Delta R(b-jet,fj);Events',30,0.,4),'deltaR_bjet_fatjet','weight__nominal'))

    out = ROOT.TFile.Open('rootfiles/%s/HHstudies_%s_%s.root'%(args.tag,args.setname,args.era),'RECREATE')
    out.cd()
    kinPlots.Do('Write')

    import json
    fcutflow_old = "gg_cutflow/%s_%s_cutflow.txt"%(args.setname, args.era)
    old_dict = json.load(open(fcutflow_old), object_pairs_hook=OrderedDict)
    for key,v in selection.GetCutflowDict().items():
        if key!= "Initial":
            #print(selection.a.GetActiveNode().DataFrame.GetColumnNames())
            old_dict[key] = v*selection.a.GetActiveNode().DataFrame.Mean("weight__nominal").GetValue()
            #old_dict[key] = v*selection.GetXsecScale()
    out = open('gg_cutflow/%s/%s_%s_cutflow.txt'%(args.tag,args.setname, args.era),'w')
    out.write(json.dumps(old_dict))
    out.close()

    print ('%s sec'%(time.time()-start))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-s', type=str, dest='setname',
                        action='store', required=True,
                        help='Setname to process.')
    parser.add_argument('-y', type=str, dest='era',
                        action='store', required=True,
                        help='Year of set (16, 17, 18).')
    parser.add_argument('--ss', type=str, dest='samplestr',
                        action='store', default='',
                        help='Multi sample str')
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    parser.add_argument('-m', type=int, dest='mass',
                        action='store', default=125,
                        help='Mass')
    args = parser.parse_args()
    args.threads = 1
    HHstudies(args)
