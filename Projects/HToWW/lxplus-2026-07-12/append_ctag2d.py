#!/usr/bin/env python3
"""
Append 2D-CTAG category columns to the H->WW parquets.

Method (see Projects/HToWW/CTAG.md, finding 2026-07-12):
  The official AN-25-222 / SFbc-2D 2D flavour-tagging scheme partitions a
  (HFvLF, BvC) plane into 11 categories L0,C0..C4,B0..B4 with frozen edges.
  Our parquets store only PNet CvsL / CvsB, but the two axes are exactly
  recoverable from them via the PNet 3-simplex (b, c, L=uds+g):

      BvC   (y) = 1 - CvB
      HFvLF (x) = P_b + P_c = 1 - P_L = CvL / (CvL + CvB*(1 - CvL))

  (verified: symbolic + 2M synthetic triplets @4e-16 + 30k NanoAODv12 jets @2.8e-5.)

We apply the OFFICIAL frozen edges to these axes and append an int8 category id
per jet collection. No reprocessing, no B storage needed.

Adds, for each jet collection present (cjet_cand, leadingjet):
    <coll>_ctag_2d_cat   int8   0..10  (-1 if score is null / unassigned)

Idempotent: re-running overwrites the columns, never duplicates.

Usage:
    python append_ctag2d.py /eos/home-c/cgupta/higgscharm/outputs/hww/2022postEE
    python append_ctag2d.py <dir> --dry-run
    python append_ctag2d.py <dir1> <dir2> ...
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# ---- Official frozen edges (SFbc-2D docs, 2026.06.29) -----------------------
X_HFvLF = np.array([0.0, 0.250, 0.452, 0.808, 1.000])
Y_BvC   = np.array([0.0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.0])

CATEGORIES = ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]
CAT_ID = {k: i for i, k in enumerate(CATEGORIES)}

# Prefix for the per-category one-hot columns fed to the MVA (11 int8 0/1 columns):
#   cjet_cand_ctag2d_L0 ... cjet_cand_ctag2d_B4
ONEHOT_PREFIX = "cjet_cand_ctag2d_"
ONEHOT_COLS = [ONEHOT_PREFIX + c for c in CATEGORIES]

# Jet collections to process: (cvsl_col, cvsb_col, output_col).
# The MVA (config/HPlusCHToWW.yml) consumes ONLY the cjet_cand collection, which
# is null-free in hww_combine_fixed. We therefore build the 2D category from it
# alone -> the appended column has NO nulls. (leadingjet/second/third carry padding
# nulls and are not MVA inputs, so we deliberately skip them.)
COLLECTIONS = [
    ("cjet_cand_cvsl_pnet", "cjet_cand_cvsb_pnet", "cjet_cand_ctag_2d_cat"),
]


def axes_from_pnet(cvl, cvb):
    """(HFvLF proxy x, BvC y) from stored PNet CvsL/CvsB. NaN-safe."""
    cvl = np.asarray(cvl, dtype=np.float64)
    cvb = np.asarray(cvb, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        den = cvl + cvb * (1.0 - cvl)          # = CvL + CvB(1-CvL)
        x = np.where(den != 0, cvl / den, np.nan)   # HFvLF = pB+C
    y = 1.0 - cvb                                     # BvC
    return x, y


def assign_category(cvl, cvb):
    """Return int8 category ids (0..10), -1 where score is null/unassigned.

    Layout (matches SFbc-2D figure topology):
      left of HFvLF=0.808 -> L0 | C0 | C1  by x-edges 0.250, 0.452 (full height)
      right of 0.808      -> stacked in BvC(y): bottom C4,C3,C2 (y<0.055),
                             then b-band B0..B4 rising to B4 at y->1 (purest b).
    """
    x, y = axes_from_pnet(cvl, cvb)
    cat = np.full(x.shape, -1, dtype=np.int8)
    good = np.isfinite(x) & np.isfinite(y)

    left = good & (x < X_HFvLF[3])
    right = good & (x >= X_HFvLF[3])

    cat[left & (x < X_HFvLF[1])] = CAT_ID["L0"]
    cat[left & (x >= X_HFvLF[1]) & (x < X_HFvLF[2])] = CAT_ID["C0"]
    cat[left & (x >= X_HFvLF[2])] = CAT_ID["C1"]

    cat[right & (y < Y_BvC[1])] = CAT_ID["C4"]
    cat[right & (y >= Y_BvC[1]) & (y < Y_BvC[2])] = CAT_ID["C3"]
    cat[right & (y >= Y_BvC[2]) & (y < Y_BvC[3])] = CAT_ID["C2"]
    cat[right & (y >= Y_BvC[3]) & (y < Y_BvC[4])] = CAT_ID["B0"]
    cat[right & (y >= Y_BvC[4]) & (y < Y_BvC[5])] = CAT_ID["B1"]
    cat[right & (y >= Y_BvC[5]) & (y < Y_BvC[6])] = CAT_ID["B2"]
    cat[right & (y >= Y_BvC[6]) & (y < Y_BvC[7])] = CAT_ID["B3"]
    cat[right & (y >= Y_BvC[7])] = CAT_ID["B4"]
    return cat


def process_file(path: Path, dry_run: bool = False) -> str:
    table = pq.read_table(path)
    names = set(table.column_names)
    added = []
    for cvsl, cvsb, out in COLLECTIONS:
        if cvsl not in names or cvsb not in names:
            continue
        cvl = table.column(cvsl).to_numpy(zero_copy_only=False)
        cvb = table.column(cvsb).to_numpy(zero_copy_only=False)
        cat = assign_category(cvl, cvb)
        n_unassigned = int(np.sum(cat < 0))
        if n_unassigned:
            print(f"    WARNING {path.name}:{out} has {n_unassigned} unassigned "
                  f"(-1) rows — cjet_cand was expected null-free", file=sys.stderr)
        def put(name, values):
            a = pa.array(values, type=pa.int8())
            nonlocal table
            if name in table.column_names:            # idempotent overwrite
                table = table.set_column(table.column_names.index(name), name, a)
            else:
                table = table.append_column(name, a)

        # integer category id (diagnostics / SF lookup)
        put(out, cat)
        added.append(out)
        # one-hot columns for the MVA (0/1 int8). -1 (should not occur) -> all zeros.
        for k, col in zip(CATEGORIES, ONEHOT_COLS):
            put(col, (cat == CAT_ID[k]).astype(np.int8))
        added.append(f"{ONEHOT_PREFIX}{{{','.join(CATEGORIES)}}}")
    if not added:
        return f"skip (no PNet cols): {path.name}"
    if dry_run:
        return f"[dry] would add {added} to {path.name} ({table.num_rows} rows)"
    tmp = path.with_suffix(".parquet.tmp")
    pq.write_table(table, tmp, compression="snappy")
    tmp.replace(path)
    return f"added {added} -> {path.name} ({table.num_rows} rows)"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", help="dir(s) holding <process>.parquet files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--glob", default="*.parquet",
                    help="file glob within each dir (default *.parquet)")
    args = ap.parse_args()

    files = []
    for d in args.dirs:
        files += sorted(Path(d).glob(args.glob))
    if not files:
        print("no parquet files found", file=sys.stderr)
        sys.exit(1)

    print(f"{len(files)} file(s){' [DRY RUN]' if args.dry_run else ''}")
    for f in files:
        if f.name.endswith(".tmp"):
            continue
        try:
            print(" ", process_file(f, args.dry_run))
        except Exception as e:
            print(f"  ERROR {f.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
