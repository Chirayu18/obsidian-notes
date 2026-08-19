import glob, os, re, json
R="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
B="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
for S in ("WtoLNu_2Jets_0J","WtoLNu_2Jets_1J","WtoLNu_2Jets_2J"):
    npart=len(json.load(open(f"{R}/condor/hww_combine_2dcat/2022postEE/{S}/partitions.json")))
    have=set()
    for d in glob.glob(f"{B}/{S}")+glob.glob(f"{B}/{S}_*"):
        if glob.glob(f"{d}/sumw_records/*.parquet"):
            m=re.fullmatch(rf"{S}(?:_(\d+))?",os.path.basename(d))
            if m: have.add(int(m.group(1) or 0))
    missing=sorted(set(range(npart))-have)
    print(f"{S}: {len(have)}/{npart} present, missing={missing}")
