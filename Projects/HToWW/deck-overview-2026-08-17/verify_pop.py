"""Verify deck-2 claim: only 7 of 11 categories populated; B1-B4 receive ZERO candidate c-jets."""
import pandas as pd, numpy as np, glob
D="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
CATS=["L0","C0","C1","C2","C3","C4","B0","B1","B2","B3","B4"]
tot={c:0 for c in CATS}; nrows=0
for f in sorted(glob.glob(f"{D}/*.parquet")):
    if "Data" in f or "Run2022" in f or "EGamma" in f or "Muon" in f: continue
    try:
        df=pd.read_parquet(f, columns=[f"cjet_cand_ctag2d_{c}" for c in CATS])
    except Exception:
        continue
    nrows+=len(df)
    for c in CATS: tot[c]+=int(df[f"cjet_cand_ctag2d_{c}"].sum())
s=sum(tot.values())
print(f"MC rows scanned: {nrows}   assigned: {s}   (rowsum check: {s==nrows})")
print(f"{'cat':5s} {'N':>12s} {'%':>7s}")
for c in CATS:
    print(f"{c:5s} {tot[c]:12,d} {100*tot[c]/max(s,1):6.2f}%" + ("   <-- EMPTY" if tot[c]==0 else ""))
