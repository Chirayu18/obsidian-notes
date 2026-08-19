import glob, pyarrow.parquet as pq, subprocess, json

B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
FS = json.load(open("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"))
NEV = {"WtoLNu_2Jets_0J": 678397952, "WtoLNu_2Jets_1J": 522553517, "WtoLNu_2Jets_2J": 344572777}

for S in ["WtoLNu_2Jets_0J", "WtoLNu_2Jets_1J", "WtoLNu_2Jets_2J"]:
    dirs = sorted(glob.glob(f"{B}/{S}_*")) + ([f"{B}/{S}"] if glob.glob(f"{B}/{S}/sumw_records") else [])
    tot = 0.0; n = 0
    for d in dirs:
        for f in glob.glob(f"{d}/sumw_records/*.parquet"):
            tot += sum(pq.read_table(f).column("sumw").to_pylist()); n += 1
    nfiles_total = len(FS.get(S, []))
    print(f"{S}: {len(dirs)} partition dirs, {n} sumw files, sumw={tot:,.0f}")
    # mean genWeight per event should be ~ (1-2*negfrac) * |w|
    if n:
        print(f"   fileset files: {nfiles_total};  DAS events: {NEV[S]:,}")
