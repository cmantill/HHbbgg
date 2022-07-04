sig_dict = {
    700: [60,125,250], 
    1000: [60,90,125,250,300], # 800
    1200: [60,90,125,250,300],
    1400: [60,90,125,250,300,400,500],
    1600: [60,90,125,250,300,400,600],
    1800: [60,90,125,250,300,400,500,600,700],
    2000: [60,90,125,250,300,400,500,800,1000,1200],
    2500: [60,90,250,300,400,500,600,700,800,1000,1200],
}

signal_sets = []
for mx,mys in sig_dict.items():
    for my in mys:
        sig_str = "NMSSM-XToYH-MX%s-MY%s-HTo2gYTo2b"%(mx,my)
        signal_sets.append(sig_str)

other_sig_dict = {
    1200: [10,20,40,60,250,300],
    2000: [5,10,20],
}

other_signal_sets = []
for mx,mys in other_sig_dict.items():
    for my in mys:
        sig_str = "XHY-mx%s-my%s"%(mx,my)
        other_signal_sets.append(sig_str)

bkg_sets = [
    "GJet-Pt-20to40-MGG-80toInf",
    "GJet-Pt-20toInf-MGG-40to80",
    "GJet-Pt-40toInf-MGG-80toInf",
    "DiPhotonJets-MGG-80toInf",
    "TTTo2L2Nu",
    "TTToHadronic",
    "TTToSemiLeptonic",
    "QCD-Pt-30toInf-DoubleEMEnriched-MGG-40to80",
    "QCD-Pt-40ToInf-DoubleEMEnriched-MGG-80ToInf",
    "VBFHToBB-M-125",
    "ggZH-HToBB-ZToQQ-M-125",
    "WminusH-HToBB-WToQQ-M-125",
    "WplusH-HToBB-WToQQ-M-125",
    "ZH-HToBB-ZToQQ-M-125",
    "GluGluHToBB-Pt-200ToInf-M-125",
    "VBFHToGG-M125",
    "GluGluHToGG-M125",
]

sets = []
sets.extend(signal_sets)
# sets.extend(other_signal_sets)
sets.extend(bkg_sets)

with open("HH_refs.txt","w") as f:
    for iset in sets:
        f.write('%s\n'%iset)
