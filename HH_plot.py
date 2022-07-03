import multiprocessing
import argparse,os
from HH_studies import HHstudies
import ROOT
from TIMBER.Tools.Plot import CompareShapes

CommonSets = {
    "TTbar": [ROOT.kAzure-3,
              ["TTTo2L2Nu",
               "TTToHadronic",
               "TTToSemiLeptonic",
           ],
          ],
    "Diphoton": [ROOT.kGreen+2,
                 [
                     "DiPhotonJets-MGG-80toInf"
                 ],
             ],
}
colorsignal = {
    'MX700': ROOT.kBlue,
    'MX1000': ROOT.kOrange,
    'MX1200': ROOT.kGreen,
    'MX1400': ROOT.kRed,
    'MX1600': ROOT.kViolet,
    'MX1800': ROOT.kTeal,
    'MX2000': ROOT.kPink,
    'MX2500': ROOT.kCyan,
}


def GetProcYearFromTxt(filename):
    pieces = filename.split('/')[-1].split('.')[0].split('_')
    return pieces[0], pieces[1]
def GetProcYearFromROOT(filename):
    pieces = filename.split('/')[-1].split('.')[0].split('_')
    return pieces[1], pieces[2]

def multicore(tag,files=[],doStudies=True):
    pool = multiprocessing.Pool(processes=4 if doStudies else 6,maxtasksperchild=1)
    nthreads = 1
    process_args = []
    for f in files:
        setname, era = GetProcYearFromTxt(f)
        process_args.append(argparse.Namespace(threads=nthreads,setname=setname,era=era,tag=tag))
    pool.map(HHstudies,process_args)

def CombineCommonSets(tag,year,combine=False):
    common_sets = []
    remove_sets = []
    for key,setdict in CommonSets.items():
        baseStr = 'rootfiles/%s/HHstudies_%s_%s.root'%(tag,key,year)
        haddCmd = 'hadd -f %s'%baseStr
        for iset in setdict[1]:
            fname = 'rootfiles/%s/HHstudies_%s_%s.root'%(tag,iset,year)
            haddCmd += ' %s'%fname
            remove_sets.append(iset)
        if combine:
            os.system(haddCmd)
        common_sets.append(key)
    return common_sets,remove_sets

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
        if 'HH' in proc or 'NMSSM' in proc or 'XHY' in proc:
            all_hists['sig'][proc] = hist
        elif proc == 'Data':
            all_hists['data'] = hist
        else:
            all_hists['bkg'][proc] = hist
    return all_hists


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--recycle', dest='recycle',
                        action='store_true', default=False,
                        help='Recycle existing files and just plot.')
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    parser.add_argument('--sigbkg', action='store_true', help='Do sig and bkg plot')
    parser.add_argument('--sig', action='store_true', help='Do sig plot')
    args = parser.parse_args()
    
    year = "17"

    with open("HH_refs.txt") as f:
        sets = f.read().splitlines()

    names = {}; colors = {}
    for c in CommonSets.keys():
        names[c] = c
        colors[c] = CommonSets[c][0]
    to_color = {}
    for key in sets:
        if 'NMSSM' in key:
            mx = key.split('-')[2]
            my = key.split('-')[3]
        elif 'XHY' in key:
            mx = key.split('-')[1].replace('mx','MX')
            my = key.split('-')[2].replace('my','MY')
        else:
            continue
        if mx in to_color.keys():
            to_color[mx].append(key)
        else:
            to_color[mx] = [key]
        names[key] = '%s-%s'%(mx,my)

    for mx,keys in to_color.items():
        for i,key in enumerate(keys):
            colors[key] =colorsignal[mx]+i
            

    combine = False
    if not args.recycle:
        snapshot_files = ["gg_nano/%s/snapshots/%s_%s.txt"%(args.tag,s,year) for s in sets]
        multicore(args.tag,snapshot_files,doStudies=True) 
        combine = True
        
    common_sets,remove_sets = CombineCommonSets(args.tag,year,combine)
    sets.extend(common_sets)
    all_files = ["rootfiles/%s/HHstudies_%s_%s.root"%(args.tag,iset,year) for iset in sets if iset not in remove_sets]

    os.system('mkdir -p plots/%s'%args.tag)
    h = 'msd'
    hists = GetHistDict(h, all_files)
    print(hists["sig"].keys())

    if args.sigbkg:
        signals = ["NMSSM-XToYH-MX2000-MY250-HTo2gYTo2b"]
        signal = {key: val for key,val in hists["sig"].items() if key in signals}
        CompareShapes('plots/%s/%s_%s.pdf'%(args.tag,h,year),
                      "2017",
                      "Reg. Mass [GeV]",
                      bkgs=hists["bkg"],
                      signals=signal,
                      names=names,
                      colors=colors,
                      scale=False,
                      stackBkg=True,
                      doSoverB=True,
                      forceBackward=False,
                      logy=True
                  )
    if args.sig:
        sigtag = 'test'
        signals = {
            "MX2500-MY90": hists["sig"]["NMSSM-XToYH-MX2500-MY90-HTo2gYTo2b"],
            "MX2500-MY250": hists["sig"]["NMSSM-XToYH-MX2500-MY250-HTo2gYTo2b"],
        }
        CompareShapes('plots/%s/signal_%s_%s_%s.pdf'%(args.tag,h,year,sigtag),
                      "2017",
                      "Reg. Mass [GeV]",
                      signals=signals,
                      names=names,
                      colors=colors,
                      scale=True,
                      logy=False
                  )
