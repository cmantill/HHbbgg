import os,glob
import ROOT, time

from HHClass import HHClass

def apply_selection(f,fname,tag,i=0,mass=125):
    era = f.split('_')[-2]
    name = f.split('/')[-1].split('_')[0]
    selection = HHClass(f,era,1,1)
    selection.OpenForSelection()
    try:
        selection.a.Define('lead_photon', "hardware::TLvector(SelPhoton_pt[0],SelPhoton_eta[0],SelPhoton_phi[0],0)")
    except:
        print('no lead photon')
        return

    selection.a.Define("sublead_photon", "hardware::TLvector(SelPhoton_pt[1],SelPhoton_eta[1],SelPhoton_phi[1],0)")
    selection.a.Define("fatjet", "hardware::TLvector(SelFatJet_pt[fatjet_index],SelFatJet_eta[fatjet_index],SelFatJet_phi[fatjet_index],SelFatJet_msoftdrop[fatjet_index])")
    selection.a.Define('dr_fj_p0','hardware::DeltaR(lead_photon,fatjet)')
    selection.a.Define('dr_fj_p1','hardware::DeltaR(sublead_photon,fatjet)')
    selection.a.Define("bscore_jetaway", "JetAwayFatJet_index>=0? SelJet_btagDeepFlavB[JetAwayFatJet_index]:2")
    selection.a.Cut("photonsawayjet", "dr_fj_p0>1. && dr_fj_p1>0.8")
    selection.a.Cut("nobtagsaway", "bscore_jetaway < 0.340")
    selection.a.Cut("SelFatJet_Xbb_tight","SelFatJet_Xbb[0]>0.9")

    selection.a.Define("CMS_hgg_mass", "hardware::InvariantMass({lead_photon,sublead_photon})")
    selection.a.Define("CMS_hbb_mass", "SelFatJet_msoftdrop[fatjet_index]")

    if selection.a.isData:
        selection.a.Cut("mbb_veto", "SelFatJet_msoftdrop[fatjet_index]<90 && SelFatJet_msoftdrop[fatjet_index]>150")
        # selection.a.Cut("mgg_veto", "(CMS_hgg_mass < %s) || (CMS_hgg_mass > %s)"%(mass-20,mass+20))
    else:
        selection.a.Cut("mgg_window", "(CMS_hgg_mass > %s) && (CMS_hgg_mass < %s)"%(mass-15,mass+15))

    selection.a.MakeWeightCols(extraNominal='' if selection.a.isData else 'genWeight*%s'%selection.GetXsecScale())
    selection.a.Define("weight","weight__nominal")
    columns = ["CMS_hbb_mass","CMS_hgg_mass","weight"]

    selection.a.Snapshot(columns, fname.replace('.root','%s_%s.root'%(name,era)), 'trees/%s_13TeV_SR'%tag, openOption='RECREATE')
    print(fname.replace('.root','%s_%s.root'%(name,era)))

def HHselection(args):
    
    start = time.time()
    #os.system('rm -r rootfiles/%s/selection*.root'%args.tag)
    os.system('mkdir -p rootfiles/%s'%args.tag)
    
    """
    data_fname = 'rootfiles/%s/selection_data.root'%args.tag
    data_fnames = 'rootfiles/%s/selection_dataData*.root'%args.tag
    for i,f in enumerate(glob.glob('gg_nano/Data*.txt')):
        print(f)
        apply_selection(f,data_fname,"Data",i,args.mass)
    cmd = 'hadd -f %s %s'%(data_fname,data_fnames)
    print(cmd)
    os.system(cmd)
    """

    sig_fname = 'rootfiles/%s/selection_signal_mX1200mY%i.root'%(args.tag,args.mass)
    for i,f in enumerate(glob.glob('gg_nano/NMSSM-XToYHTo2g2b-MX-1200MY%i*.txt'%args.mass)):
        print(f)
        apply_selection(f,sig_fname,"NMSSMX1200ToY%i_125"%args.mass,i,args.mass)
    cmd = 'hadd -f %s %s'%(sig_fname,'rootfiles/%s/selection_signal*NMSSM*.root'%args.tag)
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    parser.add_argument('-m', type=int, dest='mass',
                        action='store', default=125,
                        help='Mass')
    args = parser.parse_args()
    args.threads = 1
    HHselection(args)
