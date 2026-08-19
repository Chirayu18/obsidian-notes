import os, sys, glob
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, os.getcwd())
from coffea import processor
from coffea.nanoevents import NanoAODSchema
from analysis.processors.base import BaseProcessor
import numpy as np, pandas as pd

# one WtoLNu vjets file via eoscms (no grid proxy needed)
URLS = {"WtoLNu_2Jets": ["root://eoscms.cern.ch//eos/cms/store/mc/Run3Summer22EENanoAODv12/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2520000/4ac52a7f-8837-403a-a1b0-61f9a5862639.root"]}
out_loc = "/tmp/sr_negrw_test/"
os.system(f"rm -rf {out_loc}; mkdir -p {out_loc}")

out = processor.run_uproot_job(
    URLS, treename="Events",
    processor_instance=BaseProcessor(workflow="hww_combine_fixed", year="2022postEE",
                                     output_format="parquet", output_location=out_loc),
    executor=processor.iterative_executor,
    executor_args={"schema": NanoAODSchema, "workers": 1},
    chunksize=30000, maxchunks=6,
)
print("RUN OK")
pqs = [p for p in glob.glob(out_loc+"**/*.parquet", recursive=True) if "sumw" not in p]
print("parquet files:", len(pqs))
if not pqs:
    print("NO PARQUET (0 SR events in these chunks?) — cutflow:", 
          {k:v for k,v in out.get("metadata",{}).items()}); sys.exit(0)
df = pd.concat([pd.read_parquet(p) for p in pqs], ignore_index=True)
print("SR rows:", len(df))
print("has weight_negrw:", "weight_negrw" in df.columns, "| has weight_negrw_std:", "weight_negrw_std" in df.columns)
if "weight_negrw" in df.columns:
    g = df["weight_negrw"].astype(float); s = df["weight_negrw_std"].astype(float)
    print(f"  weight_negrw:     nonnull {g.notna().mean():.3f}  range [{g.min():.3f},{g.max():.3f}]  mean {g.mean():.3f}  (must be in [-1,1])")
    print(f"  weight_negrw_std: nonnull {s.notna().mean():.3f}  range [{s.min():.3f},{s.max():.3f}]  mean {s.mean():.3f}")
    print(f"  in-range check: all g in [-1,1]? {bool(((g>=-1.0001)&(g<=1.0001)).all())}")
    # SR should be emu pairs -> confirm this is the tight SR
    l1=df.get("lepton1_pdgId"); 
    print("  sample gen features present:", [c for c in ["lhe_vpt","lhe_nc","genparton1_pt"] if c in df.columns])
    # cross-check g vs frac-positive of weight_nominal
    w=df["weight_nominal"].astype(float)
    print(f"  weight_nominal frac>0 {np.mean(w>0):.3f}  vs mean g {(g.mean()+1)/2:.3f} (P+ proxy)")
