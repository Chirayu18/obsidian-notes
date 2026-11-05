"""Backup plots: EVERY combine input template.

B1  per-channel stacked nominal templates + data_obs + MC-stat band   (6 panels)
B2  per-channel, per-process nominal templates with MC-stat errors     (6 x 6 grid)
B3  every shape systematic, as Up/Down ratio to nominal, per channel   (signal region + one per CR)
"""
import numpy as np, uproot, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from collections import defaultdict
import os

F   = "/eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_v4.root"
OUT = "/eos/user/c/cgupta/HToWW/plots/negrw"
os.makedirs(OUT, exist_ok=True)

CHAN = ["SR_hplusc","CR_higgsbkg","CR_tt","CR_st","CR_diboson","CR_vjets"]
PROC = ["hplusc","higgsbkg","tt","st","diboson","vjets"]
COL  = {"hplusc":"#e41a1c","higgsbkg":"#ff7f00","tt":"#377eb8",
        "st":"#4daf4a","diboson":"#984ea3","vjets":"#a65628"}

f = uproot.open(F)
keys = {k.split(";")[0] for k in f.keys()}
def get(name):
    h = f[name]; return h.values(), np.sqrt(h.variances())

# ---------------- B1: stacked nominal per channel ----------------
SIGSCALE = 2000            # ONE global factor for every panel, so shapes are comparable
fig, axes = plt.subplots(2, 3, figsize=(15.5, 8))
for ax, ch in zip(axes.ravel(), CHAN):
    bottom = None; tot = None; tote2 = None
    for p in PROC:
        if p == "hplusc":            # signal drawn as a line, not stacked
            continue
        v, e = get(f"{ch}_{p}")
        x = np.arange(len(v))
        ax.bar(x, v, 0.92, bottom=bottom, color=COL[p], label=p,
               edgecolor="white", lw=.3)
        bottom = v if bottom is None else bottom + v
        tot    = v if tot    is None else tot + v
        tote2  = e**2 if tote2 is None else tote2 + e**2
    te = np.sqrt(tote2)
    x = np.arange(len(tot))
    ax.bar(x, 2*te, 0.92, bottom=tot-te, color="none", edgecolor="k",
           hatch="////", lw=0, label="MC-stat")
    d, _ = get(f"{ch}_data_obs")
    ax.errorbar(x, d, yerr=np.sqrt(np.maximum(d, 0)), fmt="ko", ms=3.5,
                lw=1, label="Asimov")
    s, _ = get(f"{ch}_hplusc")
    ax.plot(x, s*SIGSCALE, "-", color=COL["hplusc"], lw=2,
            label=f"H+c ($\\times${SIGSCALE:g})")
    ax.set_title(ch, fontsize=11); ax.set_xlabel("discriminant bin", fontsize=9)
    ax.set_ylabel("events / bin", fontsize=9); ax.grid(alpha=.25, axis="y")
    ax.tick_params(labelsize=8)
axes[0,0].legend(fontsize=7.5, ncol=2)
fig.suptitle("All combine input channels — stacked nominal templates (v11, 2022postEE)",
             fontsize=13)
fig.tight_layout(); fig.savefig(f"{OUT}/B1_all_channels_stacked.png", dpi=140); plt.close(fig)
print("wrote B1")

# ---------------- B2: per-process grid ----------------
fig, axes = plt.subplots(6, 6, figsize=(17, 14), sharex=True)
for i, ch in enumerate(CHAN):
    for j, p in enumerate(PROC):
        ax = axes[i, j]
        v, e = get(f"{ch}_{p}")
        x = np.arange(len(v))
        live = (v > 1e-3) | (e > 0)
        ax.errorbar(x[live], v[live], yerr=e[live], fmt="o", ms=3.5,
                    color=COL[p], capsize=2, lw=1.2)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(v > 1e-3, 100*e/v, np.nan)
        mr = np.nanmean(rel[live]) if live.any() else np.nan
        ax.set_title(f"{ch} / {p}", fontsize=8)
        ax.tick_params(labelsize=7); ax.grid(alpha=.25)
        if np.isfinite(mr):
            ax.text(.97, .93, f"<rel err> {mr:.0f}%", ha="right", va="top",
                    transform=ax.transAxes, fontsize=7,
                    color="#b2182b" if mr > 50 else "black")
        real = v[v > 1e-3]
        if real.size and real.max()/real.min() > 50:
            ax.set_yscale("log")
            ax.set_ylim(max(real.min()*0.2, 1e-4), real.max()*5)
fig.suptitle("Every combine template: 6 channels x 6 processes, nominal + MC-stat error",
             fontsize=13, y=.997)
fig.tight_layout(); fig.savefig(f"{OUT}/B2_all_templates_grid.png", dpi=115); plt.close(fig)
print("wrote B2")

# ---------------- B3: every shape systematic as ratio to nominal ----------------
systs = defaultdict(set)
for k in keys:
    for ch in CHAN:
        for p in PROC:
            pre = f"{ch}_{p}_"
            if k.startswith(pre) and k.endswith("Up"):
                systs[(ch, p)].add(k[len(pre):-2])
allsys = sorted({s for v in systs.values() for s in v})
print(f"  {len(allsys)} distinct shape systematics: {allsys}")

for ch in CHAN:
    ncol = 3; nrow = int(np.ceil(len(PROC)/ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 4.2*nrow), sharex=True)
    for ax, p in zip(axes.ravel(), PROC):
        nom, _ = get(f"{ch}_{p}")
        x = np.arange(len(nom))
        n = 0
        for s in allsys:
            ku, kd = f"{ch}_{p}_{s}Up", f"{ch}_{p}_{s}Down"
            if ku not in keys or kd not in keys:
                continue
            u, _ = get(ku); d, _ = get(kd)
            with np.errstate(divide="ignore", invalid="ignore"):
                ru = np.where(nom > 1e-3, u/nom, np.nan)
                rd = np.where(nom > 1e-3, d/nom, np.nan)
            ax.plot(x, ru, "-",  lw=1.1, alpha=.8, label=s if n < 14 else None)
            ax.plot(x, rd, "--", lw=1.1, alpha=.8,
                    color=ax.lines[-1].get_color())
            n += 1
        ax.axhline(1, color="k", lw=1, ls=":")
        ax.set_title(f"{ch} / {p}  ({n} shapes)", fontsize=10)
        ax.set_ylabel("variation / nominal", fontsize=8)
        ax.set_xlabel("bin", fontsize=8); ax.grid(alpha=.25)
        ax.tick_params(labelsize=8); ax.set_ylim(.5, 1.5)
        if n:
            ax.legend(fontsize=5.6, ncol=2, loc="upper left")
    fig.suptitle(f"{ch}: all shape systematics (solid = Up, dashed = Down)", fontsize=12)
    fig.tight_layout(); fig.savefig(f"{OUT}/B3_shapes_{ch}.png", dpi=120); plt.close(fig)
    print(f"  wrote B3_shapes_{ch}")
