import glob,os

NMSSM = False
oname = 'condor/snapshot_args.txt'
if NMSSM:
    oname = 'condor/snapshot_NMSSM_args.txt'
    nmssm_dict = {
        #300: [60,70,80,90,100,125,150,200],
        #400: [60,70,80,90,100,125,150,200,250],
        #500: [60,70,80,90,100,125,150,200,250,300],
        #600: [60,70,80,90,100,125,150,200,250,300,400],
        #700: [60,70,80,90,100,125,150,200,250,300,400,500],
        #800: [60,70,80,90,100,125,150,200,250,300,400,500,600],
        #900: [60,70,80,90,100,125,150,200,250,300,400,500,600,700],
        #1000: [60,70,80,90,100,125,150,200,250,300,400,500,600,700,800],
        1200: [60,400],
    }

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

    if NMSSM:
        if 'NMSSM' in setname:
            for key,krange in nmssm_dict.items():
                if str(key) in setname:
                    for kk in krange:
                        out.write('-s %s -y %s --ss %i\n'%(setname,year,kk))
    else:
        #if 'GluGluToRadionToHH' in setname:
        #    out.write('-s %s -y %s\n'%(setname,year))
        #if 'NMSSM' in setname:
        #    continue
        print(setname)
        #if ('DiPhotonJets' not in setname) and ('GJetPt' not in setname) and ('NMSSM-XToYHTo2g2b' not in setname): continue
        #if ('GJetPt' not in setname): continue
        if ('NMSSM-XToYHTo2g2b-MX-1200MY125' not in setname) and ('NMSSM-XToYHTo2g2b-MX-1200MY300' not in setname) and ('HHbbgg-' not in setname) and ('QCD' not in setname): continue  
        njobs = int(nfiles/2)
        for i in range(1,njobs+1):
            #out.write('-s %s -y %s -j %s -n %s \n'%(setname,year,i,njobs))
            out.write('-s %s -y %s -j %s -n %s --pfnano \n'%(setname,year,i,njobs))
out.close()
