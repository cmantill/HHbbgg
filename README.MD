## XtoHYbbgg

Locally
```
python HHSnapshot.py -s GluGluToRadionToHHTo2B2G-1000 -y 16 -j 1 -n 1
python HHstudies.py -s GluGluToRadionToHHTo2B2G-1000 -y 16 

python HHSnapshot.py -s NMSSM-XToYHTo2b2g-MX-1000 -y 16 -j 0 -n 1 --ss 100
```

In condor:
```
python CondorHelper.py -r condor/run_snapshot.sh -a condor/snapshot_test_args.txt -i "HHClass.py HHSnapshot.py helpers.py"
python CondorHelper.py -r condor/run_snapshot.sh -a condor/snapshot_args.txt -i "HHClass.py HHSnapshot.py helpers.py"
```