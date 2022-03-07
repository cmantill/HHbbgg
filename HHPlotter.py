from argparse import Namespace
from glob import glob
from HHstudies import HHstudies
from TIMBER.Tools.Common import DictStructureCopy, CompileCpp, ExecuteCmd, OpenJSON, StitchQCD
from TIMBER.Tools.Plot import CompareShapes
import multiprocessing, ROOT, time

nmssm_dict = {
    1200: [60,400],
    # 300: [60,70,80,90,100,125,150],
    # 400: [60,70,80,90,100,125,150,200,250],
    # 500: [60,70,80,90,100,125,150,200,250,300],
    # 600: [60,70,80,90,100,125,150,200,250,300,400],
    # 700: [70,80,90,100,125,150,200,250,300,400,500],
    # 800: [60,70,80,90,100,125,150,200,250,300,400,500,600],
    # 900: [60,70,80,90,100,125,150,200,250,300,400,500,600,700],
    # 1000: [60,70,80,90,100,125,150,200,250,300,400,500,600,700,800],
}
colors_dict = {
    "GJets": ROOT.kOrange+5,
    "ttbar": ROOT.kAzure,
    "Hbb": ROOT.kGreen+2,
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

def CombineCommonSets(groupname,doStudies=False,modstr=''):
    '''Which stitch together
    @param groupname (str, optional): "QCD","GJets" or "ttbar".
    '''
    if groupname not in ["GJets","ttbar","Hbb"]:
        raise ValueError('Can only combine GJets or ttbar')
    config = OpenJSON('HHConfig.json')
    #for y in ['16','17','18']:
    for y in ['17']:
        baseStr = 'rootfiles/HHstudies_{0}_{1}.root'
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
                # baseStr.format('GJetsHT100-200',y),
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

def MakeRun2(setname,doStudies=False,modstr=''):
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
        # if "NMSSM" in setname:
        #     my = setname.split('-')[-1]
        #     if '1000MY' in my:
        #         my = my[6:]
        #     else:
        #         my = my[5:]
        #     process_args.append(Namespace(threads=nthreads,setname=setname,era=era,samplestr=my))
        # else:
        process_args.append(Namespace(threads=nthreads,setname=setname,era=era,samplestr=''))
    print(process_args)
    start = time.time()

    pool.map(HHstudies,process_args)
    print ('Total multicore time: %s'%(time.time()-start))                                    

def plot(histname,fancyname,signal,year='16'):
    files = [f for f in glob('rootfiles/HHstudies_*_%s.root'%year) if (('_GJets_' in f) or ('_ttbar_' in f) or ('_Hbb_' in f) or (signal in f))]
    hists = GetHistDict(histname,files)

    yearname = year
    if year=='Run2': yearname = 1

    colors = colors_dict.copy()

    names = {}
    for key in hists['bkg'].keys():
        names[key] = key
    i=0
    for key in hists['sig'].keys():
        names[key] = 'MX'+key.split('-')[-1]
        colors[key] = ROOT.kRed-i
        i+=1

    optimize = True
    print(hists['bkg'],hists['sig'])
    CompareShapes('plots/%s_%s.pdf'%(histname,year),
                  yearname,
                  fancyname,
                  bkgs=hists['bkg'],
                  signals=hists['sig'],
                  names=names,
                  colors=colors,
                  scale=False, 
                  stackBkg=True,
                  doSoverB=optimize,
                  forceBackward=False,
                  logy=True
    )


def plot_signals(histname,fancyname,year='Run2',mx='1000'):
    nmssm_plot_dict = {
        1200: [60,400],
        # 300: [60,70,80,90,100,125,150],
        # 400: [60,70,80,90,100,125,150,200,250],
        # 500: [60,70,80,90,100,125,150,200,250,300],
        # 600: [60,70,80,90,100,125,150,200,250,300,400],
        # 700: [70,80,90,100,125,150,200,250,300,400,500],
        # 800: [60,70,80,90,100,125,150,200,250,300,400,500,600],
        # 900: [60,70,80,90,100,125,150,200,250,300,400,500,600,700],
        # 1000: [60,80,100,125,200,300,400,800],
    }
    #files = ['rootfiles/HHstudies_NMSSM-XToYHTo2b2g-MX-%sMY%i_%s.root'%(mx,my,year) for my in nmssm_plot_dict[int(mx)]]
    files = ['rootfiles/HHstudies_NMSSM-XToYHTo2g2b-MX-%sMY%i_%s.root'%(mx,my,year) for my in nmssm_plot_dict[int(mx)]]
    hists = GetHistDict(histname,files)
    yearname = year
    if year=='Run2': yearname = 1
    names = {}
    for key in hists['sig'].keys():
        names[key] = 'MX'+key.split('-')[-1]
        colors[key] = ROOT.kRed
    CompareShapes('plots/signal_%s_%s_mx%s.pdf'%(histname,year,mx),
                  yearname,
                  fancyname,
                  signals=hists['sig'],
                  names=names,
                  colors=colors,
                  scale=True,
                  logy=False                  
                  )

def plot_sig_bkg(histname,fancyname,year='Run2',mx='1000'):
    nmssm_plot_dict = {
        1200: [60,400],
    }
    files = [f for f in glob('rootfiles/HHstudies_*_%s.root'%year) if (('_GJets_' in f) or ('_ttbar_' in f) or ('_Hbb_' in f) or ('NMSSM-XToYHTo2g2b' in f))]
    print(files)
    hists = GetHistDict(histname,files)
    yearname = year
    if year=='Run2': yearname = 1

    colors = colors_dict.copy()
    names = {}
    for key in hists['bkg'].keys():
        names[key] = key
    i=0
    for key in hists['sig'].keys():
        names[key] = 'MX'+key.split('-')[-1]
        colors[key] = ROOT.kRed-i
        i+=1
    CompareShapes('plots/compare_%s_%s_mx%s.pdf'%(histname,year,mx),
                  yearname,
                  fancyname,
                  bkgs=hists['bkg'],
                  signals=hists['sig'],
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

    args = parser.parse_args()

    if not args.recycle:
        #multicore(doStudies=True)

        CombineCommonSets('GJets',True)
        CombineCommonSets('ttbar',True)
        CombineCommonSets('Hbb',True)

        """
        MakeRun2('GJets',True)
        MakeRun2('ttbar',True)

        for m in [1200]:
            for my in [60,400]:
                try:
                    MakeRun2('NMSSM-XToYHTo2g2g-MX-%sMY%s'%(m,str(my)),True)
                except:
                    print('no %s for %s'%(str(my),m))                     
        """

    histNames = {
        #'mgg':'DiPhoton invariant mass m_{#gamma#gamma} (GeV)',
        'pt0': 'Lead photon p_{T} (GeV)',
        'pt0_over_mgg':'p_{T}^{#gamma_{0}}/m_{#gamma#gamma}',
        'pt1_over_mgg':'p_{T}^{#gamma_{1}}/m_{#gamma#gamma}',
        'invm': 'M_{j#gamma#gamma}',
        'redm': 'M_{j#gamma#gamma}-M_{j}-M_{#gamma#gamma}+2*M_{H}',
        'ptj':'Lead jet p_{T} (GeV)',
        'mjet':'Lead jet m_{SD} (GeV)',
        #'ptgg_over_inv':'p_{T}^{#gamma#gamma}/M_{j#gamma#gamma}',
        'ptj_over_inv':'p_{T}^{j}/M_{j#gamma#gamma}',
        'pt0_over_mj':'p_{T}^{j}/m_{SD}',
        'bscore_jetaway':'deepFlav b-jet away',
        'dr_fj_p0':'#Delta R(j,#gamma_{0})',
    }

    tempFile = ROOT.TFile.Open('rootfiles/HHstudies_NMSSM-XToYHTo2g2b-MX-1200MY400_17.root','READ')
    allValidationHists = [k.GetName() for k in tempFile.GetListOfKeys() if 'Idx' not in k.GetName()]
    for h in allValidationHists:
        print ('Plotting: %s'%h)
        if h in histNames.keys():
            #plot_signals(h,histNames[h],'17',mx='1200')
            plot_sig_bkg(h,histNames[h],year='17',mx='1200')
            plot(h,histNames[h],'NMSSM-XToYHTo2g2b-MX-1200MY400','17')
            
            
