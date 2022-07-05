import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mplhep as hep
plt.style.use(hep.style.CMS)
plt.rcParams.update({'font.size': 32})
import argparse,json
from collections import OrderedDict

def plot_eff(x,ydict,name,labels,ylim=[0.001,1],tag='Signal eff.'):
    fig, axs = plt.subplots(1,1,figsize=(10,8))
    for key in ydict.keys():
        axs.plot(x,ydict[key].values(),marker='o',label=labels[key])
    axs.legend()
    for tick in axs.get_xticklabels():
        tick.set_rotation(70)
    axs.set_ylabel(f'{tag}')
    axs.set_yscale('log')
    axs.set_ylim(ylim[0],ylim[1])
    fig.tight_layout()
    fig.savefig(f'eff/{name}.png')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    cuts = {
        r'$\gamma\gamma$': ['nphotons','Initial'],
        r'$bb$': ['njets','nphotons'],
        r'Fj pT': ['fatjet_kin','njets'],
        r'Xbb>0.8': ['fatjet_xbb','fatjet_kin'],
        r'$\gamma$ Kin': ['diphoton_kin','fatjet_xbb'],
        r'$\gamma$ E.Veto': ['diphoton_eveto','diphoton_kin'],
        r'$\Delta R(Pho.Fj)$': ['sel-photonsawayjet','sel-pt_photons'],
        r'b-tag veto': ['sel-nobtagsaway','sel-photonsawayjet'],
        r'Xbb>0.9': ['sel-SelFatJet_Xbb','sel-nobtagsaway'],
        r'MH(bb)': ['sel-mbb_window','sel-SelFatJet_Xbb'],
    }
    cutflow_path = 'gg_nano/Jul3/cutflows/'
    era = '17'

    mX_mY_efficiencies = {}
    from create_refs import sig_dict
    sig_sets = {}
    for mx,mylist in sig_dict.items():
        sig_sets[mx] = [f"NMSSM-XToYH-MX{mx}-MY{my}-HTo2gYTo2b" for my in mylist]

    labels = {}

    for mx,sigset in sig_sets.items():  
        eff = {}
        for iset in sigset:
            eff[iset] = {}
            for cut,cdict in cuts.items():
                dcut = cdict[0]
                icut = cdict[1]
                fcutflow = f"{cutflow_path}/{iset}_{era}.txt"
                old_dict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
                # eff[iset][cut] = old_dict[dcut]/old_dict[icut]
                eff[iset][cut] = old_dict[dcut]/old_dict['Initial']
        x = list(cuts.keys())
        labels = {iset: iset.replace('NMSSM-XToYH-','').replace('-HTo2gYTo2b','') for iset in sigset}
        plot_eff(x,eff,f"eff_MX{mx}",labels)

    grp_bkg = {
        "GJets-DiP-QCD": [
            "GJet-Pt-20to40-MGG-80toInf",
            "GJet-Pt-20toInf-MGG-40to80",
            "GJet-Pt-40toInf-MGG-80toInf",
            "DiPhotonJets-MGG-80toInf",
            "QCD-Pt-30toInf-DoubleEMEnriched-MGG-40to80",
            "QCD-Pt-40ToInf-DoubleEMEnriched-MGG-80ToInf",
        ],
        "HToBB": [
            "VBFHToBB-M-125",
            "ggZH-HToBB-ZToQQ-M-125",
            "WminusH-HToBB-WToQQ-M-125",
            "WplusH-HToBB-WToQQ-M-125",
            "ZH-HToBB-ZToQQ-M-125",
            "GluGluHToBB-Pt-200ToInf-M-125",
        ],
        "HToGG": [
            "VBFHToGG-M125",
            "GluGluHToGG-M125",
        ],
        "TT": [
            "TTTo2L2Nu",
            "TTToHadronic",
            "TTToSemiLeptonic"
        ],
        "WGamma": [
            "WGToLNuG",
        ],
    }
    labels = {
        "GJet-Pt-20to40-MGG-80toInf": "GJet-Pt-20to40-highMGG",
        "GJet-Pt-20toInf-MGG-40to80": "GJet-Pt-40toInf-lowMGG",
        "GJet-Pt-40toInf-MGG-80toInf": "GJet-Pt-40toInf-highMGG",
        "DiPhotonJets-MGG-80toInf":  "DiPhoton-highMGG",
        "QCD-Pt-30toInf-DoubleEMEnriched-MGG-40to80": "QCD-lowMGG",
        "QCD-Pt-40ToInf-DoubleEMEnriched-MGG-80ToInf": "QCD-highMGG",
        "VBFHToBB-M-125": "VBF-Hbb",
        "ggZH-HToBB-ZToQQ-M-125": "ggZH-Hbb",
        "WminusH-HToBB-WToQQ-M-125": "WHm-Hbb",
        "WplusH-HToBB-WToQQ-M-125": "WHp-Hbb",
        "ZH-HToBB-ZToQQ-M-125": "ZH-Hbb",
        "GluGluHToBB-Pt-200ToInf-M-125": "Hbb",
        "VBFHToGG-M125": "VBF-Hgg",
        "GluGluHToGG-M125": "Hgg",
        "TTTo2L2Nu": "TTlep",
        "TTToHadronic": "TThad",
        "TTToSemiLeptonic": "TTsemi",
        "WGToLNuG": "WGamma",
    }
    for bkg,bkgset in grp_bkg.items():
        eff = {}
        eyield = {}
        for iset in bkgset:
            eff[iset] = {}
            eyield[iset] = {}
            fcutflow = f"{cutflow_path}/{iset}_{era}.txt"
            old_dict = json.load(open(fcutflow), object_pairs_hook=OrderedDict)
            for cut,cdict in cuts.items():
                dcut = cdict[0]
                icut = cdict[1]
                try:
                    eff[iset][cut] = old_dict[dcut]/old_dict['Initial']
                except:
                    eff[iset][cut] = 0.0
                if dcut+'-weight' in old_dict.keys():
                    eyield[iset][cut] = old_dict[dcut+'-weight']
                else:
                    eyield[iset][cut] = 0.0
        x = list(cuts.keys())
        plot_eff(x,eff,f"eff_{bkg}",labels,ylim=[1e-7,1],tag='Bkg. eff.')
        print(eyield)
        plot_eff(x,eyield,f"yield_{bkg}",labels,ylim=[1e-3,10000],tag='Bkg. yield')
