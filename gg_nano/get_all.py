from glob import glob
import subprocess, os,argparse

from TIMBER.Tools.Common import ExecuteCmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--idir', default='/store/user/%s/HHbbgg/'%os.getenv('USER'), help='Input directory w snapshots')
    parser.add_argument('--odir', default='', help='Output directory')
    args = parser.parse_args()

    redirector = 'root://cmseos.fnal.gov/'
    
    for key in ["snapshots","cutflows"]:
        files = subprocess.check_output('eos %s ls %s'%(redirector,eos_path), shell=True)
        org_files = {}
        for f in files.split('\n'):
            if f == '': continue
            info = f.split('.')[0].split('_')
            setname = info[1]
            year = info[2]
            file_path = redirector+eos_path+f
            
            if year not in org_files.keys():
                org_files[year] = {}
            if setname not in org_files[year].keys():
                org_files[year][setname] = []
            
            org_files[year][setname].append(file_path)
    
        for y in org_files.keys():
            for s in org_files[y].keys():
                if s=="GJetsHT100-200": continue
                out = open('gg_nano/%s_%s_%s.txt'%(s,y,key),'w')
                for f in org_files[y][s]:
                    out.write(f+'\n')
                out.close()
