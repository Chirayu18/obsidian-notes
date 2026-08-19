import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
OUT="/home/cgupta/obsidian-notes/Projects/HToWW/deck-overview-2026-08-17/img"
BLUE, RED, GREY, GREEN = "#1f4e79", "#a01c1c", "#8c959d", "#2f6b3c"

# ---------- 1. limit cascade ----------
steps = ["early\ncard", "negrw +\nsumw fix", "+ 2D\nc-tag SF", "W+jets\njet-binned"]
vals  = [1371, 1150, 1164, 1034]
fig, ax = plt.subplots(figsize=(9,4.6))
ax.plot(range(4), vals, "o-", color=BLUE, lw=2.5, ms=11, zorder=3)
for i,v in enumerate(vals):
    ax.annotate(f"{v}", (i,v), textcoords="offset points", xytext=(0,14),
                ha="center", fontsize=15, fontweight="bold",
                color=GREEN if v==1034 else BLUE)
ax.axhline(980, ls="--", color=GREY, lw=1.6)
ax.text(3.32, 985, "AN-23-102\nscaled to 26.7 fb$^{-1}$", fontsize=10, color=GREY, va="bottom", ha="right")
ax.set_xticks(range(4)); ax.set_xticklabels(steps, fontsize=11)
ax.set_ylabel("expected UL (95% CL)", fontsize=12)
ax.set_ylim(900, 1450); ax.grid(alpha=.25, axis="y")
ax.set_title("Expected upper limit — 2022postEE, 26.7 fb$^{-1}$", fontsize=13, fontweight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/limit_cascade.png", dpi=160); plt.close(fig)

# ---------- 2. freeze scan NEW vs OLD ----------
labels = ["autoMCStats\n(all)", "autoMCStats\n(SR only)", "scalevar_muF", "CMS_ctag2d", "4FS/5FS", "rate_tt"]
old = [255, 225, 69, 35, np.nan, np.nan]
new = [1034-956, 1034-967, 1034-944, 1034-964, 1034-921, 1034-1011]
x = np.arange(len(labels)); w=0.38
fig, ax = plt.subplots(figsize=(10,4.8))
ax.bar(x-w/2, old, w, label="before W+jets fix (1160 card)", color=GREY)
ax.bar(x+w/2, new, w, label="current (1034 card)", color=BLUE)
for i,v in enumerate(new):
    ax.text(i+w/2, v+3, f"{v:.0f}", ha="center", fontsize=11, fontweight="bold", color=BLUE)
for i,v in enumerate(old):
    if not np.isnan(v): ax.text(i-w/2, v+3, f"{v:.0f}", ha="center", fontsize=10, color=GREY)
ax.set_ylabel("limit improvement when frozen", fontsize=12)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
ax.legend(fontsize=10); ax.grid(alpha=.25, axis="y")
ax.set_title("Nuisance impact — the ranking has changed", fontsize=13, fontweight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/freeze_scan_new.png", dpi=160); plt.close(fig)

# ---------- 3. V+jets n_eff ----------
fig, axes = plt.subplots(1,2, figsize=(10,4.2))
procs=["hplusc","higgsbkg","tt","st","diboson","vjets"]
neff=[314.9,17886.6,787376.7,73148.6,8845.1,279.8]
cols=[GREY]*5+[RED]
axes[0].barh(procs, neff, color=cols); axes[0].set_xscale("log")
axes[0].set_xlabel("$n_{eff}$ in SR (log)", fontsize=11)
axes[0].set_title("Before: V+jets starved", fontsize=12, fontweight="bold")
axes[0].grid(alpha=.25, axis="x")
b=axes[1].bar(["before","after"],[279.8,1169.6],color=[RED,GREEN],width=.55)
for r,v in zip(b,[279.8,1169.6]):
    axes[1].text(r.get_x()+r.get_width()/2, v+30, f"{v:.0f}", ha="center", fontsize=13, fontweight="bold")
axes[1].set_ylabel("V+jets $n_{eff}$ in SR", fontsize=11)
axes[1].set_title("After jet-binned samples: ×4.2", fontsize=12, fontweight="bold")
axes[1].grid(alpha=.25, axis="y"); axes[1].set_ylim(0,1400)
fig.tight_layout(); fig.savefig(f"{OUT}/vjets_neff.png", dpi=160); plt.close(fig)
print("wrote 3 plots")
