sig_dict = {
    700: [125,250], #60                                                                                                                                                                                                                                                     
    1000: [90,125,250], # 60,300,800                                                                                                                                                                                                                                        
    1200: [90,125], # 300                                                                                                                                                                                                                                                   
    1400: [90,250], # 60,400,500                                                                                                                                                                                                                                            
    1600: [90,250], # 60,400,600                                                                                                                                                                                                                                            
    1800: [90,125,250], # 300,400,500                                                                                                                                                                                                                                       
    2000: [250], # 60,500,800,1000,1200,1400                                                                                                                                                                                                                                
    2500: [90,250], # 300,400,500,600,700,800,1000,1200,1400,1800                                                                                                                                                                                                           
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
    #"GJetPt20to40DoubleEMEnriched-MGG80toInf",                                                                                                                                                                                                                             
    #"GJetPt40toInfDoubleEMEnriched-MGG80toInf",
    "DiPhotonJets-MGG-80toInf",
    "TTTo2L2Nu",
    "TTToHadronic",
    "TTToSemiLeptonic",
]

sets = []
sets.extend(signal_sets)
sets.extend(other_signal_sets)
sets.extend(bkg_sets)

with open("HH_refs.txt","w") as f:
    for iset in sets:
        f.write('%s\n'%iset)
