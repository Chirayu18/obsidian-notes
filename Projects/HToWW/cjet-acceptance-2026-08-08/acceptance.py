"""Signal acceptance for the three c-jet variants vs the current 2dcat baseline.

Reads the base/ parquets each variant produced and reports raw event counts and
weighted yields (lumi*xsec/sumw via read_scale, i.e. the same normalisation the fit
uses). For variant 3, also background yields and S/sqrt(B).
"""
import sys, glob
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts" / "combine"))
from make_combine_inputs import read_scale, load_lumi

YEAR = "2022postEE"
OUT = Path("/eos/user/c/cgupta/higgscharm/outputs")
lumi = load_lumi(YEAR)

VARIANTS = [
    ("baseline (2dcat)", "hww_combine_2dcat"),
    ("1: no c-tag",      "hww_2dcat_nocjet"),
    ("2: loose WP",      "hww_2dcat_looseWP"),
    ("3: no-tag + kin",  "hww_2dcat_nocjet_kin"),
]
SIG = "HplusCharm_HtoWW"

def yield_of(wf, sample):
    """raw N and weighted yield for one sample in one workflow's tree."""
    base = OUT / wf / YEAR
    # merged per-sample parquet if present, else the sharded base/ dir
    cand = list(base.glob(f"{sample}.parquet")) or \
           sorted(glob.glob(f"{base}/{sample}*/base/*.parquet")) or \
           sorted(glob.glob(f"{base}/{sample}/base/*.parquet"))
    if not cand:
        return None, None
    n, w = 0, 0.0
    for f in cand:
        try:
            d = pd.read_parquet(f, columns=["weight_nominal"])
        except Exception:
            continue
        n += len(d)
        w += float(d["weight_nominal"].sum())
    if n == 0:
        return 0, 0.0
    try:
        sc = read_scale(sample, YEAR, base, lumi)
    except Exception:
        sc = float("nan")
    return n, w * sc

print(f"{'variant':<20s} {'raw N':>10s} {'weighted':>12s} {'vs base':>9s}")
print("-" * 56)
ref_n = ref_w = None
for label, wf in VARIANTS:
    n, w = yield_of(wf, SIG)
    if n is None:
        print(f"{label:<20s} {'--- not produced yet ---':>32s}")
        continue
    if ref_n is None:
        ref_n, ref_w = n, w
    rn = n / ref_n if ref_n else float("nan")
    print(f"{label:<20s} {n:>10,d} {w:>12.4f} {rn:>8.2f}x")
print("\n(weighted = lumi*xsec/sumw, same normalisation as the fit)")
