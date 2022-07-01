import argparse
import json

def main(args):

    year = args.year
    y = year.replace("20","")
    fname = f"fileset/pfnanoindex_{year}.json"

    fileset = {}
    with open(fname, 'r') as f:
        files = json.load(f)
        for subdir in files[year]:
            for key, flist in files[year][subdir].items():
                fileset[key] = ["root://cmsxrootd.fnal.gov/" + f for f in flist]

    for key,flist in fileset.items():
        key = key.replace("_","-")
        fname = f"{key}_{y}.txt"
        with open(fname,"w") as f:
            for fline in flist:
                f.write(fline+'\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year",      dest="year",      default="2017",                help="year", type=str)
    args = parser.parse_args()

    main(args)
