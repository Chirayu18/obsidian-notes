"""Charts for the framework-plan deck. Numbers from 2026-10-08-framework-optimization-plan.md (§1.2, §4.2, §4.3)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
NAVY, GOLD, RED, GREY, GREEN = "#1f4e79", "#b8862b", "#a01c1c", "#9aa3ad", "#2f6b3c"

# 1. processor CPU per 20k-event chunk
st = [("parquet writer (dump_parquet ×15)", 14.8, RED), ("object selection ×15", 11.3, NAVY),
      ("event sel. + axis eval + cutflow ×15", 7.6, NAVY), ("weights ×15", 2.8, NAVY),
      ("object corrections (once)", 2.1, GREY)]
fig, ax = plt.subplots(figsize=(11, 4.6))
y = np.arange(len(st))[::-1]
ax.barh(y, [s[1] for s in st], color=[s[2] for s in st], height=0.6)
for yi, s in zip(y, st):
    ax.text(s[1] + 0.3, yi, f"{s[1]:.1f} s  ({100*s[1]/38.9:.0f}%)", va="center", fontsize=14)
ax.set_yticks(y); ax.set_yticklabels([s[0] for s in st])
ax.set_xlim(0, 19); ax.set_xlabel("seconds per 20k-event TTto2L2Nu chunk (total 38.9 s) [M]")
fig.tight_layout(); fig.savefig("img/cpu_breakdown.png", dpi=140)

# 2. ttH lepton-MVA timing, 20k events
rows = [("Thomas: get_scores, cache MISS", 31.20, 31.67, RED), ("Thomas: _calculate_scores (compute only)", 18.39, 20.06, RED),
        ("Thomas: get_scores, cache HIT", 12.78, 11.97, GOLD), ("vectorised numpy tree walk", 0.565, 0.587, NAVY),
        ("vectorised numba tree walk", 0.409, 0.442, NAVY), ("vectorised + ONNX Runtime (BRANCH_LT)", 0.216, 0.227, GREEN)]
fig, ax = plt.subplots(figsize=(11.5, 5))
y = np.arange(len(rows))[::-1]; h = 0.36
ax.barh(y + h/2, [r[1] for r in rows], h, color=[r[3] for r in rows], label="muons (24,484)")
ax.barh(y - h/2, [r[2] for r in rows], h, color=[r[3] for r in rows], alpha=0.55, label="electrons (25,713)")
for yi, r in zip(y, rows):
    ax.text(r[1] * 1.12, yi + h/2, f"{r[1]:.2f} s" if r[1] >= 1 else f"{r[1]:.3f} s", va="center", fontsize=12)
    ax.text(r[2] * 1.12, yi - h/2, f"{r[2]:.2f} s" if r[2] >= 1 else f"{r[2]:.3f} s", va="center", fontsize=12, color="#555")
ax.set_xscale("log"); ax.set_xlim(0.1, 120)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
ax.set_xlabel("seconds for 20,000 tt events, 1 thread (log scale)")
ax.legend(loc="lower right", fontsize=12, frameon=False)
fig.tight_layout(); fig.savefig("img/tthmva_timing.png", dpi=140)

# 3. production-scale extrapolation
rows = [("cache miss\n(first production)", 3750, RED), ("cache hit,\nper pass", 1480, GOLD),
        ("vectorised + ONNX,\nper pass", 26, GREEN)]
fig, ax = plt.subplots(figsize=(8.5, 4.6))
x = np.arange(len(rows))
ax.bar(x, [r[1] for r in rows], color=[r[2] for r in rows], width=0.55)
for xi, r in zip(x, rows): ax.text(xi, r[1] * 1.15, f"{r[1]:,} core-h", ha="center", fontsize=14, weight="bold")
ax.axhline(1570, color="k", ls="--", lw=1.2); ax.text(2.45, 1700, "today's whole production\n≈1,570 core-h", ha="right", fontsize=11)
ax.set_yscale("log"); ax.set_ylim(10, 15000); ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows])
ax.set_ylabel("core-hours, 4 eras (upper estimate)")
fig.tight_layout(); fig.savefig("img/tthmva_production.png", dpi=140)
print("ok")
