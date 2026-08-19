"""Complete the interrupted merge in the hww_combine_2dcat tree.

Only writes group parquets that are MISSING; never touches existing ones.
Uses the repo's own merge_parquet_files (flat concat + sumw aggregation).
"""
import glob, os, re, sys
from pathlib import Path
from analysis.postprocess.utils import merge_parquet_files

D2 = "outputs/hww_combine_2dcat/2022postEE"
DF = "outputs/hww_combine_fixed/2022postEE"

have = {os.path.basename(p) for p in glob.glob(f"{D2}/*.parquet")}
want = {os.path.basename(p) for p in glob.glob(f"{DF}/*.parquet")}
missing = sorted(want - have)
print(f"{len(have)} present, {len(want)} expected, {len(missing)} missing\n")

done = skipped = 0
for name in missing:
    sample = name[:-len(".parquet")]
    # per-partition shards: <sample>_<n>/base/*.parquet ; guard prefix collisions
    dirs = [d for d in glob.glob(f"{D2}/{sample}_*/base") + glob.glob(f"{D2}/{sample}/base")
            if re.fullmatch(rf"{re.escape(sample)}(_\d+)?", Path(d).parent.name)]
    shards = [f for d in dirs for f in glob.glob(f"{d}/*.parquet")]
    if not shards:
        print(f"  [skip] {sample:34s} no shards"); skipped += 1; continue
    out = f"{D2}/{name}"
    ok = merge_parquet_files(shards, out)
    print(f"  [{'ok' if ok else 'FAIL'}] {sample:34s} {len(shards):4d} shards -> {name}")
    done += ok

print(f"\nmerged {done}, skipped {skipped}")
