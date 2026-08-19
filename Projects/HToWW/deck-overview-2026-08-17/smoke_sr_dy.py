import os, sys, glob
os.environ.setdefault("X509_USER_PROXY", "/tmp/x509up_u151861")
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, os.getcwd())
from coffea import processor
from coffea.nanoevents import NanoAODSchema
from analysis.processors.base import BaseProcessor
import numpy as np, pandas as pd

URLS = {"DYto2L_2Jets_50": ["root://cmsdcache-kit-disk.gridka.de:1094//store/mc/Run3Summer22EENanoAODv12/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2520000/098581d9-40df-4e56-9e33-f5d452fa4ee3.root"]}
out_loc = "/tmp/sr_negrw_dy/"
os.system(f"rm -rf {out_loc}; mkdir -p {out_loc}")
out = processor.run_uproot_job(
    URLS, treename="Events",
    processor_instance=BaseProcessor(workflow="hww_combine_fixed", year="2022postEE",
                                     output_format="parquet", output_location=out_loc),
    executor=processor.iterative_executor,
    executor_args={"schema": NanoAODSchema, "workers": 1},
    chunksize=50000, maxchunks=8,
)
pqs = [p for p in glob.glob(out_loc+"**/*.parquet", recursive=True) if "sumw" not in p]
print("parquet files:", len(pqs))
df = pd.concat([pd.read_parquet(p) for p in pqs], ignore_index=True) if pqs else pd.DataFrame()
print("SR rows:", len(df))
if len(df) and "weight_negrw" in df.columns:
    g=df["weight_negrw"].astype(float); s=df["weight_negrw_std"].astype(float)
    print(f"  g: n={len(g)} nonnull {g.notna().mean():.3f} range [{g.min():.3f},{g.max():.3f}] mean {g.mean():.3f} std {g.std():.3f}")
    print(f"  g percentiles [5,25,50,75,95]:", np.round(np.nanpercentile(g,[5,25,50,75,95]),3).tolist())
    print(f"  n distinct g values: {g.round(4).nunique()}  (must be >1 -> g varies with x)")
    print(f"  delta_g: range [{s.min():.4f},{s.max():.4f}] mean {s.mean():.4f}")
    print(f"  all g in [-1,1]? {bool(((g>=-1.001)&(g<=1.001)).all())}")
    w=df["weight_nominal"].astype(float)
    print(f"  weight_nominal frac>0 {np.mean(w>0):.3f}")
    # sanity: g vs lhe_vpt correlation (higher vpt -> different neg fraction)
    if "lhe_vpt" in df.columns:
        vpt=df["lhe_vpt"].astype(float)
        print(f"  corr(g, lhe_vpt) = {np.corrcoef(g,vpt)[0,1]:.3f}")
