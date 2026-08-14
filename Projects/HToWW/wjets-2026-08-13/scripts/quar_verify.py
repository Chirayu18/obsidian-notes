import glob, os, re, hashlib, pyarrow.parquet as pq

B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
Q = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_old_inclusive_wjets"

print("=== 1. quarantine contains ONLY inclusive ===")
parts = sorted(os.listdir(f"{Q}/partitions"))
bad = [n for n in parts if not re.fullmatch(r"WtoLNu_2Jets(_\d+)?", n)]
print(f"  partition dirs: {len(parts)}   non-inclusive: {len(bad)} {bad if bad else ''}")
merged = glob.glob(f"{Q}/merged/*/*.parquet")
print(f"  merged parquets: {len(merged)}")
badm = [m for m in merged if os.path.basename(m) != "WtoLNu_2Jets.parquet"]
print(f"  non-inclusive merged: {len(badm)}")

print("\n=== 2. NO name collisions were overwritten (each shift dir kept separate) ===")
dirs = sorted(os.listdir(f"{Q}/merged"))
print(f"  shift subdirs: {len(dirs)}")
print(f"  {dirs}")

print("\n=== 3. live tree has NO inclusive leftovers ===")
live_incl = [d for d in os.listdir(B) if re.fullmatch(r"WtoLNu_2Jets(_\d+)?", d)]
print(f"  inclusive dirs in live tree: {len(live_incl)} {live_incl if live_incl else '(none)'}")
print(f"  inclusive merged in live tree: {len(glob.glob(f'{B}/*/WtoLNu_2Jets.parquet')) + len(glob.glob(f'{B}/WtoLNu_2Jets.parquet'))}")

print("\n=== 4. every live jet-binned file is READABLE (no truncation from the move) ===")
nbad = nok = 0
rows = 0
for S in ("0J", "1J", "2J"):
    for d in glob.glob(f"{B}/WtoLNu_2Jets_{S}") + glob.glob(f"{B}/WtoLNu_2Jets_{S}_*"):
        for f in glob.glob(f"{d}/**/*.parquet", recursive=True):
            try:
                m = pq.ParquetFile(f).metadata
                nok += 1
                if "/base/" in f: rows += m.num_rows
            except Exception as e:
                nbad += 1
                print(f"    CORRUPT {f}: {type(e).__name__}")
print(f"  readable parquet files: {nok}   corrupt: {nbad}")
print(f"  surviving base rows: {rows}")

print("\n=== 5. no duplicate sumw chunk (would double-count) ===")
for S in ("0J", "1J", "2J"):
    seen = {}
    dup = 0
    for d in glob.glob(f"{B}/WtoLNu_2Jets_{S}") + glob.glob(f"{B}/WtoLNu_2Jets_{S}_*"):
        for f in glob.glob(f"{d}/sumw_records/*.parquet"):
            k = os.path.basename(f)
            if k in seen: dup += 1
            seen[k] = f
    print(f"  {S}: {len(seen)} unique sumw chunks, {dup} duplicate filenames")
