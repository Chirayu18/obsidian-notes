"""argmax=tt density across the (mTll, mTl2) plane, with the top-CR cuts drawn.

Mirrors internalised_2d_plane.png (which shows argmax=signal vs the SR cuts) but for
the tt class, so the two can be read side by side: the signal plot shows the network
carving out the SR without being told to; this one shows where the tt class lives and
how the hand-made top CR (mTl2>30 & mTll<=60) sits inside it.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts" / "combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR = "2022postEE"; WF = "hww_combine_fixed"
MVA = Path("/eos/user/c/cgupta/higgscharm/outputs") / WF / YEAR / "mva"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "."); OUT.mkdir(parents=True, exist_ok=True)
CLASSES = ["hplusc", "higgsbkg", "tt", "st", "diboson", "vjets"]
SC = [f"mva_score_{c}" for c in CLASSES]
MIN_N = 50

cfg = WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s = gather_samples(YEAR, cfg.combine["process_map"])
samples = sorted({s for v in c2s.values() for s in v})

need = SC + ["mtll", "mtl2", "dilepton_mass"]
ch = []
for s in samples:
    p = MVA / f"{s}.parquet"
    if not p.exists():
        continue
    av = set(pq.read_schema(p).names)
    if not set(SC).issubset(av):
        continue
    ch.append(pd.read_parquet(p, columns=[c for c in need if c in av]))

df = pd.concat(ch, ignore_index=True)
sc = df[SC].to_numpy(float)
am = np.argmax(sc, axis=1)
mtll = df.mtll.to_numpy(float)
mtl2 = df.mtl2.to_numpy(float)
is_tt = (am == CLASSES.index("tt")).astype(float)
print("pooled %s   argmax=tt %s" % (format(len(df), ","), format(int(is_tt.sum()), ",")))

xb = np.linspace(0, 300, 61)
yb = np.linspace(0, 160, 41)
n_all, _, _ = np.histogram2d(mtll, mtl2, bins=[xb, yb])
n_tt, _, _ = np.histogram2d(mtll, mtl2, bins=[xb, yb], weights=is_tt)
frac = np.where(n_all >= MIN_N, n_tt / np.maximum(n_all, 1), np.nan)

fig, ax = plt.subplots(figsize=(8.6, 5.4))
pcm = ax.pcolormesh(xb, yb, 100 * frac.T, cmap="viridis", vmin=0, vmax=np.nanmax(100 * frac))
cb = fig.colorbar(pcm, ax=ax); cb.set_label("% of events with argmax = tt")

# top-CR definition: mTl2 > 30 & mTll <= 60
ax.axvline(60, color="#ff2d95", lw=2.4, ls="--", label=r"top CR  $m_T^{\ell\ell}\leq 60$")
ax.axhline(30, color="#00e5ff", lw=2.4, ls="--", label=r"top CR  $m_T^{\ell_2}>30$")
# shade the cut-defined top CR box
ax.add_patch(plt.Rectangle((0, 30), 60, yb[-1] - 30, fill=True, color="#ff2d95",
                           alpha=0.13, zorder=3))
ax.text(30, 148, "cut-defined\ntop CR", color="#ff2d95", fontsize=9, ha="center",
        va="top", weight="bold", zorder=4)

ax.set_xlabel(r"$m_T^{\ell\ell}$ [GeV]")
ax.set_ylabel(r"$m_T^{\ell_2}$ [GeV]")
ax.set_title("v11 argmax=tt density vs the top-CR cuts\n"
             "(2022postEE MC pooled, raw; cells with N<%d blank)" % MIN_N, fontsize=10)
ax.legend(loc="upper right", fontsize=9, framealpha=0.85)
fig.tight_layout()
f = OUT / "cr_topcr_argmax_tt_plane.png"
fig.savefig(f, dpi=145, bbox_inches="tight")
plt.close(fig)
print("wrote", f)

# numbers for the caption
box = (mtl2 > 30) & (mtll <= 60)
print("  cut-defined top CR      : N=%s  argmax=tt %.2f%%" %
      (format(int(box.sum()), ","), 100 * is_tt[box].mean()))
print("  everything outside it   : N=%s  argmax=tt %.2f%%" %
      (format(int((~box).sum()), ","), 100 * is_tt[~box].mean()))
print("  whole plane             : N=%s  argmax=tt %.2f%%" %
      (format(len(df), ","), 100 * is_tt.mean()))
inbox_of_all_tt = is_tt[box].sum() / is_tt.sum()
print("  fraction of ALL argmax=tt events inside the cut box: %.2f%%" % (100 * inbox_of_all_tt))
