import json
from collections import OrderedDict

#tag = "SR_May2_mbbveto"
tag = "SR_May2_mbbwindow_mggvetodata"

combine_dict = {
    "GJets": {
        "17": [
            #"GJetPt20to40DoubleEMEnriched-MGG80toInf",
            "GJetPt40toInfDoubleEMEnriched-MGG80toInf",
            "DiPhotonJets-MGG-80toInf",
            "GJetsHT200-400",
            "GJetsHT400-600",
            "GJetsHT600-Inf",
        ],
    },
    "TTbar": {
        "17": [
            "TTToHadronic",
            "TTTo2L2Nu",
            "TTToSemiLeptonic",
        ],
    },
    "Data": {
        "16": [
            "Data-DoubleEG-RunBv2HIPM",
            "Data-DoubleEG-RunCHIPM",
            "Data-DoubleEG-RunDHIPM",
            "Data-DoubleEG-RunEHIPM",
            "Data-DoubleEG-RunFHIPM",
            "Data-DoubleEG-RunF",
            "Data-DoubleEG-RunG",
            "Data-DoubleEG-RunH",
        ],
        "17": [
            "Data-DoubleEG-RunB",
            "Data-DoubleEG-RunC",
            "Data-DoubleEG-RunD",
            "Data-DoubleEG-RunE",
            "Data-DoubleEG-RunF",
        ],
        "18": [
            "Data-EGamma-RunA",
            "Data-EGamma-RunB",
            "Data-EGamma-RunC",
            "Data-EGamma-RunD",
        ],
    },
    "HH": {
        "17": [
            "HHbbgg-cHH1",
        ],
    },
    "XHY-MX1200-MY125": {
        "17": [
            "NMSSM-XToYHTo2g2b-MX-1200MY125",
        ]
    },
    "XHY-MX1200-MY250": {
        "17": [
            "NMSSM-XToYHTo2g2b-MX-1200MY250",
        ]
    },
}

cuts = [
    "Initial",
    "nphotons",
    "njets",
    "fatjet_kin",
    "fatjet_xbb",
    "diphoton_kin",
    "diphoton_eveto",
    "ptphoton_over_mgg",
    "metcut",
    "photonsawayjet",
    "nobtagsaway",
    "SelFatJet_Xbb_tight",
    "mbb_window",
    #"mbb_veto",
]

for sample,ydict in combine_dict.items():
    new_dict = {}
    for era,files in ydict.items():
        for subs in files:
            fcutflow = "gg_cutflow/%s/%s_%s_cutflow.txt"%(tag,subs,era)
            fdict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
            for key,v in fdict.items():
                if key not in new_dict.keys():
                    new_dict[key] = v
                else:
                    new_dict[key] += v
    out = open('gg_cutflow/%s/%s_cutflow.txt'%(tag,sample),'w')
    out.write(json.dumps(new_dict))
    out.close()
    print(sample)
    for cut in cuts:
        try:
            print(cut,new_dict[cut])
        except:
            pass
