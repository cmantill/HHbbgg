import ROOT, time

from TIMBER.Analyzer import HistGroup, Correction
from TIMBER.Tools.Common import CompileCpp
ROOT.gROOT.SetBatch(True)

import os

from HH_class import HHClass
from collections import OrderedDict

def HHstudies(args):
    print ('PROCESSING: %s %s'%(args.setname, args.era))
    ROOT.ROOT.EnableImplicitMT(args.threads)

    import json
    fcutflow_old = "gg_nano/%s/cutflows/%s_%s.txt"%(args.tag,args.setname, args.era)
    cutflow_dict = json.load(open(fcutflow_old), object_pairs_hook=OrderedDict)
    if cutflow_dict["diphoton_eveto"]<=0:
        print(cutflow_dict["diphoton_eveto"])
        return

    mh = 125
    if 'NMSSM' in args.setname:
        mh = int(args.setname.split('-')[3].replace('MY',''))
    if 'XHY-' in args.setname:
        mh = int(args.setname.split('-')[2].replace('my',''))    

    start = time.time()
    # Base setup
    hh = HHClass('gg_nano/%s/snapshots/%s_%s.txt'%(args.tag,args.setname,args.era),int(args.era),1,1,mh=mh,silent=True)
    hh.Selection(xbb_cut=0.9)

    # Kinematic plots
    kinPlots = HistGroup('kinPlots')
    mass = 125
    kinPlots.Add('mgg',hh.a.DataFrame.Histo1D(('mgg',';M_{#gamma#gamma} [GeV];Events',100,40,450),'mgg','weight__nominal'))
    kinPlots.Add('mbb_mgg',hh.a.DataFrame.Histo2D(('mbb_mg',';M_{bb} [GeV];M_{#gamma#gamma} [GeV];Events',60,90,150,60,mass-15,mass+15),'mreg','mgg','weight__nominal'))
    kinPlots.Add('pt0',hh.a.DataFrame.Histo1D(('pt0',r';p_{T}(#gamma_{0}) [GeV];Events',60,30,500),'pt0','weight__nominal'))
    kinPlots.Add('pt0_over_mgg',hh.a.DataFrame.Histo1D(('pt0_over_mgg',';p_{T}(#gamma^{1})/M_{#gamma#gamma};Events',40,0,6),'pt0_over_mgg','weight__nominal'))
    kinPlots.Add('pt1_over_mgg',hh.a.DataFrame.Histo1D(('pt1_over_mgg',';p_{T}(#gamma^{2})/M_{#gamma#gamma};Events',40,0,6),'pt1_over_mgg','weight__nominal'))
    kinPlots.Add('dr_p0_p1',hh.a.DataFrame.Histo1D(('dr_p0_p1',';#Delta R(#gamma_{0},#gamma_{1});Events',40,0,2),'dr_p0_p1','weight__nominal'))
    kinPlots.Add('invm',hh.a.DataFrame.Histo1D(('invm',';M_{j#gamma#gamma} [GeV];Events',60,100,1400),'invm','weight__nominal'))
    kinPlots.Add('fourm',hh.a.DataFrame.Histo1D(('fourm',';M_{j#gamma#gamma}-M_{j}-M_{#gamma#gamma}+M_{H}+M_{Y};Events',60,0,2000),'fourm','weight__nominal'))
    kinPlots.Add('ptj',hh.a.DataFrame.Histo1D(('ptj',r';p_{T}(j) [GeV];Events',60,250,1000),'ptj','weight__nominal'))
    kinPlots.Add('met',hh.a.DataFrame.Histo1D(('met',r';MET [GeV];Events',60,0,150),'met','weight__nominal'))
    kinPlots.Add('mreg',hh.a.DataFrame.Histo1D(('mreg',r';m_{reg}(j) [GeV];Events',60,50,250),'msd','weight__nominal'))
    kinPlots.Add('msd',hh.a.DataFrame.Histo1D(('msd',r';m_{SD}(j) [GeV];Events',60,50,250),'msd','weight__nominal'))
    kinPlots.Add('ptgg_over_inv',hh.a.DataFrame.Histo1D(('ptgg_over_inv',r';p_{T}(#gamma#gamma)/M_{X};Events',30,0,2),'ptgg_over_inv','weight__nominal'))
    kinPlots.Add('ptj_over_inv',hh.a.DataFrame.Histo1D(('ptj_over_inv',r';p_{T}(j)/M_{X};Events',30,0,3),'ptj_over_inv','weight__nominal'))
    kinPlots.Add('pt0_over_mj',hh.a.DataFrame.Histo1D(('pt0_over_mj',r';p_{T}(j)/m_{SD};Events',30,1.5,8),'pt0_over_mj','weight__nominal'))
    kinPlots.Add('bscore_jetaway',hh.a.DataFrame.Histo1D(('bscore_jetaway',r';Jet.btagDeep;Events',30,0,1),'bscore_jetaway','weight__nominal'))
    kinPlots.Add('dr_fj_p0',hh.a.DataFrame.Histo1D(('dr_fj_p0',r';#Delta R(fj,#gamma^0);Events',30,0.,4),'dr_fj_p0','weight__nominal'))
    kinPlots.Add('dr_fj_p1',hh.a.DataFrame.Histo1D(('dr_fj_p1',r';#Delta R(fj,#gamma^1);Events',30,0.,4),'dr_fj_p1','weight__nominal'))
    kinPlots.Add('deta_p0_p1',hh.a.DataFrame.Histo1D(('deta_p0_p1',r';#Delta#eta(#gamma_{0},#gamma_{1});Events',40,-5,5),'deta_p0_p1','weight__nominal'))
    kinPlots.Add('dphi_p0_p1',hh.a.DataFrame.Histo1D(('dphi_p0_p1',r';#Delta#phi(#gamma_{0},#gamma_{1});Events',40,-5,5),'dphi_p0_p1','weight__nominal'))
    kinPlots.Add('p0_mva',hh.a.DataFrame.Histo1D(('p0_mva',r';MVA #gamma_{0};Events',40,-1,1),'p0_mva','weight__nominal'))
    kinPlots.Add('p1_mva',hh.a.DataFrame.Histo1D(('p1_mva',r';MVA #gamma_{0};Events',40,-1,1),'p1_mva','weight__nominal'))

    os.system('mkdir -p rootfiles/%s'%args.tag)

    out = ROOT.TFile.Open('rootfiles/%s/HHstudies_%s_%s.root'%(args.tag,args.setname,args.era),'RECREATE')
    out.cd()
    kinPlots.Do('Write')
    # print ('%s sec'%(time.time()-start))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-s', type=str, dest='setname',
                        action='store', required=True,
                        help='Setname to process.')
    parser.add_argument('-y', type=str, dest='era',
                        action='store', required=True,
                        help='Year of set (16, 17, 18).')
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    args = parser.parse_args()
    args.threads = 1

    HHstudies(args)
