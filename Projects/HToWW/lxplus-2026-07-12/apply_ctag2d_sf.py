#!/usr/bin/env python3
"""Apply the per-campaign PNet 2D c-tag scale factor to the combine mva parquets.

For each MC `mva/<sample>.parquet` this:
  * recomputes the 2D category from cjet_cand_cvsl_pnet / cjet_cand_cvsb_pnet
    (the mva/ parquets carry the raw scores but not the int cat column),
  * maps it to the SF `wp` id  (L0=0, C0..C4=40..44, B0..B4=50..54),
  * evaluates the SF for the candidate c-jet using cjet_cand_flavour (0/4/5) and
    cjet_cand_pt (abseta inclusive -> dummy 0.0),
  * SCALES weight_nominal and every existing weight_* column by the CENTRAL SF
    (a genuine correction, applied everywhere),
  * adds two nuisance columns
        weight_CMS_ctag2d_<year>Up   = weight_nominal_corrected * SF_upTotal/SF_central
        weight_CMS_ctag2d_<year>Down = weight_nominal_corrected * SF_downTotal/SF_central

Rows with no candidate c-jet (cjet_cand_pt NaN) get SF = 1 (no shift).

Idempotent: writes a one-time `.bak_pre_ctag2dsf` backup and refuses to run twice
(guarded by the presence of the Up column). Atomic via a .tmp rename.

Usage:
  python apply_ctag2d_sf.py --year 2022postEE
  python apply_ctag2d_sf.py --year 2022postEE --dry-run
"""
import argparse
import glob
import os
import shutil
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from correctionlib import CorrectionSet

# --- 2D category from PNet scores (mirrors analysis.utils.ctag2d, numpy version) ---
X_HFVLF_EDGES = [0.0, 0.250, 0.452, 0.808, 1.000]
Y_BVC_EDGES = [0.0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.0]
CATS = ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]
CID = {n: i for i, n in enumerate(CATS)}
# SF `wp` integer ids
WP_ID = {"L0": 0, "C0": 40, "C1": 41, "C2": 42, "C3": 43, "C4": 44,
         "B0": 50, "B1": 51, "B2": 52, "B3": 53, "B4": 54}
# our int cat 0..10 -> SF wp id
CAT_TO_WP = np.array([WP_ID[c] for c in CATS], dtype=np.int64)

SF_FILES = {
    "2022preEE":   "/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022preEE.json.gz",
    "2022postEE":  "/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022postEE.json.gz",
    "2023preBPix": "/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2023/2D_HF_Tagging/flavTaggingSF_2023preBPix.json.gz",
    "2023postBPix": "/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2023/2D_HF_Tagging/flavTaggingSF_2023postBPix.json.gz",
}
# nuisance uses a 2022/2023 label (correlate campaigns within a year)
NUIS_YEAR = {"2022preEE": "2022", "2022postEE": "2022",
             "2023preBPix": "2023", "2023postBPix": "2023"}

OUTPUT_ROOT = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed"


def ctag2d_category_np(cvsl, cvsb):
    """int category 0..10 per row; -1 where undefined (NaN scores)."""
    den = cvsl + cvsb * (1.0 - cvsl)
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(den != 0, cvsl / den, np.nan)  # HFvLF
    y = 1.0 - cvsb                                    # BvC
    good = np.isfinite(x) & np.isfinite(y)
    cat = np.full(x.shape, -1, dtype=np.int64)
    xe, ye = X_HFVLF_EDGES, Y_BVC_EDGES
    left = good & (x < xe[3])
    right = good & (x >= xe[3])

    def put(mask, name):
        cat[mask] = CID[name]

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


def eval_sf(corr, systematic, flavour, wp, pt):
    """Vectorised SF; abseta inclusive so pass 0.0. Returns SF array (1.0 where undefined)."""
    n = len(flavour)
    sf = np.ones(n, dtype=np.float64)
    # only rows with a defined wp (>=0 int cat, so wp mapped) and finite pt
    ok = (wp >= 0) & np.isfinite(pt)
    if ok.any():
        # correctionlib wants float pt, int flavour/wp
        vals = corr.evaluate(
            systematic,
            flavour[ok].astype(np.int64),
            wp[ok].astype(np.int64),
            np.zeros(ok.sum(), dtype=np.float64),   # abseta (inclusive)
            np.clip(pt[ok].astype(np.float64), 20.0001, 9999.0),
        )
        sf[ok] = vals
    return sf


def process_file(path, corr, nuis_col, dry_run=False):
    up_col = f"{nuis_col}Up"
    dn_col = f"{nuis_col}Down"
    schema_cols = pq.read_schema(path).names
    if up_col in schema_cols:
        return f"  [skip] {os.path.basename(path)}: already has {up_col}"

    df = pd.read_parquet(path)
    if len(df) == 0:
        return f"  [empty] {os.path.basename(path)}"

    need = ["cjet_cand_cvsl_pnet", "cjet_cand_cvsb_pnet", "cjet_cand_flavour",
            "cjet_cand_pt", "weight_nominal"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        return f"  [MISS] {os.path.basename(path)}: missing {miss}"

    cvsl = df["cjet_cand_cvsl_pnet"].to_numpy(dtype=np.float64)
    cvsb = df["cjet_cand_cvsb_pnet"].to_numpy(dtype=np.float64)
    pt = df["cjet_cand_pt"].to_numpy(dtype=np.float64)
    # flavour: fill any missing with 0 (light); those rows have NaN pt anyway -> SF=1
    flav = pd.to_numeric(df["cjet_cand_flavour"], errors="coerce").fillna(0).to_numpy().astype(np.int64)

    cat = ctag2d_category_np(cvsl, cvsb)          # -1 where undefined
    wp = np.where(cat >= 0, CAT_TO_WP[np.clip(cat, 0, 10)], -1)

    sf_c = eval_sf(corr, "central", flav, wp, pt)
    sf_up = eval_sf(corr, "up_Total", flav, wp, pt)
    sf_dn = eval_sf(corr, "down_Total", flav, wp, pt)

    # ratios (guard sf_c==0 -> 1)
    r_up = np.where(sf_c != 0, sf_up / sf_c, 1.0)
    r_dn = np.where(sf_c != 0, sf_dn / sf_c, 1.0)

    weight_cols = [c for c in df.columns if c.startswith("weight_")]

    stats = dict(
        n=len(df),
        n_cand=int(np.isfinite(pt).sum()),
        sf_mean=float(sf_c[np.isfinite(pt)].mean()) if np.isfinite(pt).any() else 1.0,
        cat_counts={CATS[i]: int((cat == i).sum()) for i in range(11) if (cat == i).any()},
    )

    if dry_run:
        return (f"  [dry] {os.path.basename(path):40s} n={stats['n']:7d} "
                f"cand={stats['n_cand']:7d} <SFc>={stats['sf_mean']:.4f} "
                f"cats={stats['cat_counts']}")

    # backup once
    bak = path + ".bak_pre_ctag2dsf"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

    # scale every existing weight column by central SF; then add Up/Down from
    # the corrected nominal (which is now already * sf_c)
    for c in weight_cols:
        df[c] = df[c].to_numpy(dtype=np.float64) * sf_c
    wn_corr = df["weight_nominal"].to_numpy(dtype=np.float64)
    df[up_col] = wn_corr * r_up
    df[dn_col] = wn_corr * r_dn

    tmp = path + ".tmp"
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)
    return (f"  [ok]  {os.path.basename(path):40s} n={stats['n']:7d} "
            f"cand={stats['n_cand']:7d} <SFc>={stats['sf_mean']:.4f} "
            f"scaled {len(weight_cols)} weight cols; +{up_col}/{dn_col}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True, choices=list(SF_FILES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mva-dir", default=None,
                    help="override mva dir (default OUTPUT_ROOT/<year>/mva)")
    args = ap.parse_args()

    sf_file = SF_FILES[args.year]
    if not os.path.exists(sf_file):
        sys.exit(f"SF file not found: {sf_file}")
    corr = CorrectionSet.from_file(sf_file)["ParticleNetAK4_pseudocontinuous"]
    nuis_col = f"weight_CMS_ctag2d_{NUIS_YEAR[args.year]}"

    mva_dir = args.mva_dir or os.path.join(OUTPUT_ROOT, args.year, "mva")
    fs = sorted(f for f in glob.glob(os.path.join(mva_dir, "*.parquet"))
                if not f.endswith(".bak_pre_negrw")
                and not f.endswith(".bak_pre_ctag2dsf")
                and not f.endswith(".tmp")
                and os.path.basename(f) != "Data.parquet")
    print(f"year={args.year}  SF={sf_file}")
    print(f"nuisance column base = {nuis_col}  (Up/Down)")
    print(f"{len(fs)} MC mva parquets in {mva_dir}\n")

    for f in fs:
        print(process_file(f, corr, nuis_col, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
