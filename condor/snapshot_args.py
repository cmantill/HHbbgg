import glob,os,argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', dest='year', default='17', help='year split by commas')
    parser.add_argument('--files_per_job',dest='files_per_job', default=20, help='files per job')
    parser.add_argument('--samples',dest='samples',default=None,help='specify samples')
    parser.add_argument('--samplekey',dest='samplekey',default=None,help='specify matching sample key')
    parser.add_argument("--submit",dest='submit',action='store_true',help="submit jobs when created")
    parser.add_argument('--tag', type=str, dest='tag',
                        action='store', default='test',
                        help='Tag to identify study')
    args = parser.parse_args()

    outdir = "/store/user/cmantill/HHbbgg/%s/"%args.tag

    oname = 'condor/snapshot_args.txt'
    out = open(oname,'w')
    for year in args.year.split(','):
        for f in glob.glob('raw_nano/*_%s.txt'%year):
            if os.path.getsize(f) == 0:
                print('File %s is empty... Skipping.'%f)
                continue
            filename = f.split('/')[-1].split('.')[0]
            setname = filename.split('_')[0]
            if args.samples is not None:
                if setname not in args.samples.split(','):
                    continue
            if args.samplekey is not None:
                if args.samplekey not in setname:
                    continue

            nfiles = len(open(f,'r').readlines())
            njobs = int(nfiles/int(args.files_per_job))
            for i in range(1,njobs+1):
                out.write('-s %s -y %s -j %i -n %i \n'%(setname,year,i,njobs))
    out.close()

    sh_templ_file = open("condor/run_snapshot.sh")
    localsh = "condor/run_snapshot_%s.sh"%args.tag
    sh_file = open(localsh, "w")
    for line in sh_templ_file:
        line = line.replace("DIRECTORY", outdir)
        sh_file.write(line)
    sh_file.close()
    sh_templ_file.close()

    if args.submit:
        os.system("mkdir -p /eos/uscms/%s"%outdir)
        os.system("mkdir -p /eos/uscms/%s/snapshots/"%outdir)
        os.system("mkdir -p /eos/uscms/%s/cutflows/"%outdir)
        cmd = 'python CondorHelper.py -r %s -a %s -i "HH_class.py HH_snapshot.py helpers.py"'%(localsh,oname)
        print(cmd)
        os.system(cmd)
