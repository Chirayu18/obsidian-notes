import glob, numpy as np, pandas as pd

BASE = "/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/"
pqs = [p for p in glob.glob(BASE+"**/*.parquet", recursive=True) if "sumw_records" not in p]
print("parquet files:", len(pqs))
df = pd.concat([pd.read_parquet(p) for p in pqs], ignore_index=True)
print("TOTAL training rows:", len(df))
print("columns:", list(df.columns))

# ---- VETO INTEGRITY ----
l1 = df["lepton1_pdgId"].astype(int).abs()
l2 = df["lepton2_pdgId"].astype(int).abs()
has_pair = df["lepton1_pdgId"].astype(int) != 0
is_emu = ((l1==11)&(l2==13)) | ((l1==13)&(l2==11))
n_emu = int((has_pair & is_emu).sum())
is_sf = has_pair & (((l1==11)&(l2==11)) | ((l1==13)&(l2==13)))
print("\n=== VETO CHECK ===")
print("  rows with a pair:", int(has_pair.sum()))
print("  emu-pair rows (MUST be 0):", n_emu)
print("  same-flavor-pair rows:", int(is_sf.sum()))
print("  no-pair rows:", int((~has_pair).sum()))

# ---- WEIGHT / SIGN ----
wcol = "weight_nominal" if "weight_nominal" in df.columns else None
print("\n=== WEIGHT ===")
if wcol:
    w = df[wcol].astype(float)
    print(f"  {wcol}: nonnull {w.notna().mean():.3f}  frac>0 {np.mean(w>0):.4f}  mean|w| {np.nanmean(np.abs(w)):.1f}")
if "genweight_sign" in df.columns:
    gs = df["genweight_sign"].astype(float)
    print(f"  genweight_sign: frac>0 {np.mean(gs>0):.4f}")

# ---- GEN-FEATURE SUPPORT (training region) ----
print("\n=== TRAINING gen-feature support ===")
for c in ["lhe_vpt","lhe_ht","lhe_htincoming","lhe_nc","lhe_nb","lhe_njets","lhe_npnlo","genparton1_pt"]:
    if c in df.columns:
        s = df[c].astype(float)
        print("  %-16s mean %8.2f  p50 %8.2f  p95 %9.2f  max %9.2f" % (
            c, np.nanmean(s), np.nanpercentile(s,50), np.nanpercentile(s,95), np.nanmax(s)))
if "lhe_nc" in df.columns:
    print("  frac(lhe_nc>=1):", float((df["lhe_nc"]>=1).mean()))
    print("  lhe_nc value counts:", df["lhe_nc"].astype(int).value_counts().sort_index().to_dict())

# ---- per dataset row split ----
if "dataset" in df.columns:
    print("\n=== rows per dataset ===")
    print(df["dataset"].value_counts().to_dict())
