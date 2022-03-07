#cd $CMSSW_BASE/../
cd /uscms/home/cmantill/nobackup/timber/hhbbgg/CMSSW_11_1_4/../
tar --exclude-caches-all --exclude-vcs --exclude-caches-all --exclude-vcs -cvzf CMSSW_11_1_4.tgz CMSSW_11_1_4 --exclude=tmp --exclude=".scram" --exclude=".SCRAM" --exclude=CMSSW_11_1_4/src/timber-env --exclude=CMSSW_11_1_4/src/HHbbgg/*.root --exclude=CMSSW_11_1_4/src/BstarToTW_CMSDAS2022/ --exclude=CMSSW_11_1_4/src/TIMBER/docs --exclude=CMSSW_11_1_4/src/HHbbgg/plots --exclude=CMSSW_11_1_4/src/HHbbgg/logs --exclude=CMSSW_11_1_4/src/HHbbgg/rootfiles --exclude=CMSSW_11_1_4/src/HHbbgg/gg_nano
xrdcp -f CMSSW_11_1_4.tgz root://cmseos.fnal.gov//store/user/$USER/CMSSW_11_1_4.tgz
cd /uscms/home/cmantill/nobackup/timber/hhbbgg/CMSSW_11_1_4/src/HHbbgg/
#cd $CMSSW_BASE/src/HHbbgg/
