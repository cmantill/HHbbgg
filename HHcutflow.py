from collections import OrderedDict

cutflow_dict = OrderedDict()
fname = "/eos/uscms/store/user/cmantill/HHbbgg/snapshots/HHcutflow_TTTo2L2Nu_17_3of19.txt"
values = open(fname).read().split()
for i,v in enumerate(values):
    if i == len(values)-1: break
    cutflow_dict[v] = values[i+1]

print(cutflow_dict)



