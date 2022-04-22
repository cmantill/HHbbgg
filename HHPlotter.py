from argparse import Namespace
from glob import glob
from HHstudies import HHstudies
from TIMBER.Tools.Common import DictStructureCopy, CompileCpp, ExecuteCmd, OpenJSON, StitchQCD
from TIMBER.Tools.Plot import CompareShapes
import multiprocessing, ROOT, time

nmssm_dict = {
    1200: [60,125,300,400],
}
colors_dict = {
    "GJets": ROOT.kOrange+5,
    "ttbar": ROOT.kAzure-2,
    "TT": ROOT.kAzure-2,
    "TTToHadronic": ROOT.kAzure+8,
    "TTTo2L2Nu": ROOT.kAzure-2,
    "TTToSemiLeptonic": ROOT.kCyan-3,
    "Hbb": ROOT.kGreen+2,
    "QCD": ROOT.kRed-7
}
labels_dict = {
    "GJets": "#gamma+jets",
    "TTToHadronic": "tt had",
    "TTTo2L2Nu": "tt lep",
    "TTToSemiLeptonic": "tt sl",
    "Hbb": "h(bb)",
    "QCD": "QCD",
}

def GetAllFiles():
    return [f for f in glob('gg_nano/*_snapshot.txt') if f != '']
    
def GetProcYearFromTxt(filename):
    pieces = filename.split('/')[-1].split('.')[0].split('_')
    return pieces[0], pieces[1]
def GetProcYearFromROOT(filename):
    pieces = filename.split('/')[-1].split('.')[0].split('_')
    return pieces[1], pieces[2]

def GetHistDict(histname, all_files):
    all_hists = {
        'bkg':{},'sig':{},'data':None
    }
    for f in all_files:
        proc, year = GetProcYearFromROOT(f)
        tfile = ROOT.TFile.Open(f)
        hist = tfile.Get(histname)
        if hist == None:
            raise ValueError('Histogram %s does not exist in %s.'%(histname,f))
        hist.SetDirectory(0)
        if 'HH' in proc or 'NMSSM' in proc:
            all_hists['sig'][proc] = hist
        elif proc == 'Data':
            all_hists['data'] = hist
        else:
            all_hists['bkg'][proc] = hist
    return all_hists

def CombineCommonSets(tag,groupname,doStudies=False,modstr=''):
    '''Which stitch together
    @param groupname (str, optional): "QCD","GJets" or "ttbar".
    '''
    if groupname not in ["GJets","ttbar","Hbb","QCD"]:
        raise ValueError('Can only combine GJets or ttbar')
    config = OpenJSON('HHConfig.json')
    #for y in ['16','17','18']:
    for y in ['17']:
        baseStr = 'rootfiles/%s/HHstudies_{0}_{1}.root'%tag
        if groupname == 'ttbar':
            ExecuteCmd('hadd -f %s %s %s %s'%(
                baseStr.format('ttbar',y),
                baseStr.format('TTTo2L2Nu',y),
                baseStr.format('TTToSemiLeptonic',y),
                baseStr.format('TTToHadronic',y)
            )
            )
        elif groupname == 'GJets':
            ExecuteCmd('hadd -f %s %s %s %s %s %s'%(
                baseStr.format('GJets',y),
                #baseStr.format('GJetsHT100-200',y),
                baseStr.format('GJetsHT200-400',y),
                baseStr.format('GJetsHT400-600',y),
                baseStr.format('GJetsHT600-Inf',y),
                baseStr.format('DiPhotonJets-MGG-80toInf',y),
                baseStr.format('GJetPt40toInfDoubleEMEnriched-MGG80toInf',y)
                #baseStr.format('GJetPt20to40DoubleEMEnriched-MGG80toInf',y)
            )
            )
        elif groupname == 'Hbb':
            ExecuteCmd('hadd -f %s %s %s %s'%(
                baseStr.format('Hbb',y),
                baseStr.format('ggH-HtoBB',y),
                #baseStr.format('ZH-HtoBB-ZtoQQ',y),
                #baseStr.format('ggZH-HtoBB-ZtoQQ',y),
                baseStr.format('VBF-HtoBB',y),
                baseStr.format('ttH-HtoBB',y),
                #baseStr.format('WminusH-HToBB-WtoQQ',y),
                #baseStr.format('WplusH-HToBB-WtoQQ',y)
            )
            )
        elif groupname == "QCD":
            ExecuteCmd('hadd -f %s %s %s %s %s'%(
                baseStr.format('QCD',y),
                baseStr.format('QCDHT700to1000',y),
                baseStr.format('QCDHT1000to1500',y),
                baseStr.format('QCDHT1500to2000',y),
                baseStr.format('QCDHT2000toInf',y),
            )
            )

def MakeRun2(tag,setname,doStudies=False,modstr=''):
    t = 'studies' if doStudies else 'selection'
    ExecuteCmd('hadd -f rootfiles/HH{1}_{0}{2}_Run2.root rootfiles/HH{1}_{0}{2}_16.root rootfiles/HH{1}_{0}{2}_17.root rootfiles/HH{1}_{0}{2}_18.root'.format(setname,t,modstr))

def multicore(infiles=[],doStudies=True):
    if infiles == []: files = GetAllFiles()
    else: files = infiles

    pool = multiprocessing.Pool(processes=4 if doStudies else 6,maxtasksperchild=1)
    #nthreads = 4 if doStudies else 2
    nthreads = 1
    process_args = []
    for f in files:
        setname, era = GetProcYearFromTxt(f)
        process_args.append(Namespace(threads=nthreads,setname=setname,era=era,samplestr=''))
    #print(process_args)
    start = time.time()

    pool.map(HHstudies,process_args)
    print ('Total multicore time: %s'%(time.time()-start))                                    

def plot(tag,histname,fancyname,year='16'):
    files = [f for f in glob('rootfiles/%s/HHstudies_*_%s.root'%(tag,year)) if (('_GJets_' in f) or ('_ttbar_' in f) or ('NMSSM-XToYHTo2g2b-MX-1200MY400' in f))]
    #files = [f for f in glob('rootfiles/%s/HHstudies_*_%s.root'%(tag,year)) if (('_GJets_' in f) or ('_TTTo2L' in f) or ('_TTToSemi' in f) or ('_TTToHad' in f) or ('NMSSM-XToYHTo2g2b' in f) or ('HHbbgg-cHH1' in f))]
    #print(files)
    hists = GetHistDict(histname,files)

    yearname = year
    if year=='Run2': yearname = 1
    yearname = 1

    colors = colors_dict.copy()

    names = {}
    for key in hists['bkg'].keys():
        names[key] = key
    i=0
    for key in hists['sig'].keys():
        if 'HH' in key:
            names[key] = 'HH mH=125'
            colors[key] = ROOT.kBlue
        else:
            names[key] = 'MX'+key.split('-')[-1]
            colors[key] = ROOT.kRed-i
        i+=1

    hbkg = {'TT':hists['bkg']['ttbar'],'GJets':hists['bkg']['GJets']}
    optimize = True
    print(hists['bkg'],hists['sig'])
    CompareShapes('plots/%s/%s_%s.pdf'%(tag,histname,year),
                  yearname,
                  fancyname,
                  bkgs=hbkg,
                  signals=hists['sig'],
                  names=names,
                  colors=colors,
                  scale=False, 
                  stackBkg=True,
                  doSoverB=optimize,
                  forceBackward=False,
                  logy=True
    )


def plot_signals(tag,histname,fancyname,year='Run2',mx='1000'):
    nmssm_plot_dict = {
        1200: [60,400],
    }
    files = ['rootfiles/%s/HHstudies_NMSSM-XToYHTo2g2b-MX-%sMY%i_%s.root'%(tag,mx,my,year) for my in nmssm_plot_dict[int(mx)]]
    hists = GetHistDict(histname,files)
    yearname = year
    if year=='Run2': yearname = 1
    names = {}
    for key in hists['sig'].keys():
        if 'HH' in key:
            names[key] = 'HH mH=125'
            colors[key] = ROOT.kBlue
        else:
            names[key] = 'MX'+key.split('-')[-1]
            colors[key] = ROOT.kRed-i
    CompareShapes('plots/%s/signal_%s_%s_mx%s.pdf'%(tag,histname,year,mx),
                  yearname,
                  fancyname,
                  signals=hists['sig'],
                  names=names,
                  colors=colors,
                  scale=True,
                  logy=False                  
                  )

def plot_sig_bkg(tag,histname,fancyname,year='Run2',sig=True,bkg=True):
    files = []
    if sig:
        files = [f for f in glob('rootfiles/%s/HHstudies_*_%s.root'%(tag,year)) if (('MX-1200MY125' in f) or ('MX-1200MY400' in f) or ('MX-2000MY20' in f) or ('MX-2000MY20' in f) or ('HHbbgg-cHH1' in f))]
    if bkg:
        files += [f for f in glob('rootfiles/%s/HHstudies_*_%s.root'%(tag,year)) if (('_GJets_' in f) or ('_TTTo2L' in f) or ('_TTToSemi' in f))]
    #print(files)
    hists = GetHistDict(histname,files)
    yearname = year
    if year=='Run2': yearname = 1
    yearname = 1 ##!

    colors = colors_dict.copy()
    names = {}
    h_all = {}
    for key in hists['bkg'].keys():
        names[key] = labels_dict[key]
        h_all[key] = hists['bkg'][key]
    i=0
    for key in hists['sig'].keys():
        if 'HH' in key:
            names[key] = 'HH mH=125'
            colors[key] = ROOT.kBlue
        else:
            names[key] = 'MX'+key.split('-')[-1]
            colors[key] = ROOT.kRed-i
        h_all[key] = hists['sig'][key]
        i+=1

    stag = ''
    if sig: stag+='sig'
    if bkg: stag+='bkg'
    plotname = 'plots/%s/compare_%s_%s_%s.pdf'%(tag,histname,year,stag)
    CompareShapes(plotname,
                  yearname,
                  fancyname,
                  bkgs=hists['bkg'],
                  signals=hists['sig'],
                  #signals=h_all,
                  names=names,
                  colors=colors,
                  scale=True,
                  logy=False
    )


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--recycle', dest='recycle',
                        action='store_true', default=False,
                        help='Recycle existing files and just plot.')
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    args = parser.parse_args()

    if not args.recycle:
        #multicore(doStudies=True)

        CombineCommonSets(args.tag,'GJets',True)
        CombineCommonSets(args.tag,'ttbar',True)
        CombineCommonSets(args.tag,'Hbb',True)
        CombineCommonSets(args.tag,'QCD',True)

    histNames = {
        #'mgg':'DiPhoton invariant mass m_{#gamma#gamma} (GeV)',
        'ptgg_over_inv':'p_{T}^{#gamma#gamma}/M_{j#gamma#gamma}',
        'pt0': 'Lead photon p_{T} (GeV)',
        'pt0_over_mgg':'p_{T}^{#gamma_{0}}/m_{#gamma#gamma}',
        'pt1_over_mgg':'p_{T}^{#gamma_{1}}/m_{#gamma#gamma}',
        #'invm': 'M_{j#gamma#gamma}',
        'redm': 'M_{j#gamma#gamma}-M_{j}-M_{#gamma#gamma}+2*M_{H}',
        'ptj':'Lead jet p_{T} (GeV)',
        'mjet':'Lead jet m_{SD} (GeV)',
        'met': 'MET (GeV)',
        'ptj_over_inv':'p_{T}^{j}/M_{j#gamma#gamma}',
        'pt0_over_mj':'p_{T}^{j}/m_{SD}',
        'bscore_jetaway':'deepFlav b-jet away',
        'dr_fj_p0':'#Delta R(j,#gamma_{0})',
        'dr_fj_p1': '#Delta R(j,#gamma_{1})',
        'deltaR_bjet_fatjet': '#Delta R(j,b-jet)',
        'dr_p0_p1': '#Delta R(#gamma_{0},#gamma_{1})',
        'deta_p0_p1': '#Delta #eta(#gamma_{0},#gamma_{1})',
        'dphi_p0_p1': '#Delta #phi(#gamma_{0},#gamma_{1})',
        'p0_mva': 'MVA ID #gamma_{0}',
        'p1_mva': 'MVA ID #gamma_{1}',
    }

    import os
    os.system('mkdir -p plots/%s/'%args.tag)

    tempFile = ROOT.TFile.Open('rootfiles/%s/HHstudies_NMSSM-XToYHTo2g2b-MX-1200MY400_17.root'%args.tag,'READ')
    allValidationHists = [k.GetName() for k in tempFile.GetListOfKeys() if 'Idx' not in k.GetName()]
    for h in allValidationHists:
        print ('Plotting: %s'%h)
        if h in histNames.keys():
            #print(h)
            #plot_signals(h,histNames[h],'17',mx='1200')
            plot_sig_bkg(args.tag,h,histNames[h],year='17',sig=True,bkg=True)
            plot_sig_bkg(args.tag,h,histNames[h],year='17',sig=True,bkg=False)
            plot(args.tag,h,histNames[h],year='17')
