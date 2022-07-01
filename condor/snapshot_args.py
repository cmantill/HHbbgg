import glob,os

# a.k.a. UL v9 or pfnano
pfnano = [
    # "NMSSM-XToYHTo2g2b-MX-1200MY10",
    # "NMSSM-XToYHTo2g2b-MX-1200MY20",
    # "NMSSM-XToYHTo2g2b-MX-1200MY40",
    # "NMSSM-XToYHTo2g2b-MX-1200MY60",
    # "NMSSM-XToYHTo2g2b-MX-1200MY125",
    # "NMSSM-XToYHTo2g2b-MX-1200MY250",
    # "NMSSM-XToYHTo2g2b-MX-1200MY300",
    # "NMSSM-XToYHTo2g2b-MX-1200MY400",
    # "NMSSM-XToYHTo2g2b-MX-2000MY5",
    # "NMSSM-XToYHTo2g2b-MX-2000MY10",
    # "NMSSM-XToYHTo2g2b-MX-2000MY30",

    "NMSSM-XToYHTo2g2b-MX-1000MY800",
    "NMSSM-XToYHTo2g2b-MX-1000MY125",
    "NMSSM-XToYHTo2g2b-MX-1000MY60",
    "NMSSM-XToYHTo2g2b-MX-1000MY250",
    "NMSSM-XToYHTo2g2b-MX-700MY60",
    "NMSSM-XToYHTo2g2b-MX-700MY125",
    "NMSSM-XToYHTo2g2b-MX-2000MY60",
    "NMSSM-XToYHTo2g2b-MX-2000MY800",
    "NMSSM-XToYHTo2g2b-MX-2000MY250",
    "NMSSM-XToYHTo2g2b-MX-1400MY60",
    "NMSSM-XToYHTo2g2b-MX-1400MY500",

    "HHbbgg-cHH1",

    "TTTo2L2Nu",
    "TTToSemiLeptonic",
    "TTToHadronic",

    "DiPhotonJets-MGG-80toInf",
    "GJetPt20to40DoubleEMEnriched-MGG80toInf",
    "GJetPt40toInfDoubleEMEnriched-MGG80toInf",
    "GJetsHT100-200",
    "GJetsHT200-400",
    "GJetsHT400-600",
    "GJetsHT600-Inf",

    "Data-DoubleEG-RunB",
    "Data-DoubleEG-RunC",
    "Data-DoubleEG-RunD",
    "Data-DoubleEG-RunE",
    "Data-DoubleEG-RunF",

    "Data-DoubleEG-RunBv1HIPM",
    "Data-DoubleEG-RunBv2HIPM",
    "Data-DoubleEG-RunCHIPM",
    "Data-DoubleEG-RunDHIPM",
    "Data-DoubleEG-RunEHIPM",
    "Data-DoubleEG-RunFHIPM",
    "Data-DoubleEG-RunG",
    "Data-DoubleEG-RunH",

    "Data-EGamma-RunA",
    "Data-EGamma-RunB",
    "Data-EGamma-RunC",
    "Data-EGamma-RunD",
]

oname = 'condor/snapshot_args.txt'
out = open(oname,'w')
years = ["17"]
#years = ["16","18"]

for f in glob.glob('raw_nano/*.txt'):
    if os.path.getsize(f) == 0:
        print ('File %s is empty... Skipping.'%(f))
        continue
    filename = f.split('/')[-1].split('.')[0]
    nfiles = len(open(f,'r').readlines())
    setname = filename.split('_')[0]
    year = filename.split('_')[1]
    if year not in years: 
        print(year,f)
        continue

    #if 'NMSSM' in setname or 'HHbbgg' in setname:
    #    njobs = 1
    #else:
    njobs = int(nfiles/20) 

    print(setname)
    for i in range(1,njobs+1):
        #if setname in pfnano:
        #if ('TTTo' not in setname) and ('GJetPt' not in setname) and ('DiPhoton' not in setname): continue
        #if ('Data' not in setname) and ('NMSSM' not in setname) and ('HHbbgg' not in setname): continue
        #if ('HHbbgg' not in setname) and ('GJets' not in setname): continue
        if ('NMSSM' not in setname and 'XHY' not in setname): continue
        out.write('-s %s -y %s -j %s -n %s --pfnano \n'%(setname,year,i,njobs))
        #else:
        #continue
        #out.write('-s %s -y %s -j %s -n %s \n'%(setname,year,i,njobs))

out.close()
