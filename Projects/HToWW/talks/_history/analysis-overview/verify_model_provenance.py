"""Decisive test: does the stored weight_negrw column reproduce from the Jul-15 model?
If yes -> parquets carry the CURRENT model. If no -> stale (June) model."""
import numpy as np, pandas as pd, joblib, sys

MODEL = "/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models.joblib"
P = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/DYto2L_2Jets_50.parquet"

blob = joblib.load(MODEL)
models = blob["models"] if isinstance(blob, dict) and "models" in blob else blob
feats = blob.get("features") if isinstance(blob, dict) else None
print("model file:", MODEL)
print("  n_models:", len(models))
print("  features:", feats)

df = pd.read_parquet(P)
print("\nparquet:", P)
print("  rows:", len(df))
cols = [c for c in df.columns if "negrw" in c]
print("  negrw cols:", cols)
if not cols:
    sys.exit("NO negrw COLUMNS -> nothing to verify")

if feats is None:
    sys.exit("model blob has no feature list; cannot re-score")
missing = [f for f in feats if f not in df.columns]
if missing:
    sys.exit(f"features missing from parquet: {missing}")

X = df[feats].to_numpy()
ok = np.isfinite(X).all(axis=1)
X = X[ok]
print(f"  scoring {len(X)} finite rows with {len(models)} models ...")
P_list = np.stack([m.predict_proba(X)[:, 1] for m in models])
p_mean = P_list.mean(axis=0)
g_recomp = 2 * p_mean - 1
g_std_recomp = 2 * P_list.std(axis=0)

g_store = df.loc[ok, "weight_negrw"].to_numpy()
d = np.abs(g_recomp - g_store)
print(f"\n  weight_negrw:      max|diff| = {d.max():.3e}   mean = {d.mean():.3e}")
if "weight_negrw_std" in df.columns:
    s_store = df.loc[ok, "weight_negrw_std"].to_numpy()
    ds = np.abs(g_std_recomp - s_store)
    print(f"  weight_negrw_std:  max|diff| = {ds.max():.3e}   mean = {ds.mean():.3e}")

print("\n  VERDICT:", "MATCHES Jul-15 model (current)" if d.max() < 1e-6
      else "DOES NOT MATCH -> parquets carry a DIFFERENT (stale) model")
