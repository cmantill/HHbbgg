#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/cmantill/CMSSW_11_1_4.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
scramv1 project CMSSW CMSSW_11_1_4
tar -xzvf CMSSW_11_1_4.tgz
rm CMSSW_11_1_4.tgz
rm *.root

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_1_4/src/HHbbgg/; cd ../CMSSW_11_1_4/src/
echo 'IN RELEASE'
pwd
ls
eval `scramv1 runtime -sh`
rm -rf timber-env
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ../HHbbgg

echo python HHSnapshot.py $*
python HHSnapshot.py $*

xrdcp -f HHsnapshot_*.root root://cmseos.fnal.gov//store/user/cmantill/HHbbgg/snapshots/

