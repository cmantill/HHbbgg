tag=$1

python HHstudies.py -s GJetsHT100-200 -y 17 --tag $tag
python HHstudies.py -s GJetsHT200-400 -y 17 --tag $tag
python HHstudies.py -s GJetsHT400-600 -y 17 --tag $tag
python HHstudies.py -s GJetsHT600-Inf -y 17 --tag $tag

python HHstudies.py -s GJetPt40toInfDoubleEMEnriched-MGG80toInf -y 17 --tag $tag
python HHstudies.py -s GJetPt20to40DoubleEMEnriched-MGG80toInf -y 17 --tag $tag 
python HHstudies.py -s DiPhotonJets-MGG-80toInf -y 17 --tag $tag
python HHstudies.py -s TTToHadronic -y 17 --tag $tag
python HHstudies.py -s TTTo2L2Nu -y 17 --tag $tag
python HHstudies.py -s TTToSemiLeptonic -y 17 --tag $tag

python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY125 -y 17 --tag $tag
python HHstudies.py -s NMSSM-XToYHTo2g2b-MX-1200MY250 -y 17 --tag $tag
python HHstudies.py -s HHbbgg-cHH1 -y 17 --tag $tag

python HHstudies.py -s Data-DoubleEG-RunB -y 17 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunC -y 17 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunD -y 17 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunE -y 17 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunF -y 17 --tag $tag

python HHstudies.py -s Data-DoubleEG-RunBv1HIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunBv2HIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunCHIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunDHIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunEHIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunFHIPM -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunF -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunG -y 16 --tag $tag
python HHstudies.py -s Data-DoubleEG-RunH -y 16 --tag $tag

python HHstudies.py -s Data-EGamma-RunA -y 18 --tag $tag
python HHstudies.py -s Data-EGamma-RunB -y 18 --tag $tag
python HHstudies.py -s Data-EGamma-RunC -y 18 --tag $tag
python HHstudies.py -s Data-EGamma-RunD -y 18 --tag $tag
