import glob,os

pfnano = [
    "NMSSM-XToYHTo2g2b-MX-1200MY10",
    "NMSSM-XToYHTo2g2b-MX-1200MY20",
    "NMSSM-XToYHTo2g2b-MX-1200MY40",
    "NMSSM-XToYHTo2g2b-MX-1200MY60",
    "NMSSM-XToYHTo2g2b-MX-1200MY125",
    "NMSSM-XToYHTo2g2b-MX-1200MY250",
    "NMSSM-XToYHTo2g2b-MX-1200MY300",
    "NMSSM-XToYHTo2g2b-MX-1200MY400",
    "NMSSM-XToYHTo2g2b-MX-2000MY5",
    "NMSSM-XToYHTo2g2b-MX-2000MY10",
    "NMSSM-XToYHTo2g2b-MX-2000MY30",
    "HHbbgg-cHH1"
    "TTTo2L2Nu",
    "TTToSemiLeptonic",
    "TTToHadronic",
    "DiPhotonJets-MGG-80toInf",
    "GJetPt20to40DoubleEMEnriched-MGG80toInf",
    "GJetPt40toInfDoubleEMEnriched-MGG80toInf",
]

oname = 'condor/snapshot_args.txt'
out = open(oname,'w')
for f in glob.glob('raw_nano/*.txt'):
    if os.path.getsize(f) == 0:
        print ('File %s is empty... Skipping.'%(f))
        continue
    filename = f.split('/')[-1].split('.')[0]
    nfiles = len(open(f,'r').readlines())
    setname = filename.split('_')[0]
    year = filename.split('_')[1]
    if year == '16' or year == '18': 
        continue

    #if 'GluGluToRadionToHH' in setname:
    #    out.write('-s %s -y %s\n'%(setname,year))
    #if 'NMSSM' in setname:
    #    continue
    #if ('DiPhotonJets' not in setname) and ('GJetPt' not in setname) and ('NMSSM-XToYHTo2g2b' not in setname): continue
    #if ('DiPhotonJets' not in setname): continue
    #if ('QCD' not in setname): continue
    #if ('NMSSM-XToYHTo2g2b-MX-1200MY125' in setname) or ('NMSSM-XToYHTo2g2b-MX-1200MY300' in setname) or ('HHbbgg-' in setname) or ('QCD' in setname): continue  

    if 'NMSSM' in setname or 'HHbbgg' in setname:
        njobs = 1
    else:
        njobs = int(nfiles/2) 
    for i in range(1,njobs+1):
        if setname in pfnano:
            #if ('TTTo' not in setname) and ('NMSSM' not in setname): continue
            if ('NMSSM' not in setname): continue
            out.write('-s %s -y %s -j %s -n %s --pfnano \n'%(setname,year,i,njobs))
        else:
            continue
            out.write('-s %s -y %s -j %s -n %s \n'%(setname,year,i,njobs))

out.close()
