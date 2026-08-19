"""tt-CR purity: MVA-defined (argmax==tt, NO kinematic cuts) vs cut-defined.

Purity = fraction of events in the region whose TRUE process is tt.
Also reports signal contamination, which is what makes a CR safe to fit.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts" / "combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR = "2022postEE"; WF = "hww_combine_fixed"
MVA = Path("/eos/user/c/cgupta/higgscharm/outputs") / WF / YEAR / "mva"
CLASSES = ["hplusc", "higgsbkg", "tt", "st", "diboson", "vjets"]
SC = [f"mva_score_{c}" for c in CLASSES]

cfg = WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s = gather_samples(YEAR, cfg.combine["process_map"])
s2p = {s: cp for cp, ss in c2s.items() for s in ss}

need = SC + ["mtll", "mtl2", "dilepton_mass"]
frames = []
for s, cp in sorted(s2p.items()):
    p = MVA / f"{s}.parquet"
    if not p.exists():
        continue
    av = set(pq.read_schema(p).names)
    if not set(SC).issubset(av):
        continue
    d = pd.read_parquet(p, columns=[c for c in need if c in av])
    if len(d) == 0:
        continue
    d["true_proc"] = cp
    frames.append(d)

df = pd.concat(frames, ignore_index=True)
sc = df[SC].to_numpy(float)
df["argmax"] = [CLASSES[i] for i in np.argmax(sc, axis=1)]
mtll = df.mtll.to_numpy(float)
mtl2 = df.mtl2.to_numpy(float)
mll = df.dilepton_mass.to_numpy(float)

REGIONS = {
    "MVA tt CR (argmax==tt, NO kin cuts)":        (df["argmax"] == "tt").to_numpy(),
    "Cut tt CR (mTl2>30 & mTll<=60)":             (mtl2 > 30) & (mtll <= 60),
    "Cut tt CR (mll>72)":                         (mll > 72),
    "Cut tt CR (mll>72 & mTl2>30 & mTll>60)":     (mll > 72) & (mtl2 > 30) & (mtll > 60),
    "MVA tt CR AND cut tt CR (overlap)":          ((df["argmax"] == "tt").to_numpy()) & (mtl2 > 30) & (mtll <= 60),
}

print("pooled: {:,}".format(len(df)))
print()
hdr = "%-42s %11s %9s %9s %11s" % ("region", "N", "tt purity", "sig frac", "non-tt bkg")
print(hdr); print("-" * len(hdr))
rows = []
for name, m in REGIONS.items():
    n = int(m.sum())
    if n == 0:
        print("%-42s %11d %9s" % (name, 0, "--")); continue
    tp = df.true_proc.to_numpy()[m]
    pur = (tp == "tt").mean() * 100
    sig = (tp == "hplusc").mean() * 100
    oth = 100 - pur - sig
    rows.append((name, n, pur, sig, oth))
    print("%-42s %11s %8.2f%% %8.4f%% %10.2f%%" % (name, format(n, ","), pur, sig, oth))

print()
print("=== composition of the MVA tt CR (true process) ===")
m = (df["argmax"] == "tt").to_numpy()
tp = df.true_proc.to_numpy()[m]
for proc in ["tt", "st", "higgsbkg", "diboson", "vjets", "hplusc"]:
    c = int((tp == proc).sum())
    print("   %-10s %10s (%6.2f%%)" % (proc, format(c, ","), 100 * c / len(tp)))
