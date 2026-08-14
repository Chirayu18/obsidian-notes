import glob, os, re, json, collections

R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
L = f"{R}/condor/logs/hww_combine_2dcat/2022postEE"

for S in ("WtoLNu_2Jets_0J", "WtoLNu_2Jets_1J", "WtoLNu_2Jets_2J"):
    npart = len(json.load(open(f"{R}/condor/hww_combine_2dcat/2022postEE/{S}/partitions.json")))
    errs = glob.glob(f"{L}/{S}/*.err")
    xrd = [e for e in errs if "Operation expired" in open(e, errors="ignore").read()]
    # which partition ids actually produced sumw_records on EOS?
    have = set()
    for d in glob.glob(f"{B}/{S}") + glob.glob(f"{B}/{S}_*"):
        if glob.glob(f"{d}/sumw_records/*.parquet"):
            m = re.fullmatch(rf"{S}(?:_(\d+))?", os.path.basename(d))
            if m: have.add(int(m.group(1) or 0))
    print(f"{S}:")
    print(f"   partitions total      : {npart}")
    print(f"   jobs finished (.err)  : {len(errs)}")
    print(f"   with XRootD expiry    : {len(xrd)}")
    print(f"   partitions WITH sumw  : {len(have)}")
    print(f"   -> MISSING so far     : {npart - len(have)}")
