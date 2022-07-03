import subprocess
import json

def get_children(parent):
	#print(f"DEBUG : Call to get_children({parent})")
	command = f"eos root://cmseos.fnal.gov ls -F {parent}"
	#print(command)
	result = subprocess.getoutput(command)#, stdout=subprocess.PIPE)
	#print(result)
	return result.split("\n")

def get_subfolders(parent):
	subfolders = []
	for x in get_children(parent):
		if len(x) == 0: 
			continue
		if x[-1] == "/":
			subfolders.append(x)
	return subfolders

folders_to_index = [
	"/store/user/lpcpfnano/cmantill/v2_2/2017/XHYPrivate",
        "/store/user/lpcpfnano/cmantill/v2_2/2017/GJets",
        "/store/user/lpcpfnano/cmantill/v2_3/2017/HH",
        "/store/user/lpcpfnano/cmantill/v2_2/2017/QCD",
]

for pyear in ["2017"]:
    index = {}
    for f1 in folders_to_index:
        f1 = f1.rstrip("/")
        print(f1)
        year = f1.split("/")[-2]
        sample_short = f1.split("/")[-1]
        if year != pyear:
            continue
        if not year in index:
            index[year] = {}
        if not sample_short in index[year]:
            index[year][sample_short] = {}

        f1_subfolders = get_subfolders(f"{f1}")
        for f2 in f1_subfolders:
            print(f"\t/{f2}")
            subsample_long = f2.replace("/", "")  # This should be the actual dataset name
            f2_subfolders = get_subfolders(f"{f1}/{f2}")
            if len(f2_subfolders) == 0:
                root_files = [
                    f"{f1}/{f2}/{x}".replace("//", "/")
                    for x in get_children((f"{f1}/{f2}"))
                    if x[-5:] == ".root"
                ]
                if not subsample_long in index[year][sample_short]:
                    index[year][sample_short][subsample_long] = []
                index[year][sample_short][subsample_long].extend(root_files)

            for f3 in f2_subfolders:
                print(f"\t\t/{f3}")
                subsample_short = f3.replace("/", "")
                if not subsample_short in index[year][sample_short]:
                    index[year][sample_short][subsample_short] = []
                f3_subfolders = get_subfolders(f"{f1}/{f2}/{f3}")
                if len(f3_subfolders) >= 2:
                    print(f"WARNING : Found multiple timestamps for {f1}/{f2}/{f3}")

                for f4 in f3_subfolders:  # Timestamp
                    f4_subfolders = get_subfolders(f"{f1}/{f2}/{f3}/{f4}")

                    for f5 in f4_subfolders:  # 0000, 0001, ...
                        f5_children = get_children((f"{f1}/{f2}/{f3}/{f4}/{f5}"))
                        root_files = [
                            f"{f1}/{f2}/{f3}/{f4}/{f5}/{x}".replace("//", "/")
                            for x in f5_children
                            if x[-5:] == ".root"
                        ]
                        index[year][sample_short][subsample_short].extend(root_files)

    with open(f"pfnanoindex_{pyear}.json", "w") as f:
        json.dump(index, f, sort_keys=True, indent=2)
