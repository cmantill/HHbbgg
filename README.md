# X to H(bb)Y(gg)

Using RDataFrames and TIMBER to interface nanoAOD.

## Filesets

Lists of nanoAODs are contained in `raw_nano/`.
All of the samples are NanoAODv9, except for:
```
HHbbgg-cHH1 (producing privately now)
XHY_mx*
```

## HH_class

The class `HHClass` contains all the pre-selection and final-selection for the snapshots.

## Snapshots

Snapshots contain compressed info from nanoAOD defined in HHClass.

To run snapshot locally:
```
python HH_snapshot.py -s NMSSM-XToYH-MX2500-MY600-HTo2gYTo2b -y 17 -j 1 -n 1
```

### Running in condor

Get condor arguments:
```
python condor/snapshot_args.py 
```

Run condor jobs:
python CondorHelper.py -r condor/run_snapshot.sh -a condor/snapshot_test_args.txt -i "HHClass.py HHSnapshot.py helpers.py"
python CondorHelper.py -r condor/run_snapshot.sh -a condor/snapshot_args.txt -i "HHClass.py HHSnapshot.py helpers.py"
```

## Summarize snapshots

Get list of snapshots and cutflows:
```
python gg_nano/get_all.py
python gg_cutflow/get_all.py
```

