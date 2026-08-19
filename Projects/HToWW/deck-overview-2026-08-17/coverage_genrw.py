import glob, numpy as np, pandas as pd

BASE = "/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/"
pqs = [p for p in glob.glob(BASE+"**/*.parquet", recursive=True) if "sumw_records" not in p]
cols = ["lepton1_pdgId","lepton2_pdgId","lhe_vpt","lhe_ht","lhe_nc","lhe_nb","lhe_njets",
        "lhe_npnlo","genparton1_pt","weight_nominal","dilepton_pt","met_pt"]
df = pd.concat([pd.read_parquet(p, columns=cols) for p in pqs], ignore_index=True)

l1 = df["lepton1_pdgId"].astype(int).abs(); l2 = df["lepton2_pdgId"].astype(int).abs()
has_pair = df["lepton1_pdgId"].astype(int) != 0
is_sf = has_pair & (((l1==11)&(l2==11)) | ((l1==13)&(l2==13)))

# SR PROXY = same-flavor dilepton pairs (same ME as emu-SR, flavor-blind gen-x).
# CLASSIFIER DOMAIN = full training set.
sr   = df[is_sf]
full = df

FEATS = ["lhe_vpt","lhe_ht","lhe_nc","lhe_nb","lhe_njets","lhe_npnlo","genparton1_pt","dilepton_pt","met_pt"]
print("SR-proxy (same-flavor pairs) rows:", len(sr), " | full training rows:", len(full))
print("\n=== COVERAGE: is SR-proxy x inside training domain? ===")
print("%-16s | %-28s | %-28s | contained?" % ("feature","SR-proxy [p1,p50,p99,max]","train [p1,p50,p99,max]"))
ok_all = True
for f in FEATS:
    s = sr[f].astype(float).values; t = full[f].astype(float).values
    sp = np.nanpercentile(s,[1,50,99]); smax=np.nanmax(s)
    tp = np.nanpercentile(t,[1,50,99]); tmax=np.nanmax(t)
    # coverage: SR max must not exceed train max; SR min must not be below train min
    contained = (smax <= tmax*1.001) and (np.nanmin(s) >= np.nanmin(t)-1e-6)
    ok_all &= contained
    print("%-16s | [%6.1f %6.1f %7.1f %7.1f] | [%6.1f %6.1f %7.1f %7.1f] | %s" % (
        f, sp[0],sp[1],sp[2],smax, tp[0],tp[1],tp[2],tmax, "YES" if contained else "NO <<<"))

# tail check: fraction of SR-proxy above train p99 (should be small; extrapolation risk)
print("\n=== tail extrapolation risk (SR-proxy events beyond train p99) ===")
for f in ["lhe_vpt","lhe_ht","genparton1_pt"]:
    t99 = np.nanpercentile(full[f].astype(float), 99)
    frac = float((sr[f].astype(float) > t99).mean())
    print("  %-14s SR frac beyond train-p99: %.4f" % (f, frac))

# c-content: does SR proxy need lhe_nc>=1 support the training has?
print("\n=== lhe_nc coverage ===")
for name,d in [("SR-proxy",sr),("train",full)]:
    vc = d["lhe_nc"].astype(int).value_counts(normalize=True).sort_index()
    print("  %-9s nc frac:" % name, {k:round(v,4) for k,v in vc.items()})

# sign balance in SR proxy (for N_eff argument)
w = full["weight_nominal"].astype(float)
ws= sr["weight_nominal"].astype(float)
print("\n=== weight sign ===")
print("  full  frac>0 %.4f  Neff=%.0f (of %d)" % (np.mean(w>0), (w.sum()**2)/ (w**2).sum(), len(w)))
print("  SR-px frac>0 %.4f  Neff=%.0f (of %d)" % (np.mean(ws>0),(ws.sum()**2)/(ws**2).sum(), len(ws)))

print("\n=== COVERAGE VERDICT:", "PASS — SR-proxy contained in training domain" if ok_all else "FAIL — extrapolation regions exist", "===")
