"""Diagnose the NaN weight_negrw: which rows/features are bad?"""
import glob, sys
import numpy as np, pandas as pd
import joblib

pqs = glob.glob("/tmp/negrw_smoke_out/**/*.parquet", recursive=True)
df = pd.concat([pd.read_parquet(f) for f in pqs], ignore_index=True)
print("rows:", len(df))

b = joblib.load("/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models.joblib")
FEATURES = b["features"]

g = df["weight_negrw"].to_numpy()
bad = ~np.isfinite(g)
print("NaN weight_negrw rows: %d / %d (%.1f%%)" % (bad.sum(), len(g), 100*bad.mean()))
print("finite g range: [%.3f, %.3f]" % (g[~bad].min(), g[~bad].max()) if (~bad).any() else "no finite g")

print("\n--- feature NaN rates in the SR parquet ---")
for f in FEATURES:
    if f not in df.columns:
        print("  %-30s *** MISSING FROM PARQUET ***" % f)
        continue
    col = df[f].to_numpy()
    try:
        nanfrac = float(np.mean(~np.isfinite(col.astype(float))))
    except Exception as e:
        print("  %-30s dtype=%s  (non-numeric: %s)" % (f, col.dtype, e))
        continue
    flag = ""
    if nanfrac > 0:
        flag = "  <-- %.0f%% NaN" % (100*nanfrac)
    if nanfrac == 1.0:
        flag = "  <-- ALL NaN !!!"
    print("  %-30s dtype=%-10s nan=%.3f%s" % (f, col.dtype, nanfrac, flag))

# correlate: are the NaN g rows the ones with a specific feature missing?
print("\n--- for NaN-g rows, which features are NaN? ---")
if bad.any():
    for f in FEATURES:
        if f in df.columns:
            col = df[f].to_numpy()
            try:
                cn = ~np.isfinite(col.astype(float))
            except Exception:
                continue
            if cn[bad].mean() > 0.5:
                print("  %-30s NaN in %.0f%% of bad rows (vs %.0f%% of good)"
                      % (f, 100*cn[bad].mean(), 100*cn[~bad].mean() if (~bad).any() else 0))
