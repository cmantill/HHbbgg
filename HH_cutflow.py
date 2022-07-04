import ROOT

from TIMBER.Analyzer import HistGroup, Correction
from TIMBER.Tools.Common import CompileCpp
ROOT.gROOT.SetBatch(True)

import os,json

from HH_class import HHClass
from collections import OrderedDict

def HHcutflow(args):
    print ('PROCESSING: %s %s'%(args.setname, args.era))
    ROOT.ROOT.EnableImplicitMT(args.threads)

    fcutflow_old = "gg_nano/%s/cutflows/%s_%s.txt"%(args.tag,args.setname, args.era)
    cutflow_dict = json.load(open(fcutflow_old), object_pairs_hook=OrderedDict)
    if cutflow_dict["diphoton_eveto"]<=0:
        print(cutflow_dict["diphoton_eveto"])
        return None

    mh = 125
    if 'NMSSM' in args.setname:
        mh = int(args.setname.split('-')[3].replace('MY',''))
    if 'XHY-' in args.setname:
        mh = int(args.setname.split('-')[2].replace('my',''))

    hh = HHClass('gg_nano/%s/snapshots/%s_%s.txt'%(args.tag,args.setname,args.era),int(args.era),1,1,mh=mh,silent=True)
    hh.Selection(xbb_cut=0.9)
    xweight = hh.a.GetActiveNode().DataFrame.Mean("weight__nominal").GetValue()

    fcutflow_old = "gg_nano/%s/cutflows/%s_%s.txt"%(args.tag,args.setname, args.era)
    old_dict = json.load(open(fcutflow_old), object_pairs_hook=OrderedDict)
    for key,value in old_dict.items():
        if 'sel' in key: continue
        if 'weight' in key: continue
        old_dict[key+'-weight'] = value*xweight
        
    for key,v in hh.GetCutflowDict().items():
        if key!= "Initial":
            old_dict['sel-'+key] = v
            old_dict['sel-'+key+'-weight'] = v*xweight
        
    # print(old_dict)
    out = open(fcutflow_old,'w')
    out.write(json.dumps(old_dict))
    out.close() 
    print('Saved cutflow in ',fcutflow_old)
    
    return old_dict

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-y', type=str, dest='era',
                        action='store', required=True,
                        help='Year of set (16, 17, 18).')
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    args = parser.parse_args()
    args.threads = 1
        
    with open("HH_refs.txt") as f:
        sets = f.read().splitlines()

    efficiencies = {}
    for nset in sets:
        print(nset)
        args.setname = nset
        cutflow_dict = HHcutflow(args)
        if cutflow_dict is not None:
            efficiencies[nset] = cutflow_dict['sel-mbb_window']/cutflow_dict['Initial']

    print(efficiencies)
