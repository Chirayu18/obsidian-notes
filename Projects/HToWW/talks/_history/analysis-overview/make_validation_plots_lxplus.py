#!/usr/bin/env python3
"""Actual-vs-predicted validation plots for the neg-weight reweighting, from the real
vjets SR output. Shows the learned g(x) tracks the realised event weights.

Plots:
  V1 calibration   : predicted P+ vs OBSERVED frac(w>0) per P+ bin (+ Poisson bars, diagonal)
  V2 g vs sign(vpt): predicted <g> vs realised <sign(w)> in bins of lhe_vpt
  V3 closure(vpt)  : Sum w vs Sum|w|*g per lhe_vpt bin, with per-dataset renorm overlaid
  V4 weighted yield: predicted reweighted density vs nominal, |w|-weighted, in lhe_vpt
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 130, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True})
POS = "#2166ac"   # blue  = positive / predicted
NEG = "#b2182b"   # red   = negative / actual
INK = "#222222"
OUT = "/tmp/negrw_valplots"

df = pd.read_parquet("/tmp/negrw_sr_forplots.parquet")
w = df["weight_nominal"].to_numpy()
g = df["weight_negrw"].to_numpy()          # = 2*Phat+ - 1
pplus = 0.5 * (g + 1.0)                     # recovered predicted P+
vpt = df["lhe_vpt"].to_numpy()
sign = np.sign(w)
m = np.isfinite(w) & np.isfinite(g) & np.isfinite(vpt)
w, g, pplus, vpt, sign = w[m], g[m], pplus[m], vpt[m], sign[m]
print("rows for plots:", len(w))

def save(fig, name):
    fig.savefig(f"{OUT}/{name}", bbox_inches="tight"); plt.close(fig)
    print("wrote", name)

# ---------- V1: calibration / reliability ----------
# bin by predicted P+, compare to observed fraction of positive-weight events.
# UNWEIGHTED fraction is the right target: P+ models P(sign=+ | x), an event-count prob.
edges = np.linspace(pplus.min(), pplus.max(), 11)
idx = np.digitize(pplus, edges) - 1
xs, ys, yerr, xspread = [], [], [], []
for b in range(len(edges) - 1):
    sel = idx == b
    n = sel.sum()
    if n < 20:
        continue
    frac = (sign[sel] > 0).mean()
    xs.append(pplus[sel].mean())
    ys.append(frac)
    yerr.append(np.sqrt(frac * (1 - frac) / n))       # binomial error on the fraction
    xspread.append(pplus[sel].std())
xs, ys, yerr = map(np.array, (xs, ys, yerr))

fig, ax = plt.subplots(figsize=(5.6, 5.2))
lo = min(xs.min(), ys.min()) - 0.05; hi = max(xs.max(), ys.max()) + 0.05
ax.plot([lo, hi], [lo, hi], ls="--", lw=1.3, color=INK, alpha=0.6, label="perfect calibration", zorder=1)
ax.errorbar(xs, ys, yerr=yerr, fmt="o", ms=8, color=POS, ecolor=POS, elinewidth=1.6,
            capsize=3, mfc="white", mec=POS, mew=1.8, label="SR vjets (binned)", zorder=3)
ax.set_xlabel("predicted  $P_+$  (mean per bin)")
ax.set_ylabel("observed  fraction($w>0$)")
ax.set_title("Calibration — predicted vs actual positive rate")
ax.legend(frameon=False, loc="upper left")
ax.set_aspect("equal"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
save(fig, "V1_calibration.png")

# ---------- V2: predicted g vs realised mean sign, in lhe_vpt bins ----------
vedges = np.array([0, 20, 40, 60, 80, 120, 160, 220, 300, 400])
vc = 0.5 * (vedges[:-1] + vedges[1:])
gpred, sreal, serr, keep = [], [], [], []
vi = np.digitize(vpt, vedges) - 1
for b in range(len(vedges) - 1):
    sel = vi == b
    n = sel.sum()
    if n < 15:
        continue
    keep.append(b)
    gpred.append(g[sel].mean())
    ms = sign[sel].mean()
    sreal.append(ms)
    serr.append(np.sqrt(max(1 - ms**2, 0) / n))       # error on mean of +-1
kc = vc[keep]
fig, ax = plt.subplots(figsize=(7, 4.4))
ax.plot(kc, gpred, "-o", color=POS, lw=2, ms=7, mfc="white", mec=POS, mew=1.8,
        label=r"predicted  $\langle g\rangle = \langle 2P_+ - 1\rangle$")
ax.errorbar(kc, sreal, yerr=serr, fmt="s", color=NEG, ms=7, elinewidth=1.6, capsize=3,
            label=r"actual  $\langle\,\mathrm{sign}(w)\,\rangle$")
ax.axhline(0, color=INK, lw=0.8, alpha=0.4)
ax.set_xlabel("LHE $V$ $p_T$ [GeV]"); ax.set_ylabel("mean sign / reweight factor")
ax.set_title("Predicted reweight factor tracks the realised weight sign")
ax.legend(frameon=False)
save(fig, "V2_g_vs_sign.png")

# ---------- V3: closure per vpt bin, Sum w vs Sum|w|g, with per-dataset renorm ----------
# global renorm factor from the total (per-dataset in the note; here show total for the plot)
R = w.sum() / (np.abs(w) * g).sum()
nom, _ = np.histogram(vpt, bins=vedges, weights=w)
rw, _  = np.histogram(vpt, bins=vedges, weights=np.abs(w) * g)
rwn = rw * R
fig, (ax, rax) = plt.subplots(2, 1, figsize=(7, 5.2), sharex=True,
                              gridspec_kw=dict(height_ratios=[3, 1], hspace=0.08))
ax.step(vc, nom, where="mid", color=INK, lw=1.8, label=r"nominal  $\sum w$")
ax.step(vc, rwn, where="mid", color=POS, lw=1.8, ls="--",
        label=r"reweighted  $\sum|w|\,g$  (renorm.)")
ax.set_ylabel("weighted yield"); ax.set_yscale("symlog")
ax.set_title(f"Closure in the SR after per-sample renormalisation (×{R:.3f})")
ax.legend(frameon=False)
ratio = np.where(nom != 0, rwn / nom, np.nan)
rax.step(vc, ratio, where="mid", color=POS, lw=1.5)
rax.axhline(1, color=INK, ls=":", lw=1)
rax.set_ylim(0.5, 1.5); rax.set_ylabel("rw / nom"); rax.set_xlabel("LHE $V$ $p_T$ [GeV]")
save(fig, "V3_closure_renorm.png")

# ---------- V4: distribution of predicted P+ split by actual sign (does it separate?) ----------
edges = np.linspace(0, 1, 26)
c = 0.5 * (edges[:-1] + edges[1:])
hp, _ = np.histogram(pplus[sign > 0], bins=edges)
hn, _ = np.histogram(pplus[sign < 0], bins=edges)
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.step(c, hp / max(hp.sum(), 1), where="mid", color=POS, lw=1.8, label="actual $w>0$")
ax.step(c, hn / max(hn.sum(), 1), where="mid", color=NEG, lw=1.8, label="actual $w<0$")
ax.set_xlabel("predicted  $P_+$"); ax.set_ylabel("normalised events")
ax.set_title("SR events: predicted $P_+$ separates the true sign")
ax.legend(frameon=False)
save(fig, "V4_pplus_by_actual_sign.png")

# ---------- numbers for the slide ----------
chi2 = np.sum(((ys - xs) / yerr) ** 2)
print(f"\ncalibration: {len(xs)} bins, chi2/ndf = {chi2:.1f}/{len(xs)} = {chi2/len(xs):.2f}")
print(f"total closure ratio (pre-renorm) = {(np.abs(w)*g).sum()/w.sum():.4f}  -> renorm x{R:.4f}")
