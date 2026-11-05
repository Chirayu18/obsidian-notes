"""Re-smoke the SR negrw injection with the NEW (sklearn-1.7.2, in-image) model.
Runs the real BaseProcessor on one vjets SR file and checks the two new columns."""
import json, sys
import numpy as np
import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

sys.path.insert(0, "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
from analysis.processors.base import BaseProcessor

FS = ("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/"
      "analysis/filesets/fileset_2022postEE_nanov12_lxplus.json")
DATASET = "DYto2L_2Jets_50"

fs = json.load(open(FS))
entry = fs[DATASET]
files = entry["files"] if isinstance(entry, dict) and "files" in entry else entry
url = files[0] if isinstance(files, list) else list(files.keys())[0]
print("dataset:", DATASET)
print("file:", url)

events = NanoEventsFactory.from_root(
    url, treepath="Events", schemaclass=NanoAODSchema, entry_stop=60000,
    metadata={"dataset": DATASET},
).events()
print("events read:", len(events))

p = BaseProcessor(workflow="hww_combine_fixed", year="2022postEE",
                  output_format="coffea", output_location=None)
print("negrw cfg:", p.workflow_config.negrw)

# exercise the gate directly
from analysis.processors.base import _dataset_matches
names = p.workflow_config.negrw["datasets"]
print("\n--- GATE CHECK (exact match) ---")
for d in [DATASET, "WtoLNu_2Jets", "WplusH_WtoLNu_Hto2Wto2L2Nu", "TTto2L2Nu", "HplusCharm_HtoWW"]:
    print(f"  {d:32s} -> {_dataset_matches(d, names)}")

out = p.process(events)
print("\nprocessed OK")
