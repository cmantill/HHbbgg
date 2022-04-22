#tag="preSel_Mar20" #w/o btag and dr cut
tag="SR_Mar20_sig"
#tag="tight_Mar20"
python HHstudies.py -s GJetsHT100-200 -y 17 --tag $tag
python HHstudies.py -s GJetsHT200-400 -y 17 --tag $tag
python HHstudies.py -s GJetsHT400-600 -y 17 --tag $tag
python HHstudies.py -s GJetsHT600-Inf -y 17 --tag $tag 
# python HHstudies.py -s GJetPt40toInfDoubleEMEnriched-MGG80toInf -y 17 --tag $tag
# python HHstudies.py -s GJetPt20to40DoubleEMEnriched-MGG80toInf -y 17 --tag $tag 
# python HHstudies.py -s DiPhotonJets-MGG-80toInf -y 17 --tag $tag
# python HHstudies.py -s ggH-HtoBB -y 17 --tag $tag
# python HHstudies.py -s ZH-HtoBB-ZtoQQ -y 17 --tag $tag
# python HHstudies.py -s WplusH-HToBB-WtoQQ -y 17 --tag $tag
# python HHstudies.py -s ggZH-HtoBB-ZtoQQ -y 17 --tag $tag
# python HHstudies.py -s VBF-HtoBB -y 17 --tag $tag
# python HHstudies.py -s WminusH-HToBB-WtoQQ -y 17 --tag $tag
# python HHstudies.py -s ttH-HtoBB -y 17 --tag $tag
# python HHstudies.py -s TTToHadronic -y 17 --tag $tag
# python HHstudies.py -s TTTo2L2Nu -y 17 --tag $tag
# python HHstudies.py -s TTToSemiLeptonic -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY125 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY20 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY400 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-2000MY5 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-2000MY10 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY10 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY40 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY250 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-2000MY20 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY60 -y 17 --tag $tag
# python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY300 -y 17 --tag $tag
# python HHstudies.py -s HHbbgg-cHH1 -y 17 --tag $tag
# python HHstudies.py -s QCDHT1000to1500 -y 17 --tag $tag
# python HHstudies.py -s QCDHT1500to2000 -y 17 --tag $tag
# python HHstudies.py -s QCDHT2000toInf -y 17 --tag $tag
# python HHstudies.py -s QCDHT700to1000 -y 17 --tag $tag
