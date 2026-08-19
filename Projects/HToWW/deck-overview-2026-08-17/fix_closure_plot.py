#!/usr/bin/env python3
"""Regenerate the closure/N_eff plot with log-y + ratio panel so the hard-Vpt tail
(the analysis-critical, statistics-starved region) is actually visible."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 130, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3})
POS_C = "#2166ac"
d = np.load("/home/cgupta/.claude/jobs/af76ec6a/tmp/negrw_diagnostics.npz", allow_pickle=True)
b = d["vpt_bins"]; ctr = 0.5 * (b[:-1] + b[1:])
nom, rw = d["vpt_nom"], d["vpt_rw"]
ne_n, ne_r = d["vpt_neff_nom"], d["vpt_neff_rw"]
OUT = "/home/cgupta/obsidian-notes/Projects/HToWW/negrw-training/img"

# ---- closure: log-y + ratio panel ----
fig, (ax, rax) = plt.subplots(2, 1, figsize=(6.6, 5.2), sharex=True,
                              gridspec_kw=dict(height_ratios=[3, 1], hspace=0.08))
ax.step(ctr, nom, where="mid", color="k", lw=1.6, label="nominal  Σw")
ax.step(ctr, rw, where="mid", color=POS_C, ls="--", lw=1.6, label="reweighted  Σ|w|·g")
ax.set_yscale("log"); ax.set_ylabel("weighted yield")
ax.set_title("Yield closure — reweighted reproduces nominal")
ax.legend(frameon=False)
ratio = np.where(nom != 0, rw / nom, np.nan)
rax.step(ctr, ratio, where="mid", color=POS_C, lw=1.5)
rax.axhline(1.0, color="k", ls=":", lw=1)
rax.set_ylim(0.9, 1.1); rax.set_ylabel("rw / nom"); rax.set_xlabel("LHE V pT [GeV]")
fig.savefig(f"{OUT}/07_closure.png", bbox_inches="tight"); plt.close(fig)
print("wrote 07_closure.png")

# ---- N_eff: log-y + gain factor panel ----
fig, (ax, rax) = plt.subplots(2, 1, figsize=(6.6, 5.2), sharex=True,
                              gridspec_kw=dict(height_ratios=[3, 1], hspace=0.08))
ax.step(ctr, ne_n, where="mid", color="k", lw=1.6, label="nominal")
ax.step(ctr, ne_r, where="mid", color=POS_C, lw=1.6, label="reweighted")
ax.set_yscale("log"); ax.set_ylabel("$N_{eff}$ per bin")
gain_tot = ne_r.sum() / ne_n.sum()
ax.set_title(f"Effective statistics  (total {gain_tot:.2f}×,  +{100*(gain_tot-1):.0f}%)")
ax.legend(frameon=False)
gain = np.where(ne_n > 0, ne_r / ne_n, np.nan)
rax.step(ctr, gain, where="mid", color=POS_C, lw=1.5)
rax.axhline(1.0, color="k", ls=":", lw=1)
rax.set_ylabel("gain ×"); rax.set_xlabel("LHE V pT [GeV]")
rax.set_ylim(0, max(4.5, np.nanmax(gain) * 1.1))
fig.savefig(f"{OUT}/07b_neff_gain.png", bbox_inches="tight"); plt.close(fig)
print("wrote 07b_neff_gain.png")

# report the tail gains for the slides
print("\nper-bin N_eff gain (Vpt bin low edge -> gain x):")
for i in range(len(ctr)):
    if ne_n[i] > 0:
        print(f"  {b[i]:3.0f}-{b[i+1]:3.0f} GeV : {gain[i]:.2f}x   (Neff {ne_n[i]:.0f} -> {ne_r[i]:.0f})")
