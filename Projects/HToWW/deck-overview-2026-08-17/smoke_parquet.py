"""End-to-end smoke: real BaseProcessor -> parquet, with the NEW in-image model.
Confirms weight_negrw / weight_negrw_std land in the SR parquet and vary."""
import json, sys, glob, os
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
sys.path.insert(0, R)
from analysis.processors.base import BaseProcessor

OUT = "/tmp/negrw_smoke_out"
os.system(f"rm -rf {OUT}; mkdir -p {OUT}")

fs = json.load(open(f"{R}/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"))
DATASET = "DYto2L_2Jets_50"
entry = fs[DATASET]
files = entry["files"] if isinstance(entry, dict) and "files" in entry else entry
url = files[0] if isinstance(files, list) else list(files.keys())[0]
print("file:", url)

events = NanoEventsFactory.from_root(
    url, treepath="Events", schemaclass=NanoAODSchema, entry_stop=200000,
    metadata={"dataset": DATASET},
).events()
print("events read:", len(events))

p = BaseProcessor(workflow="hww_combine_fixed", year="2022postEE",
                  output_format="parquet", output_location=OUT)
p.process(events)

pqs = glob.glob(f"{OUT}/**/*.parquet", recursive=True)
print("\nparquet written:", len(pqs))
if not pqs:
    sys.exit("NO PARQUET -> no events passed SR selection in this chunk (try more entries)")

import pandas as pd
df = pd.concat([pd.read_parquet(f) for f in pqs], ignore_index=True)
print("rows:", len(df), "| cols:", len(df.columns))
for c in ["weight_negrw", "weight_negrw_std"]:
    print(f"  HAS {c}: {c in df.columns}")
if "weight_negrw" in df.columns:
    g = df["weight_negrw"].to_numpy(); s = df["weight_negrw_std"].to_numpy()
    print("\nweight_negrw : n_distinct=%d  range=[%.3f, %.3f]  mean=%.3f  std=%.3f"
          % (len(np.unique(g)), g.min(), g.max(), g.mean(), g.std()))
    print("weight_negrw_std: mean=%.4f  max=%.4f" % (s.mean(), s.max()))
    print("all g in [-1,1]:", bool(np.all((g >= -1) & (g <= 1))))
    print("any NaN:", bool(np.any(~np.isfinite(g))))
    w = df["weight_nominal"].to_numpy()
    print("\nfrac weight_nominal>0 in SR: %.3f" % (w > 0).mean())
    print("yield nominal  Sum w   = %.4g" % w.sum())
    print("yield reweight Sum|w|g = %.4g" % (np.abs(w) * g).sum())
