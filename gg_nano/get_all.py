import os
from glob import glob
import subprocess,os,argparse,json
from collections import OrderedDict

from TIMBER.Tools.Common import ExecuteCmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--idir', default='/store/user/%s/HHbbgg/'%os.getenv('USER'), help='Input directory w snapshots')
    parser.add_argument('--odir', default='', help='Output directory')
    args = parser.parse_args()

    redirector = 'root://cmseos.fnal.gov/'

    os.system('mkdir -p gg_nano/%s'%args.odir)
    
    for key in ["snapshots","cutflows"]:
        os.system('mkdir -p gg_nano/%s/%s'%(args.odir,key))

        files = subprocess.check_output('eos %s ls %s/%s/'%(redirector,args.idir,key), shell=True)
        org_files = {}
        for f in files.split('\n'):
            if f == '': continue
            info = f.split('.')[0].split('_')
            setname = info[1]
            year = info[2]
            if year not in org_files.keys():
                org_files[year] = {}
            if setname not in org_files[year].keys():
                org_files[year][setname] = []
            if key=="cutflows":
                file_path = "/eos/uscms/%s/%s/%s"%(args.idir,key,f)
            else:
                file_path = "%s/%s/%s/%s"%(redirector,args.idir,key,f)
            org_files[year][setname].append(file_path)
    
        for y in org_files.keys():
            for s in org_files[y].keys():
                out = open('gg_nano/%s/%s/%s_%s.txt'%(args.odir,key,s,y),'w')
                if key=="cutflows":
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
                    out.write(json.dumps(cutflow_dict))
                else:
                    for f in org_files[y][s]:
                        out.write(f+'\n')
                out.close()
