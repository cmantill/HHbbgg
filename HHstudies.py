import ROOT, time

from TIMBER.Analyzer import HistGroup, Correction
from TIMBER.Tools.Common import CompileCpp
ROOT.gROOT.SetBatch(True)

from HHClass import HHClass

# Not for use with data
def HHstudies(args):
    print ('PROCESSING: %s %s'%(args.setname, args.era))
    ROOT.ROOT.EnableImplicitMT(args.threads)
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
    selection.a.Define("lead_fatjet", "hardware::TLvector(SelFatJet_pt[0],SelFatJet_eta[0],SelFatJet_phi[0],SelFatJet_mass[0])")
    selection.a.Define("mgg", "hardware::InvariantMass({lead_photon,sublead_photon})")

    selection.a.Cut("SelFatJet_Xbb_tight","SelFatJet_Xbb[0]>0.9 && SelFatJet_pt[0]>300")
    selection.a.Cut("ptphoton_over_mgg", "(SelPhoton_pt[0]/mgg > 1/3) && (SelPhoton_pt[1]/mgg > 1/4)")

    selection.a.Define('dr_fj_p0','hardware::DeltaR(lead_photon,lead_fatjet)')
    selection.a.Cut("deltar", "dr_fj_p0>1.")

    selection.a.Define("bscore_jetaway", "SelFatJet_awaybjet")
    selection.a.Cut("nobtagsaway", "bscore_jetaway < 0.340")

    selection.a.Define("pt0_over_mgg", "SelPhoton_pt[0]/mgg")
    selection.a.Define("pt1_over_mgg", "SelPhoton_pt[1]/mgg")
    selection.a.Define("ptj", "SelFatJet_pt[0]")
    selection.a.Define("pt0", "SelPhoton_pt[0]")
    selection.a.Define("mjet", "SelFatJet_msoftdrop[0]")
    selection.a.Define("invm", "hardware::InvariantMass({lead_fatjet,lead_photon,sublead_photon})")
    selection.a.Define("redm", "invm-mjet-mgg+2*{0}".format(selection.mh))
    selection.a.Define("pt0_over_mj", "SelFatJet_pt[0]/mjet")
    selection.a.Define("ptgg_over_inv", "(lead_photon+sublead_photon).Pt()/invm")
    selection.a.Define("ptj_over_inv", "SelFatJet_pt[0]/invm")
    try:
        xsecscale = selection.GetXsecScale()
        selection.a.MakeWeightCols(extraNominal='' if selection.a.isData else 'genWeight*%s'%xsecscale)
    except:
        exit(1)

    selection.a.Snapshot(["mjet","invm","mgg","weight__nominal",],'%s_%s.root'%(args.setname,args.era),'Events',saveRunChain=False)
    
    # Kinematic plots
    kinPlots = HistGroup('kinPlots')
    kinPlots.Add('mgg',selection.a.DataFrame.Histo1D(('mgg',';M_{#gamma#gamma} [GeV];Events',100,40,450),'mgg','weight__nominal'))
    kinPlots.Add('pt0',selection.a.DataFrame.Histo1D(('pt0',r';p_{T}(#gamma_{0}) [GeV];Events',60,30,500),'pt0','weight__nominal'))
    kinPlots.Add('pt0_over_mgg',selection.a.DataFrame.Histo1D(('pt0_over_mgg',';p_{T}(#gamma^{1})/M_{#gamma#gamma};Events',40,0,6),'pt0_over_mgg','weight__nominal'))
    kinPlots.Add('pt1_over_mgg',selection.a.DataFrame.Histo1D(('pt1_over_mgg',';p_{T}(#gamma^{2})/M_{#gamma#gamma};Events',40,0,6),'pt1_over_mgg','weight__nominal'))
    kinPlots.Add('invm',selection.a.DataFrame.Histo1D(('invm',';M_{j#gamma#gamma} [GeV];Events',60,100,1400),'invm','weight__nominal'))
    kinPlots.Add('redm',selection.a.DataFrame.Histo1D(('redm',';M_{j#gamma#gamma}-M_{j}-M_{#gamma#gamma}+2*M_{H};Events',60,0,2000),'redm','weight__nominal'))
    kinPlots.Add('ptj',selection.a.DataFrame.Histo1D(('ptj',r';p_{T}(j) [GeV];Events',60,250,1000),'ptj','weight__nominal'))
    kinPlots.Add('mjet',selection.a.DataFrame.Histo1D(('mjet',r';m_{SD}(j) [GeV];Events',60,50,400),'mjet','weight__nominal'))
    kinPlots.Add('ptgg_over_inv',selection.a.DataFrame.Histo1D(('ptgg_over_inv',r';p_{T}(#gamma#gamma)/M_{X};Events',30,0,100),'ptgg_over_inv','weight__nominal'))
    kinPlots.Add('ptj_over_inv',selection.a.DataFrame.Histo1D(('ptj_over_inv',r';p_{T}(j)/M_{X};Events',30,0,3),'ptj_over_inv','weight__nominal'))
    kinPlots.Add('pt0_over_mj',selection.a.DataFrame.Histo1D(('pt0_over_mj',r';p_{T}(j)/m_{SD};Events',30,1.5,8),'pt0_over_mj','weight__nominal'))
    kinPlots.Add('bscore_jetaway',selection.a.DataFrame.Histo1D(('bscore_jetaway',r';Jet.btagDeep;Events',30,0,1),'bscore_jetaway','weight__nominal'))
    kinPlots.Add('dr_fj_p0',selection.a.DataFrame.Histo1D(('dr_fj_p0',r';#Delta R(fj,#gamma^0);Events',30,0.4,3.5),'dr_fj_p0','weight__nominal'))

    print('rootfiles/HHstudies_%s_%s.root'%(args.setname,args.era))
    out = ROOT.TFile.Open('rootfiles/HHstudies_%s_%s.root'%(args.setname,args.era),'RECREATE')
    out.cd()
    kinPlots.Do('Write')

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
    args = parser.parse_args()
    args.threads = 1
    HHstudies(args)
