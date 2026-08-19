import glob, os, re, json, pyarrow.parquet as pq

Q = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_old_inclusive_wjets"
R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"

print("=== A. the 13 merged inclusive parquets (what the datacard actually reads) ===")
merged = sorted(glob.glob(f"{Q}/merged/*/*.parquet"))
tot = 0
for m in merged:
    try:
        n = pq.ParquetFile(m).metadata.num_rows
        tot += n
        print(f"   {os.path.basename(os.path.dirname(m)):22s} {n:6d} rows  READABLE")
    except Exception as e:
        print(f"   {m}  *** UNREADABLE {type(e).__name__} ***")
print(f"   total rows across all 13: {tot}")

print("\n=== B. inclusive raw partitions + their sumw ===")
parts = [d for d in os.listdir(f"{Q}/partitions")
         if re.fullmatch(r"WtoLNu_2Jets(_\d+)?", d)]
sumw = 0.0; nf = 0; nbase = 0
for d in parts:
    for f in glob.glob(f"{Q}/partitions/{d}/sumw_records/*.parquet"):
        sumw += sum(pq.read_table(f).column("sumw").to_pylist()); nf += 1
    nbase += len(glob.glob(f"{Q}/partitions/{d}/base/*.parquet"))
print(f"   partition dirs: {len(parts)}   sumw files: {nf}   base files: {nbase}")
print(f"   total sumw: {sumw:,.0f}")

print("\n=== C. config restore points (backups on AFS) ===")
for pat in ("analysis/filesets/2022postEE_nanov12.yaml.bak_pre_wjets_*",
            "analysis/workflows/hww_combine_2dcat.yaml.bak_pre_wjets_*",
            "analysis/filesets/fileset_2022postEE_nanov12_lxplus.json.bak_2*"):
    for b in sorted(glob.glob(f"{R}/{pat}")):
        print(f"   {os.path.relpath(b, R)}  ({os.path.getsize(b):,} B)")

print("\n=== D. the 1160 datacard itself ===")
for f in ("v11_hplusc_2dcat.txt", "v11_hplusc_2dcat.root"):
    p = f"/eos/user/c/cgupta/higgscharm/outputs/combine/{f}"
    print(f"   {f}: {'EXISTS' if os.path.exists(p) else '*** MISSING ***'}"
          f"  {os.path.getsize(p):,} B" if os.path.exists(p) else f"   {f}: MISSING")
