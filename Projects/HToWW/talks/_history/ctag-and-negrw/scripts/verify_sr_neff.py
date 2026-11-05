"""Verify the deck's SR N_eff claim: 455 -> 1563 (3.44x) and the 16.4% neg fraction."""
import pandas as pd, numpy as np, glob
D="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva"
VJ=["DYto2L_2Jets_50","DYto2L_2Jets_10to50","WtoLNu_2Jets"]
w_all=[]; g_all=[]
for s in VJ:
    p=f"{D}/{s}.parquet.bak_pre_ctag2dsf"
    df=pd.read_parquet(p)
    sc=[c for c in df.columns if c.startswith("mva_score_")]
    names=[c.replace("mva_score_","") for c in sc]
    am=np.array(names)[df[sc].to_numpy().argmax(1)]
    m=am=="hplusc"                      # the SR
    w=df.loc[m,"weight_nominal"].to_numpy()
    g=df.loc[m,"weight_negrw"].to_numpy()
    w_all.append(w); g_all.append(g)
    print(f"  {s:22s} SR rows={m.sum():6d}")
w=np.concatenate(w_all); g=np.concatenate(g_all)
neff_nom=w.sum()**2/(w**2).sum()
rw=np.abs(w)*g
neff_rw=rw.sum()**2/(rw**2).sum()
print(f"\n  total SR vjets rows : {len(w)}   (deck says 10,205)")
print(f"  neg-weight fraction : {(w<0).mean():.4f}   (deck says 16.4% inclusive/training)")
print(f"  N_eff nominal       : {neff_nom:.1f}   (deck says 455)")
print(f"  N_eff reweighted    : {neff_rw:.1f}   (deck says 1563)")
print(f"  gain                : {neff_rw/neff_nom:.2f}x  (deck says 3.44x)")
