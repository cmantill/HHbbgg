import glob,os,argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', dest='year', default='17', help='year split by commas')
    parser.add_argument('--files_per_job',dest='files_per_job', default=20, help='files per job')
    parser.add_argument('--samples',dest='samples',default=None,help='specify samples')
    parser.add_argument('--samplekey',dest='samplekey',default=None,help='specify matching sample key')
    parser.add_argument("--submit",dest='submit',action='store_true',help="submit jobs when created")
    args = parser.parse_args()

    outdir = f"/store/user/cmantill/HHbbgg/{args.tag}/"

    oname = 'condor/snapshot_args.txt'
    out = open(oname,'w')
    for year in args.year.split(','):
        for f in glob.glob(f'raw_nano/*_{year}.txt'):
            if os.path.getsize(f) == 0:
                print(f'File {f} is empty... Skipping.')
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
            njobs = int(nfiles/args.files_per_job)             
            for i in range(1,njobs+1):
                out.write(f'-s {setname} -y {year} -j {i} -n {njobs} \n')
    out.close()

    sh_templ_file = open(f"condor/run_snapshot.sh")
    localsh = f"condor/run_snapshot_{args.tag}.sh"
    sh_file = open(localsh, "w")
    for line in sh_templ_file:
        line = line.replace("DIRECTORY", outdir)
        sh_file.write(line)
    sh_file.close()
    sh_templ_file.close()

    if args.submit:
        os.system(f"mkdir -p /eos/uscms/{outdir}")
        os.system(f"mkdir -p /eos/uscms/{outdir}/snapshots/")
        os.system(f"mkdir -p /eos/uscms/{outdir}/cutflows/")
        cmd = f'python CondorHelper.py -r {localsh} -a {oname} -i "HHClass.py HHSnapshot.py helpers.py"'
        os.system(cmd)
