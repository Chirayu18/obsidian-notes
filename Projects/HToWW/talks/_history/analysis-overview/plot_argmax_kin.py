"""mll / mTll / mTl2 split by the v11 model's ARGMAX predicted class.

Question this answers: does the v11 network implicitly impose kinematic cuts /
edges on mll, mTll, mTl2 for the classes it predicts?

So the split is purely by argmax over the six mva_score_* columns -- the sample an
event came from is NOT used. All MC+signal parquets are pooled. Events are RAW and
UNWEIGHTED (no lumi*xsec/sumw, no negrw): a physics weight would hide a hard edge.

argmax classes collapsed to three:
    signal = hplusc
    higgs  = higgsbkg
    other  = tt, st, diboson, vjets
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

WORKFLOW = "hww_combine_fixed"
YEAR = "2022postEE"
MVA = Path("/eos/user/c/cgupta/higgscharm/outputs") / WORKFLOW / YEAR / "mva"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT.mkdir(parents=True, exist_ok=True)

CLASSES = ["hplusc", "higgsbkg", "tt", "st", "diboson", "vjets"]
SCORE_COLS = [f"mva_score_{c}" for c in CLASSES]
# argmax index -> display class
IDX2DISP = {0: "signal", 1: "higgs", 2: "other", 3: "other", 4: "other", 5: "other"}
DISPLAY = ["signal", "higgs", "other"]

KIN = ["dilepton_mass", "mtll", "mtl2"]
VARS = {
    "dilepton_mass": dict(label=r"$m_{\ell\ell}$ [GeV]",   key="mll",  bins=np.linspace(0, 140, 71)),
    "mtll":          dict(label=r"$m_T^{\ell\ell}$ [GeV]", key="mTll", bins=np.linspace(0, 400, 81)),
    "mtl2":          dict(label=r"$m_T^{\ell_2}$ [GeV]",   key="mTl2", bins=np.linspace(0, 200, 81)),
}
LABELS = {
    "signal": "argmax = signal (hplusc)",
    "higgs":  "argmax = higgs bkg",
    "other":  r"argmax = other (t$\bar{t}$, st, VV, V+jets)",
}
COLORS = {"signal": "#d62728", "higgs": "#1f77b4", "other": "#555555"}

vals = {d: {v: [] for v in KIN} for d in DISPLAY}
n_ev = {d: 0 for d in DISPLAY}

# Take EXACTLY the per-sample parquets the fit consumes. The mva/ dir also holds
# group-level merges (H+c.parquet, tt.parquet, ...) whose events are duplicates of
# the per-sample files -- globbing *.parquet would double-count every event.
cfg = WorkflowConfigBuilder(workflow=WORKFLOW).build_workflow_config()
combine_to_samples = gather_samples(YEAR, cfg.combine["process_map"])
samples = sorted({s for v in combine_to_samples.values() for s in v})
files = [MVA / f"{s}.parquet" for s in samples]
files = [f for f in files if f.exists()]
print(f"pooling {len(files)} per-sample parquets "
      f"(of {len(samples)} samples in process_map)\n")
for p in files:
    avail = set(pq.read_schema(p).names)
    if not set(SCORE_COLS).issubset(avail):
        print(f"  [skip] {p.name}: no scores")
        continue
    df = pd.read_parquet(p, columns=SCORE_COLS + KIN)
    if len(df) == 0:
        continue
    am = np.argmax(df[SCORE_COLS].to_numpy(dtype=np.float64), axis=1)
    for i, disp in IDX2DISP.items():
        m = (am == i)
        if not m.any():
            continue
        n_ev[disp] += int(m.sum())
        for v in KIN:
            vals[disp][v].append(df[v].to_numpy(dtype=np.float64)[m])
    print(f"  [ok] {p.name:<50s} N={len(df):>8d}")

for d in DISPLAY:
    for v in KIN:
        vals[d][v] = np.concatenate(vals[d][v]) if vals[d][v] else np.array([])

print("\n=== raw event counts by ARGMAX class (all MC pooled) ===")
tot = sum(n_ev.values())
for d in DISPLAY:
    print(f"{d:<8s} {n_ev[d]:>10d}  ({100.0*n_ev[d]/tot:5.2f}%)")

# support / edge diagnostics -- this is what reveals an implicit cut
print("\n=== kinematic support by argmax class (raw, unweighted) ===")
hdr = f"{'var':<14s} {'class':<8s} {'N':>9s} {'min':>9s} {'p0.1':>9s} {'p1':>9s} {'p50':>9s} {'p99':>9s} {'max':>9s}"
print(hdr)
lines = [hdr]
for v in KIN:
    for d in DISPLAY:
        a = vals[d][v]
        if a.size == 0:
            continue
        q = np.percentile(a, [0.1, 1, 50, 99])
        ln = (f"{v:<14s} {d:<8s} {a.size:>9d} {a.min():>9.2f} {q[0]:>9.2f} "
              f"{q[1]:>9.2f} {q[2]:>9.2f} {q[3]:>9.2f} {a.max():>9.2f}")
        print(ln)
        lines.append(ln)
    print()
    lines.append("")

for v in KIN:
    spec = VARS[v]
    bins = spec["bins"]
    ctr = 0.5 * (bins[1:] + bins[:-1])
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))

    # (a) raw counts, log-y: a hard cut shows as a cliff to zero
    ax = axes[0]
    for d in DISPLAY:
        h, _ = np.histogram(vals[d][v], bins=bins)
        ax.step(ctr, h, where="mid", color=COLORS[d], lw=1.8, label=f"{LABELS[d]}  (N={n_ev[d]:,})")
    ax.set_yscale("log")
    ax.set_xlabel(spec["label"]); ax.set_ylabel("raw events / bin (unweighted)")
    ax.set_title("raw counts (log) - a hard cut = cliff to zero")
    ax.legend(fontsize=8, frameon=False); ax.grid(alpha=0.25, ls=":")
    ax.set_xlim(bins[0], bins[-1])

    # (b) shape-normalised, linear
    ax = axes[1]
    for d in DISPLAY:
        h, _ = np.histogram(vals[d][v], bins=bins)
        s = h.sum()
        ax.step(ctr, h / s if s else h, where="mid", color=COLORS[d], lw=1.8, label=LABELS[d])
    ax.set_xlabel(spec["label"]); ax.set_ylabel("fraction of class")
    ax.set_title("shape within each argmax class")
    ax.legend(fontsize=8, frameon=False); ax.grid(alpha=0.25, ls=":")
    ax.set_xlim(bins[0], bins[-1])

    fig.suptitle(f"{spec['label']} by v11 ARGMAX class - {YEAR}, all MC pooled, raw/unweighted",
                 fontsize=11)
    fig.tight_layout()
    f = OUT / f"argmax_{spec['key']}.png"
    fig.savefig(f, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", f)

with open(OUT / "argmax_support.txt", "w") as fh:
    fh.write(f"# v11 argmax classes, {YEAR}, all MC pooled, raw unweighted\n")
    for d in DISPLAY:
        fh.write(f"# {d}: {n_ev[d]} events\n")
    fh.write("\n".join(lines) + "\n")
print("done")
