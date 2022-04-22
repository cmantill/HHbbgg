import ROOT, time
ROOT.gROOT.SetBatch(True)
from TIMBER.Tools.Common import CompileCpp
from argparse import ArgumentParser
from HHClass import HHClass

parser = ArgumentParser()
parser.add_argument('-s', type=str, dest='setname',
                    action='store', required=True,
                    help='Setname to process.')
parser.add_argument('-y', type=str, dest='era',
                    action='store', required=True,
                    help='Year of set (16, 17, 18).')
parser.add_argument('-j', type=int, dest='ijob',
                    action='store', default=1,
                    help='Job number')
parser.add_argument('-n', type=int, dest='njobs',
                    action='store', default=1,
                    help='Number of jobs')
parser.add_argument('--ss', type=str, dest='samplestr',
                    action='store', default='',
                    help='Multi sample str')
parser.add_argument('--pfnano', action='store_true', dest='pfnano',
                    help='is pfnano')
args = parser.parse_args()

start = time.time()

selection = HHClass('raw_nano/%s_%s.txt'%(args.setname,args.era),int(args.era),args.ijob,args.njobs,args.samplestr,args.pfnano)
selection.ApplyKinematicsSnap()
out = selection.ApplyStandardCorrections(snapshot=True)
selection.Snapshot(out)
selection.GetCutflow("HHcutflow_%s_%s_%iof%i.txt"%(args.setname,args.era,args.ijob,args.njobs))

print ('%s sec'%(time.time()-start))
