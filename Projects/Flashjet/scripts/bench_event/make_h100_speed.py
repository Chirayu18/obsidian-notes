"""Regenerate the ML4Jets speed figures from a chosen results dir.

Writes, into OUT:
  atlas_abs_timing.png      time per jet vs multiplicity (log y)
  atlas_speedup_algs.png    speedup vs multiplicity, all 3 algorithms, both samples
  atlas_R_independence.png  cost vs R, and vs algorithm
  regime_throughput.png     BOTH regimes on one axis (log-log), polished

Env:
  ATRES   jet-regime results dir   (default results_h100)
  EVRES   event-regime results dir (default bench_event/results)
  OUT     output dir
"""
import json, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ATRES = os.environ.get("ATRES", "/eos/home-c/cgupta/flashjet/bench_atlas/results_h100")
EVRES = os.environ.get("EVRES", "/eos/home-c/cgupta/flashjet/bench_event/results")
OUT   = os.environ.get("OUT",   "/eos/home-c/cgupta/flashjet/bench_atlas/fig_h100")
ALGS  = ["antikt", "kt", "cambridge"]
ALGL  = {"antikt": r"anti-$k_t$", "kt": r"$k_t$", "cambridge": "C/A"}
RADII = [0.4, 0.6, 0.8, 1.0, 1.2]
BINS  = ["lo", "mid", "hi", "vhi"]
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
                     "legend.fontsize": 11, "xtick.labelsize": 11, "ytick.labelsize": 11})


def load(pat, keyfn):
    d = {}
    for p in glob.glob(pat):
        j = json.load(open(p)); d[keyfn(j)] = j
    return d


def key(j): return (j["alg"], j["R"], j["bin"])


def gpu_of(d):
    g = {j.get("gpu") for j in d.values() if j.get("gpu")}
    return sorted(g)[0] if len(g) == 1 else " / ".join(sorted(g))


def main():
    os.makedirs(OUT, exist_ok=True)
    jf = {t: load(f"{ATRES}/at_atlastop-{t}_*_flashjet.json", key) for t in ["top", "qcd"]}
    js = {t: load(f"{ATRES}/at_atlastop-{t}_*_fastjet.json", key) for t in ["top", "qcd"]}
    ev = load(f"{EVRES}/ev_*_flashjet.json", key)
    evs = load(f"{EVRES}/ev_*_fastjet.json", key)
    gpu = gpu_of(jf["top"])
    print("jet GPU:", gpu, "| event GPU:", gpu_of(ev))

    # ---------- 1. absolute timing ----------
    fig, ax = plt.subplots(figsize=(8, 3.5))
    xs = [jf["top"][("antikt", 1.0, b)]["mean_const_per_jet"] for b in BINS]
    o = np.argsort(xs); xs = np.array(xs)[o]
    fjy = np.array([jf["top"][("antikt", 1.0, b)]["us_per_jet"] for b in BINS])[o]
    awk = np.array([(js["top"].get(("antikt", 1.0, b), {}).get("awkward") or {}).get("us_per_jet", np.nan) for b in BINS])[o]
    cla = np.array([(js["top"].get(("antikt", 1.0, b), {}).get("classic") or {}).get("us_per_jet", np.nan) for b in BINS])[o]
    ax.plot(xs, fjy, "o-", lw=2.2, ms=8, label="flashjet (GPU)")
    ax.plot(xs, awk, "s-", lw=2.2, ms=8, label="FastJet vectorised (CPU)")
    ax.plot(xs, cla, "^-", lw=2.2, ms=8, label="FastJet one jet at a time (CPU)")
    ax.set_yscale("log"); ax.set_xlabel("constituents per jet")
    ax.set_ylabel(r"time per jet [$\mu$s]")
    ax.set_title(f"ATLAS Top Tagging Open Data -- anti-$k_t$ $R=1.0$   [{gpu}]")
    ax.grid(alpha=.3, which="both"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT}/atlas_abs_timing.png", dpi=140); plt.close(fig)
    print("wrote atlas_abs_timing.png")

    # ---------- 2. speedup vs multiplicity, all algs ----------
    fig, axes = plt.subplots(1, 3, figsize=(15, 3.8), sharey=True)
    for ax, alg in zip(axes, ALGS):
        for t, mk in [("top", "o-"), ("qcd", "s--")]:
            x, y = [], []
            for b in BINS:
                k = (alg, 1.0, b)
                if k in jf[t] and k in js[t]:
                    base = (js[t][k].get("awkward") or {}).get("us_per_jet")
                    if base:
                        x.append(jf[t][k]["mean_const_per_jet"])
                        y.append(base / jf[t][k]["us_per_jet"])
            if x:
                o = np.argsort(x)
                ax.plot(np.array(x)[o], np.array(y)[o], mk, lw=2, ms=7,
                        label={"top": "boosted top", "qcd": "QCD"}[t])
        ax.set_title(ALGL[alg]); ax.set_xlabel("constituents per jet"); ax.grid(alpha=.3)
    axes[0].set_ylabel("speedup vs vectorised FastJet"); axes[0].legend()
    fig.suptitle(f"Speedup vs jet multiplicity   [{gpu}]")
    fig.tight_layout(); fig.savefig(f"{OUT}/atlas_speedup_algs.png", dpi=140); plt.close(fig)
    print("wrote atlas_speedup_algs.png")

    # ---------- 3. R independence ----------
    fig, ax = plt.subplots(figsize=(7, 4.6))
    for alg in ALGS:
        y = [jf["top"][(alg, R, "all")]["us_per_jet"] for R in RADII if (alg, R, "all") in jf["top"]]
        if len(y) == len(RADII):
            ax.plot(RADII, y, "o-", lw=2, ms=7, label=ALGL[alg])
    ax.set_xlabel("jet radius $R$"); ax.set_ylabel(r"time per jet [$\mu$s]")
    ax.set_ylim(bottom=0)
    ax.set_title(f"Cost is independent of $R$ and of the algorithm   [{gpu}]")
    ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT}/atlas_R_independence.png", dpi=140); plt.close(fig)
    print("wrote atlas_R_independence.png")

    # ---------- 4. BOTH regimes, one axis, log-log, polished ----------
    fig, ax = plt.subplots(figsize=(8, 5))
    jx = sorted((jf["top"][("antikt", 1.0, b)]["mean_const_per_jet"],
                 jf["top"][("antikt", 1.0, b)]["Mpart_per_s"]) for b in BINS)
    ex = sorted((ev[("antikt", 1.0, b)]["mean_const_per_event"],
                 ev[("antikt", 1.0, b)]["Mpart_per_s"]) for b in BINS if ("antikt", 1.0, b) in ev)
    jxx = [p[0] for p in jx]; jyy = [p[1] for p in jx]
    exx = [p[0] for p in ex]; eyy = [p[1] for p in ex]

    # shade the two regions so the regimes read at a glance
    mid = (max(jxx) + min(exx)) / 2
    ax.axvspan(min(jxx) * 0.7, mid, color="#1f77b4", alpha=0.05)
    ax.axvspan(mid, max(exx) * 1.4, color="#ff7f0e", alpha=0.05)

    ax.plot(jxx, jyy, "o-", lw=2.5, ms=9, color="#1f77b4",
            label="jet regime  (one jet per unit)")
    ax.plot(exx, eyy, "s-", lw=2.5, ms=9, color="#ff7f0e",
            label="event regime  (one event per unit)")
    ax.set_xscale("log"); ax.set_yscale("log")

    # annotate the peak -- the single number the slide is about
    pi = int(np.argmax(jyy))
    # peak label sits BELOW-RIGHT of the peak so it cannot collide with the
    # italic regime caption along the top of the axes
    ax.annotate(f"peak {jyy[pi]:.0f} Mpart/s",
                xy=(jxx[pi], jyy[pi]), xytext=(jxx[pi] * 1.12, jyy[pi] * 0.50),
                arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.5),
                color="#1f77b4", fontsize=11, ha="left", fontweight="bold")
    ax.annotate(f"{eyy[-1]:.0f} Mpart/s", xy=(exx[-1], eyy[-1]),
                xytext=(exx[-1] * 0.42, eyy[-1] * 0.52),
                arrowprops=dict(arrowstyle="->", color="#ff7f0e", lw=1.5),
                color="#ff7f0e", fontsize=11, fontweight="bold")
    top = max(jyy) * 2.4
    ax.text(mid * 0.30, top, "many small units\nfill the GPU",
            color="#1f77b4", fontsize=11, ha="center", va="top", style="italic")
    ax.text(mid * 2.6, top, "one big unit\nstarves it",
            color="#ff7f0e", fontsize=11, ha="center", va="top", style="italic")

    ax.set_xlabel("particles per unit, $N$")
    ax.set_ylabel("throughput [Mparticles/s]")
    ax.set_title(f"flashjet throughput by regime   [{gpu}]")
    ax.grid(alpha=.3, which="both")
    ax.legend(loc="lower left")
    ax.set_ylim(min(eyy) * 0.42, max(jyy) * 3.0)
    fig.tight_layout(); fig.savefig(f"{OUT}/regime_throughput.png", dpi=140); plt.close(fig)
    print("wrote regime_throughput.png")

    # ---------- numbers for the slide text ----------
    sp = []
    for t in ["top", "qcd"]:
        for k in set(jf[t]) & set(js[t]):
            base = (js[t][k].get("awkward") or {}).get("us_per_jet")
            if base: sp.append(base / jf[t][k]["us_per_jet"])
    sp.sort()
    print("\nJET speedup: %.0f-%.0fx median %.0fx over %d pts" %
          (sp[0], sp[-1], sp[len(sp)//2], len(sp)))
    us = [jf["top"][("antikt", 1.0, b)]["us_per_jet"] for b in BINS]
    print("JET us/jet: %.2f-%.2f" % (min(us), max(us)))
    aw = [(js["top"][("antikt",1.0,b)].get("awkward") or {}).get("us_per_jet") for b in BINS]
    cl = [(js["top"][("antikt",1.0,b)].get("classic") or {}).get("us_per_jet") for b in BINS]
    print("FJ vec us/jet: %.0f-%.0f | FJ classic: %.0f-%.0f" %
          (min(aw), max(aw), min(cl), max(cl)))
    rr = [jf["top"][("antikt", R, "all")]["us_per_jet"] for R in RADII]
    print("R spread (anti-kt, all): %.3f%%" % (100*(max(rr)-min(rr))/np.mean(rr)))


if __name__ == "__main__":
    main()
