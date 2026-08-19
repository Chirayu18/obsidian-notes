"""Pull the columns needed for actual-vs-predicted plots from the vjets SR output.
Writes a compact parquet to /tmp for local plotting."""
import glob, numpy as np, pandas as pd, pyarrow.parquet as pq

D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
DATASETS = ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]
COLS = ["weight_nominal", "weight_negrw", "weight_negrw_std", "lhe_vpt", "lhe_ht", "lhe_njets"]

frames = []
for s in DATASETS:
    fs = [f for f in glob.glob(f"{D}/{s}_*/base/*.parquet") if "sumw_records" not in f]
    for f in fs:
        try:
            names = pq.ParquetFile(f).schema.names
        except Exception:
            continue
        if "weight_negrw" not in names:
            continue
        use = [c for c in COLS if c in names]
        d = pd.read_parquet(f, columns=use)
        d["dataset"] = s
        frames.append(d)

df = pd.concat(frames, ignore_index=True)
# drop the rare all-null bookkeeping rows if any slipped in
df = df[np.isfinite(df["weight_nominal"]) & np.isfinite(df["weight_negrw"])].reset_index(drop=True)
df.to_parquet("/tmp/negrw_sr_forplots.parquet")
print("rows:", len(df), "| datasets:", df["dataset"].value_counts().to_dict())
print("cols:", list(df.columns))
