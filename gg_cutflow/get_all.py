from glob import glob
import subprocess, os
import json
from collections import OrderedDict

from TIMBER.Tools.Common import ExecuteCmd
redirector = 'root://cmseos.fnal.gov/'
eos_path = '/store/user/%s/HHbbgg/cutflows/'%os.getenv('USER')

files = subprocess.check_output('eos root://cmseos.fnal.gov ls %s'%(eos_path), shell=True)
org_files = {}
for f in files.split('\n'):
    if f == '': continue
    info = f.split('.')[0].split('_')
    setname = info[1]
    year = info[2]
    file_path = "/eos/uscms/"+eos_path+f

    if year not in org_files.keys():
        org_files[year] = {}
    if setname not in org_files[year].keys():
        org_files[year][setname] = []

    org_files[year][setname].append(file_path)
    
for y in org_files.keys():
    for s in org_files[y].keys():
        if s=="GJetsHT100-200": continue
        cutflow_dict = OrderedDict()
        for i,f in enumerate(org_files[y][s]):
            values = open(f).read().split()
            for j,v in enumerate(values):
                if (j % 2) != 0: continue
                if j == len(values)-1: break
                if i==0:
                    cutflow_dict[v] = float(values[j+1])
                else:
                    cutflow_dict[v] += float(values[j+1])
        out = open('gg_cutflow/%s_%s_cutflow.txt'%(s,y),'w')
        out.write(json.dumps(cutflow_dict))
        out.close()
