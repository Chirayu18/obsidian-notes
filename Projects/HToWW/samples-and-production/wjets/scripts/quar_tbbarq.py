#!/usr/bin/env python3
"""Quarantine stale TBbarQ/TbarBQ outputs (samples disabled 2026-08-12).

Anchored exact-name matching -- NOT a glob -- so nothing else can be caught.
Moves, never deletes.
"""
import os, shutil, glob

NAMES = {"TBbarQ", "TbarBQ"}
ROOTS = {
  "afs": "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/outputs/hww_combine_2dcat/2022postEE",
  "eos": "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE",
}
QUAR = {
  "afs": "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/outputs/hww_combine_2dcat/2022postEE_disabled_tbbarq",
  "eos": "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_disabled_tbbarq",
}

for tag in ("afs", "eos"):
    R, Q = ROOTS[tag], QUAR[tag]
    if not os.path.isdir(R):
        print(f"{tag}: root missing, skip"); continue
    moved = 0
    # merged parquets: <root>/<shiftdir>/TBbarQ.parquet  and <root>/TBbarQ.parquet
    for p in glob.glob(f"{R}/*/*.parquet") + glob.glob(f"{R}/*.parquet"):
        base = os.path.basename(p)
        if base[:-8] in NAMES and base.endswith(".parquet"):
            rel = os.path.relpath(os.path.dirname(p), R)
            tgt = os.path.join(Q, rel) if rel != "." else Q
            os.makedirs(tgt, exist_ok=True)
            shutil.move(p, os.path.join(tgt, base)); moved += 1
    # raw partition dirs: exact name or name_<digits>
    import re
    for d in os.listdir(R):
        m = re.fullmatch(r"(TBbarQ|TbarBQ)(?:_\d+)?", d)
        if m and os.path.isdir(os.path.join(R, d)):
            os.makedirs(f"{Q}/partitions", exist_ok=True)
            shutil.move(os.path.join(R, d), f"{Q}/partitions/{d}"); moved += 1
    print(f"{tag}: moved {moved} items -> {Q}")
    # verify nothing named TBbarQ/TbarBQ remains
    left = [p for p in glob.glob(f"{R}/*/*.parquet") + glob.glob(f"{R}/*.parquet")
            if os.path.basename(p)[:-8] in NAMES]
    left += [d for d in os.listdir(R) if re.fullmatch(r"(TBbarQ|TbarBQ)(?:_\d+)?", d)]
    print(f"   remaining in live tree: {len(left)}")
