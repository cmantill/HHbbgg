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

    selection.a.Define("fatjet", "hardware::TLvector(SelFatJet_pt[fatjet_index],SelFatJet_eta[fatjet_index],SelFatJet_phi[fatjet_index],SelFatJet_msoftdrop[fatjet_index])")
    selection.ApplyGen()
    selection.a.Define('GenMatchHJet','GenMatchHJet_idx>=0? GenPart_vect[GenMatchHJet_idx]:hardware::TLvector(0,0,0,0)')
    selection.a.Define('GenMatchBPhoton','GenMatchBPhoton_idx>=0? GenPart_vect[GenMatchBPhoton_idx]:hardware::TLvector(0,0,0,0)')

    selection.a.Define('bjet', 'hardware::TLvector(SelJet_pt[JetAwayFatJet_index],SelJet_eta[JetAwayFatJet_index],SelJet_phi[JetAwayFatJet_index],SelJet_mass[JetAwayFatJet_index])')
    selection.a.Define('deltaR_genH_bjet','hardware::DeltaR(GenMatchHJet,bjet)')
    selection.a.Define('deltaR_genH_fatjet','hardware::DeltaR(GenMatchHJet,fatjet)')
    selection.a.Define('deltaR_genb_bjet','hardware::DeltaR(GenMatchBPhoton,bjet)')

    selection.a.Define('deltaR_bjet_fatjet','hardware::DeltaR(fatjet,bjet)')

    selection.a.Define("sublead_photon", "hardware::TLvector(SelPhoton_pt[1],SelPhoton_eta[1],SelPhoton_phi[1],0)")
    selection.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")

    selection.a.Define("bscore_jetaway", "JetAwayFatJet_index>=0? SelJet_btagDeepFlavB[JetAwayFatJet_index]:-1")
    selection.a.Define('dr_fj_p0','hardware::DeltaR(lead_photon,fatjet)')
    selection.a.Define('dr_p0_p1','hardware::DeltaR(lead_photon,sublead_photon)')
    selection.a.Define('dphi_p0_p1','hardware::DeltaPhi(SelPhoton_phi[0],SelPhoton_phi[1])')
    selection.a.Define('deta_p0_p1','SelPhoton_eta[0]-SelPhoton_eta[1]')
    selection.a.Define("met", "metpt")
    selection.a.Define("pt0_over_mgg", "SelPhoton_pt[0]/mgg")
    selection.a.Define("pt1_over_mgg", "SelPhoton_pt[1]/mgg")
    selection.a.Define("ptj", "SelFatJet_pt[fatjet_index]")
    selection.a.Define("pt0", "SelPhoton_pt[0]")
    selection.a.Define("mjet", "SelFatJet_msoftdrop[fatjet_index]")
    selection.a.Define("invm", "hardware::InvariantMass({fatjet,lead_photon,sublead_photon})")
    selection.a.Define("redm", "invm-mjet-mgg+{0}".format(selection.mh))
    selection.a.Define("pt0_over_mj", "SelFatJet_pt[fatjet_index]/mjet")
    selection.a.Define("ptgg_over_inv", "(lead_photon+sublead_photon).Pt()/invm")
    selection.a.Define("ptj_over_inv", "SelFatJet_pt[fatjet_index]/invm")

    selection.a.Define('deltaR_fatjet_photon0','hardware::DeltaR(lead_photon,fatjet)')
    selection.a.Define('deltaR_fatjet_photon1','hardware::DeltaR(sublead_photon,fatjet)')
    #selection.a.Cut('photonsawayjet',"deltaR_fatjet_photon0>0.4 && deltaR_fatjet_photon1>0.4")
    #selection.a.Cut("nobtagsaway", "bscore_jetaway < 0.340")
    #selection.a.Cut("deltar", "dr_fj_p0>1.")
    #selection.a.Cut("SelFatJet_Xbb_tight","SelFatJet_Xbb[0]>0.9 && SelFatJet_pt[0]>300")

    try:
        xsecscale = selection.GetXsecScale()
        selection.a.MakeWeightCols(extraNominal='' if selection.a.isData else 'genWeight*%s'%xsecscale)
    except:
        exit(1)

    selection.a.Snapshot(["mjet","invm","mgg","weight__nominal",],'selfiles/%s/%s_%s.root'%(args.tag,args.setname,args.era),'Events',saveRunChain=False)
    
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
    kinPlots.Add('bscore_jetaway',selection.a.DataFrame.Histo1D(('bscore_jetaway',r';Jet.btagDeep;Events',30,-1,1),'bscore_jetaway','weight__nominal'))
    kinPlots.Add('dr_fj_p0',selection.a.DataFrame.Histo1D(('dr_fj_p0',r';#Delta R(fj,#gamma^0);Events',30,0.,4),'dr_fj_p0','weight__nominal'))
    kinPlots.Add('deltaR_fatjet_photon1',selection.a.DataFrame.Histo1D(('deltaR_fatjet_photon1',r';#Delta R(fj,#gamma^1);Events',30,0.,4),'deltaR_fatjet_photon1','weight__nominal'))
    kinPlots.Add('deltaR_genH_bjet',selection.a.DataFrame.Histo1D(('deltaR_genH_bjet',r';#Delta R(b-jet,H);Events',30,0.,4),'deltaR_genH_bjet','weight__nominal'))
    kinPlots.Add('deltaR_genH_fatjet',selection.a.DataFrame.Histo1D(('deltaR_genH_fatjet',r';#Delta R(fj,H);Events',30,0.,4),'deltaR_genH_fatjet','weight__nominal'))
    kinPlots.Add('deltaR_genb_bjet',selection.a.DataFrame.Histo1D(('deltaR_genb_bjet',r';#Delta R(b-jet,b);Events',30,0.,4),'deltaR_genb_bjet','weight__nominal'))
    kinPlots.Add('deltaR_bjet_fatjet',selection.a.DataFrame.Histo1D(('deltaR_bjet_fatjet',r';#Delta R(b-jet,fj);Events',30,0.,4),'deltaR_bjet_fatjet','weight__nominal'))
    out = ROOT.TFile.Open('rootfiles/%s/HHstudies_%s_%s.root'%(args.tag,args.setname,args.era),'RECREATE')
    out.cd()
    kinPlots.Do('Write')

    import json
    fcutflow_old = "gg_cutflow/%s_%s_cutflow.txt"%(args.setname, args.era)
    old_dict = json.load(open(fcutflow_old), object_pairs_hook=OrderedDict)
    for key,v in selection.GetCutflowDict().items():
        if key!= "Initial":
            old_dict[key] = v

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
    args = parser.parse_args()
    args.threads = 1
    HHstudies(args)
