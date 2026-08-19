"""Verify variant 3's -1 sentinel and the in-base kinematic cuts."""
import glob
import numpy as np, pandas as pd

D = "/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE"
fs = sorted(glob.glob(f"{D}/HplusCharm_HtoWW*/base/*.parquet"))
print(f"signal shards: {len(fs)}")
cols = ["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","cjet_cand_pt",
        "mtll","mtl2","dilepton_mass","weight_nominal"]
ds = []
for f in fs[:40]:
    try:
        ds.append(pd.read_parquet(f, columns=cols))
    except Exception as e:
        print("  skip", f.split("/")[-1], e); continue
if not ds:
    raise SystemExit("no shards read")
d = pd.concat(ds, ignore_index=True)
print(f"events read: {len(d):,}\n")

for c in ["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","cjet_cand_pt"]:
    a = d[c].to_numpy(dtype=float)
    neg = (a == -1).sum()
    nan = np.isnan(a).sum()
    print(f"{c:<24s} min={np.nanmin(a):8.3f}  =-1: {neg:>7,d} ({100*neg/len(a):5.2f}%)  NaN: {nan:,}")

print("\n--- kinematic cuts should already be applied (in base) ---")
for name, ok in [("mTl2 > 30", d.mtl2 > 30),
                 ("mTll > 60", d.mtll > 60),
                 ("mll <= 72", d.dilepton_mass <= 72)]:
    print(f"  {name:<12s} satisfied: {100*ok.mean():6.2f}%   (expect 100.00%)")
