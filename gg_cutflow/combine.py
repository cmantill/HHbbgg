import json
from collections import OrderedDict

#tag = "preSel_Mar8"
#tag = "SR_Mar8"
#tag = "tight_Mar8"
tag = "SR_Mar20_sig"

era = "17"
combine_dict = {
    "Hbb": [
        "ggH-HtoBB",
        "VBF-HtoBB",
        "ttH-HtoBB",
    ],
    "GJets": [
        "GJetPt40toInfDoubleEMEnriched-MGG80toInf",
        "DiPhotonJets-MGG-80toInf",
        "GJetsHT200-400",
        "GJetsHT400-600",
        "GJetsHT600-Inf",
    ],
    "TTbar": [
        "TTToHadronic",
        "TTTo2L2Nu",
        "TTToSemiLeptonic",
    ],
    "QCD": [
        "QCDHT2000toInf",
        "QCDHT700to1000",
        "QCDHT1000to1500",
        "QCDHT1500to2000"
    ],
}
for sample,files in combine_dict.items():
    new_dict = {}
    for subs in files:
        fcutflow = "gg_cutflow/%s/%s_%s_cutflow.txt"%(tag,subs,era)
        fdict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
        for key,v in fdict.items():
            if key not in new_dict.keys():
                new_dict[key] = v
            else:
                new_dict[key] += v
    out = open('gg_cutflow/%s/%s_%s_cutflow.txt'%(tag,sample,era),'w')
    out.write(json.dumps(new_dict))
    out.close()
