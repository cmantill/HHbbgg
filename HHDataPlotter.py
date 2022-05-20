from argparse import Namespace
from glob import glob
from HHstudies import HHstudies
from TIMBER.Tools.Common import DictStructureCopy, CompileCpp, ExecuteCmd, OpenJSON, StitchQCD
from TIMBER.Tools.Plot import CompareShapes, EasyPlots
import multiprocessing, ROOT, time

colors_dict = {
    "GJets": ROOT.kRed-7,
    "ttbar": ROOT.kGreen-3,
    "TT": ROOT.kGreen-2,
    "TTToHadronic": ROOT.kGreen+8,
    "TTTo2L2Nu": ROOT.kGreen-2,
    "TTToSemiLeptonic": ROOT.kGreen-3,
    "Hbb": ROOT.kAzure-5,
    "QCD": ROOT.kAzure-2,
}
labels_dict = {
    "GJets": "#gamma+jets",
    "ttbar": "tt",
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
        'bkg':{},'sig':{},'data':{}
    }
    for f in all_files:
        proc, year = GetProcYearFromROOT(f)
        tfile = ROOT.TFile.Open(f)
        hist = tfile.Get(histname)
        if hist == None:
            raise ValueError('Histogram %s does not exist in %s.'%(histname,f))
        hist.SetDirectory(0)
        if 'HH' in proc or 'NMSSM' in proc:
            hist.SetName(proc.replace('NMSSM-XToYHTo2g2b-',''))
            all_hists['sig'][proc] = hist
        elif proc == 'Data':
            hist.SetName('Data')
            all_hists['data'] = hist
        else:
            hist.SetName(labels_dict[proc])
            all_hists['bkg'][proc] = hist
    print(all_hists)
    return all_hists

def CombineCommonSets(tag,groupname,doStudies=False,modstr=''):
    '''Which stitch together
    @param groupname (str, optional): "QCD","GJets" or "ttbar".
    '''
    config = OpenJSON('HHConfig.json')
    baseStr = 'rootfiles/%s/HHstudies_{0}_{1}.root'%tag
    for y in ['17']:
        if groupname == 'ttbar':
            ExecuteCmd('hadd -f %s %s %s %s'%(
                baseStr.format('ttbar','Run2'),
                baseStr.format('TTTo2L2Nu',y),
                baseStr.format('TTToSemiLeptonic',y),
                baseStr.format('TTToHadronic',y)
            ))
        elif groupname == 'GJets':
            ExecuteCmd('hadd -f %s %s %s %s %s %s'%(
                baseStr.format('GJets','Run2'),
                baseStr.format('GJetsHT200-400',y),
                baseStr.format('GJetsHT400-600',y),
                baseStr.format('GJetsHT600-Inf',y),
                baseStr.format('DiPhotonJets-MGG-80toInf',y),
                baseStr.format('GJetPt40toInfDoubleEMEnriched-MGG80toInf',y)
            ))
        elif groupname == 'Data':
            cmd = baseStr.format('Data-DoubleEG-RunB','17') 
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunC','17')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunD','17')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunE','17')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunF','17')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunBv2HIPM','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunCHIPM','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunDHIPM','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunEHIPM','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunFHIPM','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunF','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunG','16')
            cmd += ' ' + baseStr.format('Data-DoubleEG-RunH','16')
            cmd += ' ' + baseStr.format('Data-EGamma-RunA','18')
            cmd += ' ' + baseStr.format('Data-EGamma-RunB','18')
            cmd += ' ' + baseStr.format('Data-EGamma-RunC','18')
            cmd += ' ' + baseStr.format('Data-EGamma-RunD','18')
            ExecuteCmd('hadd -f %s %s'%(
                baseStr.format('Data','Run2'),
                cmd
            ))

def plot(tag,histname,fancyname):
    files = [f for f in glob('rootfiles/%s/HHstudies_*_Run2.root'%(tag)) if (('_GJets_' in f) or ('_ttbar_' in f) or ('Data_Run2' in f))]
    files.extend([f for f in glob('rootfiles/%s/HHstudies_*_17.root'%tag) if ('NMSSM-XToYHTo2g2b-MX-1200MY125' in f or 'NMSSM-XToYHTo2g2b-MX-1200MY250' in f)])
    hists = GetHistDict(histname,files)
    #colors = [colors_dict['GJets'],colors_dict['ttbar'],ROOT.kBlue,ROOT.kRed]
    colors = [colors_dict['ttbar'],colors_dict['GJets'],ROOT.kBlue,ROOT.kRed]
    EasyPlots('data_plots/%s/easy_%s_Run2.pdf'%(tag,histname),
              [hists['data']],
              bkglist=[[hists['bkg']['ttbar'],hists['bkg']['GJets']]],
              #bkglist=[[hists['bkg']['GJets'],hists['bkg']['ttbar']]],
              signals=[hists['sig']['NMSSM-XToYHTo2g2b-MX-1200MY125'],hists['sig']['NMSSM-XToYHTo2g2b-MX-1200MY250']],
              colors=colors,
              xtitle=fancyname,
              logy=True
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
        CombineCommonSets(args.tag,'GJets',True)
        CombineCommonSets(args.tag,'ttbar',True)
        CombineCommonSets(args.tag,'Data',True)

    histNames = {
        'mgg':'DiPhoton invariant mass m_{#gamma#gamma} (GeV)',
        'invm': 'M_{j#gamma#gamma}',
        'mjet':'Lead jet m_{SD} (GeV)',
    }

    import os
    os.system('mkdir -p data_plots/%s/'%args.tag)

    tempFile = ROOT.TFile.Open('rootfiles/%s/HHstudies_NMSSM-XToYHTo2g2b-MX-1200MY250_17.root'%args.tag,'READ')
    allValidationHists = [k.GetName() for k in tempFile.GetListOfKeys() if 'Idx' not in k.GetName()]
    for h in allValidationHists:
        if h in histNames.keys():
            print ('Plotting: %s'%h)
            plot(args.tag,h,histNames[h])
