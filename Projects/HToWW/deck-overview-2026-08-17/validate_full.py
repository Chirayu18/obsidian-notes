"""Full validation of the vjets SR re-run: merge all nominal base shards across the
three datasets, check weight_negrw sanity + closure vs nominal, per dataset and total."""
import glob, numpy as np, pandas as pd, pyarrow.parquet as pq

D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
DATASETS = ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]
COLS = ["weight_nominal", "weight_negrw", "weight_negrw_std", "lhe_vpt"]

def load(sample):
    fs = [f for f in glob.glob(f"{D}/{sample}_*/base/*.parquet") if "sumw_records" not in f]
    dfs = []
    for f in fs:
        try:
            names = pq.ParquetFile(f).schema.names
        except Exception:
            continue
        if "weight_negrw" not in names:
            continue
        use = [c for c in COLS if c in names]
        dfs.append(pd.read_parquet(f, columns=use))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(columns=COLS)

allw = []; allg = []
for s in DATASETS:
    d = load(s)
    if len(d) == 0:
        print(f"{s:24s}: NO ROWS"); continue
    g = d["weight_negrw"].to_numpy(); w = d["weight_nominal"].to_numpy()
    st = d["weight_negrw_std"].to_numpy()
    fin = np.isfinite(g) & np.isfinite(w)
    g, w, st = g[fin], w[fin], st[fin]
    allw.append(w); allg.append(g)
    ratio = (np.abs(w)*g).sum() / w.sum() if w.sum() else float("nan")
    print(f"{s:24s}: rows={len(w):7d}  negrw[{g.min():+.3f},{g.max():+.3f}] mean {g.mean():+.3f}"
          f"  dg~{st.mean():.3f}  fracw>0={ (w>0).mean():.3f}"
          f"  closure Sw={w.sum():.4g} S|w|g={(np.abs(w)*g).sum():.4g} ratio={ratio:.4f}"
          f"  anyNaN={bool(np.any(~np.isfinite(d['weight_negrw'].to_numpy())))}")

w = np.concatenate(allw); g = np.concatenate(allg)
print("\n=== TOTAL (all vjets) ===")
print(f"rows={len(w)}  all g in [-1,1]: {bool(np.all((g>=-1)&(g<=1)))}")
print(f"Sum w = {w.sum():.5g}   Sum|w|*g = {(np.abs(w)*g).sum():.5g}   ratio = {(np.abs(w)*g).sum()/w.sum():.4f}")
# Neff comparison
neff_nom = w.sum()**2 / (w**2).sum()
rww = np.abs(w)*g
neff_rw = rww.sum()**2 / (rww**2).sum()
print(f"N_eff nominal = {neff_nom:.0f}   N_eff reweighted = {neff_rw:.0f}   gain = {neff_rw/neff_nom:.2f}x")
