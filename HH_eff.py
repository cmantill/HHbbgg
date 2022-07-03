import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mplhep as hep
plt.style.use(hep.style.CMS)
plt.rcParams.update({'font.size': 32})
import argparse,json
from collections import OrderedDict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    cuts = {
        '2 photons': ['nphotons','Initial'],
        '2 jets': ['njets','nphotons'],
        'Jet kin': ['fatjet_kin','njets'],
        'Xbb>0.8': ['fatjet_xbb','fatjet_kin'],
        'Photon kin': ['diphoton_kin','fatjet_xbb'],
        'Photon Electron veto': ['diphoton_eveto','diphoton_kin'],
        'Pt Photon/Mgg': ['ptphoton_over_mgg','diphoton_eveto'],
        #'MET': ['metcut','ptphoton_over_mgg'],
        #'Pt Photons': ['sel-pt_photons','metcut'],
        'Photon away from jet': ['sel-photonsawayjet','sel-pt_photons'],
        'No btag away': ['sel-nobtagsaway','sel-photonsawayjet'],
        'PN > 0.9': ['sel-SelFatJet_Xbb','sel-nobtagsaway'],
        'Mbb window': ['sel-mbb_window','sel-SelFatJet_Xbb'],
    }
    cutflow_path = 'gg_nano/Jun28/cutflows/'
    era = '17'

    mX_mY_efficiencies = {}

    sig_sets = [f"NMSSM-XToYH-MX1000-MY{my}-HTo2gYTo2b" for my in [60,90,125,250,300,800]]

    fig, axs = plt.subplots(1,1,figsize=(10,8))     
    eff = {}
    for iset in sig_sets:  
        eff[iset] = {}                                                                                                                                                                                                                      
        for cut,cdict in cuts.items():
            dcut = cdict[0]
            icut = cdict[1]
            fcutflow = f"{cutflow_path}/{iset}_{era}.txt"
            old_dict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
            # eff[iset][cut] = old_dict[dcut]/old_dict[icut]
            eff[iset][cut] = old_dict[dcut]/old_dict['Initial']
    """
        for mx,mys in sig_dict.items():
            mX_mY_efficiencies[mx] = {}
            for my in mys:
                fcutflow = f"{cutflow_path}/NMSSM-XToYH-MX{mx}-MY{my}-HTo2gYTo2b_{era}.txt"
                old_dict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
                # print(old_dict.keys(),fcutflow)
                # print(mx,my,old_dict[dcut],old_dict[icut])
                # mX_mY_efficiencies[mx][my] = old_dict['sel-mbb_window']/old_dict['Initial']
                try:
                    mX_mY_efficiencies[mx][my] = old_dict[dcut]/old_dict[icut]
                except:
                    print('skipping ',dcut,icut,' for ',mx,' ',my)

        fig, axs = plt.subplots(1,1,figsize=(10,8))
        for mX,mYdict in mX_mY_efficiencies.items():
            x = [int(k) for k in mYdict.keys()]
            y = list(mYdict.values())
            print(x,y,mX)
            axs.plot(x,y,marker='o',label=r'$m_{X}$='f'{mX}')
    """
    x = list(cuts.keys())
    for iset in eff.keys():
        y = list(eff[iset].values())
        #leg = f"{iset}"
        leg = iset.replace('NMSSM-XToYH-','').replace('-HTo2gYTo2b','')
        axs.plot(x,y,marker='o',label=f'{leg}')
    axs.legend()
    for tick in axs.get_xticklabels():
        tick.set_rotation(70)
    # axs.set_xlabel(r'$m_{Y}$ [GeV]')
    axs.set_ylabel('Signal efficiency')
    axs.set_yscale('log')
    # axs.set_title(f'{cut}')
    fig.tight_layout()
    fig.savefig(f'eff/sigMY1000_efficiency_all_vs_initial.png')
