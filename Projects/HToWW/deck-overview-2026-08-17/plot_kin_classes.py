"""Plot mll, mTll, mTl2 for signal / higgs-bkg / other-bkg using the v11 model tree.

Classes are the combine process groups from the workflow's `process_map`, collapsed
to three:
    signal   = hplusc            (H+c)
    higgs    = higgsbkg          (H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB)
    other    = tt + st + diboson + vjets

Normalisation and the vjets neg-weight reweighting are taken from
scripts/combine/make_combine_inputs.py so these plots match the fit templates.
"""
import sys, logging
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "combine"))

from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples, read_scale, load_lumi

logging.basicConfig(level=logging.WARNING)

WORKFLOW = "hww_combine_fixed"
YEAR = "2022postEE"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT.mkdir(parents=True, exist_ok=True)

BASE = Path("/eos/user/c/cgupta/higgscharm/outputs") / WORKFLOW / YEAR
MVA = BASE / "mva"

cfg = WorkflowConfigBuilder(workflow=WORKFLOW).build_workflow_config()
combine = cfg.combine
process_map = combine["process_map"]
lumi = load_lumi(YEAR)
combine_to_samples = gather_samples(YEAR, process_map)

# three display classes <- combine processes
GROUPS = {
    "signal": ["hplusc"],
    "higgs":  ["higgsbkg"],
    "other":  ["tt", "st", "diboson", "vjets"],
}
LABELS = {
    "signal": r"Signal  H+c $\to$ WW",
    "higgs":  r"Higgs bkg (ggH, VBF, VH, ttH, H+b)",
    "other":  r"Other bkg (t$\bar{t}$, single-t, VV, V+jets)",
}
COLORS = {"signal": "#d62728", "higgs": "#1f77b4", "other": "#7f7f7f"}

VARS = {
    "dilepton_mass": dict(label=r"$m_{\ell\ell}$ [GeV]", bins=np.linspace(12, 120, 37), key="mll"),
    "mtll":          dict(label=r"$m_T^{\ell\ell}$ [GeV]", bins=np.linspace(0, 300, 41), key="mTll"),
    "mtl2":          dict(label=r"$m_T^{\ell_2}$ [GeV]",  bins=np.linspace(0, 160, 41), key="mTl2"),
}

COLS = list(VARS.keys()) + ["weight_nominal"]

# accumulate raw (value, weight) per display class
data = {g: {v: [] for v in VARS} for g in GROUPS}
wts  = {g: [] for g in GROUPS}
yields = {}
raw_counts = {}

for disp, cprocs in GROUPS.items():
    tot_y = 0.0
    tot_n = 0
    for cp in cprocs:
        for sample in combine_to_samples.get(cp, []):
            p = MVA / f"{sample}.parquet"
            if not p.exists():
                print(f"  [skip] {cp}/{sample}: no {p.name}")
                continue
            cols = list(COLS)
            # vjets negrw reweighting, exactly as process_sample does it
            need_negrw = (cp == "vjets")
            df = pd.read_parquet(p)
            if len(df) == 0:
                continue
            scale = read_scale(sample, YEAR, BASE, lumi)
            w = df["weight_nominal"].to_numpy(dtype=np.float64)
            if need_negrw and "weight_negrw" in df.columns:
                g_negrw = df["weight_negrw"].to_numpy(dtype=np.float64)
                sw, swg = w.sum(), (np.abs(w) * g_negrw).sum()
                renorm = (sw / swg) if swg != 0 else 1.0
                w = np.abs(w) * g_negrw * renorm
            w = w * scale
            for v in VARS:
                data[disp][v].append(df[v].to_numpy(dtype=np.float64))
            wts[disp].append(w)
            tot_y += w.sum()
            tot_n += len(df)
            print(f"  [ok]  {disp:<7s} {cp:<9s} {sample:<45s} N={len(df):>7d} yield={w.sum():.4g}")
    yields[disp] = tot_y
    raw_counts[disp] = tot_n

for disp in GROUPS:
    wts[disp] = np.concatenate(wts[disp]) if wts[disp] else np.array([])
    for v in VARS:
        data[disp][v] = np.concatenate(data[disp][v]) if data[disp][v] else np.array([])

print("\n=== yields (2022postEE, base e-mu + >=1 c-jet) ===")
for disp in GROUPS:
    print(f"{disp:<8s} raw={raw_counts[disp]:>9d}  weighted={yields[disp]:>14.3f}")

# ---------------- plots ----------------
for v, spec in VARS.items():
    bins = spec["bins"]
    ctr = 0.5 * (bins[1:] + bins[:-1])

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))

    # (a) shape-normalised overlay
    ax = axes[0]
    for disp in ["other", "higgs", "signal"]:
        h, _ = np.histogram(data[disp][v], bins=bins, weights=wts[disp])
        s = h.sum()
        if s != 0:
            h = h / s
        ax.step(ctr, h, where="mid", color=COLORS[disp], lw=2.0, label=LABELS[disp])
    ax.set_xlabel(spec["label"])
    ax.set_ylabel("normalised to unit area")
    ax.set_title("shape comparison")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.25, ls=":")
    ax.set_xlim(bins[0], bins[-1])

    # (b) absolute yields, log scale
    ax = axes[1]
    for disp in ["other", "higgs", "signal"]:
        h, _ = np.histogram(data[disp][v], bins=bins, weights=wts[disp])
        ax.step(ctr, h, where="mid", color=COLORS[disp], lw=2.0, label=LABELS[disp])
    ax.set_yscale("log")
    ax.set_xlabel(spec["label"])
    ax.set_ylabel("events / bin  (26.7 fb$^{-1}$)")
    ax.set_title("absolute yield")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.25, ls=":")
    ax.set_xlim(bins[0], bins[-1])

    fig.suptitle(f"{spec['label']} by class - v11 tree, {YEAR}, base e$\\mu$ + $\\geq$1 c-jet",
                 fontsize=11)
    fig.tight_layout()
    f = OUT / f"kin_{spec['key']}_classes.png"
    fig.savefig(f, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", f)

# summary table
with open(OUT / "kin_classes_yields.txt", "w") as fh:
    fh.write(f"# {WORKFLOW} {YEAR}  base e-mu + >=1 c-jet\n")
    fh.write(f"{'class':<8s} {'raw':>10s} {'weighted':>16s}\n")
    for disp in GROUPS:
        fh.write(f"{disp:<8s} {raw_counts[disp]:>10d} {yields[disp]:>16.4f}\n")
print("done")
