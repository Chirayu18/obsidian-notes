#!/usr/bin/env python3
"""Append the 11 one-hot cjet_cand_ctag2d_* columns to mva parquets.

These are a deterministic function of the stored PNet cvsl/cvsb scores (same
category assignment as apply_ctag2d_sf.py). The 2D-cat MVA (config
HPlusCHToWW_2dcats) needs them as inputs; run_inference fills MISSING features
with 0, so they must be materialized before inference or the model silently sees
an all-zero category vector.

Idempotent: skips a file that already has cjet_cand_ctag2d_L0. Atomic .tmp rename.
No backup needed (these dirs are the throwaway 2dcat copy; the source tree is
untouched).

Usage:
  python append_onehot.py --mva-dir <dir>
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

X_HFVLF_EDGES = [0.0, 0.250, 0.452, 0.808, 1.000]
Y_BVC_EDGES = [0.0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.0]
CATS = ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]
CID = {n: i for i, n in enumerate(CATS)}


def ctag2d_category_np(cvsl, cvsb):
    den = cvsl + cvsb * (1.0 - cvsl)
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(den != 0, cvsl / den, np.nan)
    y = 1.0 - cvsb
    good = np.isfinite(x) & np.isfinite(y)
    cat = np.full(x.shape, -1, dtype=np.int64)
    xe, ye = X_HFVLF_EDGES, Y_BVC_EDGES
    left = good & (x < xe[3])
    right = good & (x >= xe[3])

    def put(m, n):
        cat[m] = CID[n]

    put(left & (x < xe[1]), "L0")
    put(left & (x >= xe[1]) & (x < xe[2]), "C0")
    put(left & (x >= xe[2]), "C1")
    put(right & (y < ye[1]), "C4")
    put(right & (y >= ye[1]) & (y < ye[2]), "C3")
    put(right & (y >= ye[2]) & (y < ye[3]), "C2")
    put(right & (y >= ye[3]) & (y < ye[4]), "B0")
    put(right & (y >= ye[4]) & (y < ye[5]), "B1")
    put(right & (y >= ye[5]) & (y < ye[6]), "B2")
    put(right & (y >= ye[6]) & (y < ye[7]), "B3")
    put(right & (y >= ye[7]), "B4")
    return cat


def process(path):
    cols = pq.read_schema(path).names
    if "cjet_cand_ctag2d_L0" in cols:
        return f"  [skip] {os.path.basename(path)}: already has one-hot"
    if "cjet_cand_cvsl_pnet" not in cols or "cjet_cand_cvsb_pnet" not in cols:
        return f"  [MISS] {os.path.basename(path)}: no cvsl/cvsb"
    df = pd.read_parquet(path)
    if len(df) == 0:
        return f"  [empty] {os.path.basename(path)}"
    cvsl = df["cjet_cand_cvsl_pnet"].to_numpy(dtype=np.float64)
    cvsb = df["cjet_cand_cvsb_pnet"].to_numpy(dtype=np.float64)
    cat = ctag2d_category_np(cvsl, cvsb)
    for i, name in enumerate(CATS):
        df["cjet_cand_ctag2d_" + name] = (cat == i).astype(np.int8)
    tmp = path + ".tmp"
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)
    filled = int((cat >= 0).sum())
    return f"  [ok]  {os.path.basename(path):40s} n={len(df):7d} categorized={filled}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mva-dir", required=True)
    args = ap.parse_args()
    fs = sorted(f for f in glob.glob(os.path.join(args.mva_dir, "*.parquet"))
                if not f.endswith(".tmp"))
    for f in fs:
        print(process(f))


if __name__ == "__main__":
    main()
