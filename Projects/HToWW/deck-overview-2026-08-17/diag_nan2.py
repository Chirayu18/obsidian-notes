import glob
import numpy as np, pandas as pd

pqs = glob.glob("/tmp/negrw_smoke_out/**/*.parquet", recursive=True)
df = pd.concat([pd.read_parquet(f) for f in pqs], ignore_index=True)
g = df["weight_negrw"].to_numpy()
bad = ~np.isfinite(g)
print("rows: %d | NaN-g rows: %d (%.1f%%)" % (len(df), bad.sum(), 100*bad.mean()))

# what distinguishes the bad rows? look at non-feature columns
print("\n--- bad rows: identity / weights ---")
cols = [c for c in ["weight_nominal", "weight_genweight", "genweight_sign", "event",
                    "lhe_njets", "lhe_vpt", "genparton_multiplicity"] if c in df.columns]
print(df.loc[bad, cols].head(12).to_string())

print("\n--- good rows for comparison ---")
print(df.loc[~bad, cols].head(5).to_string())

# is weight_nominal also nan on bad rows?
w = df["weight_nominal"].to_numpy()
print("\nweight_nominal NaN on bad rows: %.0f%%" % (100*np.mean(~np.isfinite(w[bad]))))
print("weight_nominal NaN on good rows: %.0f%%" % (100*np.mean(~np.isfinite(w[~bad]))))
print("\nSum w over GOOD rows only      = %.6g" % w[~bad][np.isfinite(w[~bad])].sum())
gg = g[~bad]; ww = w[~bad]
m = np.isfinite(ww)
print("Sum |w|*g over GOOD rows only  = %.6g" % (np.abs(ww[m])*gg[m]).sum())
