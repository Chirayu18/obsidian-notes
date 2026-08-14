import glob, os, re, pyarrow.parquet as pq
B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
Q = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_old_inclusive_wjets"

print("=== live jet-binned integrity ===")
bad = []
for S in ("0J","1J","2J"):
    dirs = glob.glob(f"{B}/WtoLNu_2Jets_{S}") + glob.glob(f"{B}/WtoLNu_2Jets_{S}_*")
    nsumw = nbase = rows = 0
    for d in dirs:
        sw = glob.glob(f"{d}/sumw_records/*.parquet")
        nsumw += len(sw)
        if not sw: bad.append(d)
        for f in glob.glob(f"{d}/base/*.parquet"):
            nbase += 1
            try: rows += pq.ParquetFile(f).metadata.num_rows
            except Exception as e: bad.append(f"CORRUPT {f}")
    print(f"  {S}: {len(dirs):4d} dirs, {nsumw:4d} sumw files, {nbase:3d} base files, {rows:5d} rows")
print("  dirs with NO sumw_records:", len(bad))
if bad: print("   ", bad[:3])

print("\n=== quarantine (inclusive only) ===")
names = sorted(os.listdir(f"{Q}/partitions"))
print("  partition dirs:", len(names))
print("  all match inclusive pattern:",
      all(re.fullmatch(r"WtoLNu_2Jets(_\d+)?", n) for n in names))
print("  merged parquets:", len(glob.glob(f"{Q}/merged/*/*.parquet")))
