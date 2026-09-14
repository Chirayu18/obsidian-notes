"""Combined jet+event regime timing figure with a speedup ratio panel.

Top:    time per unit vs N -- flashjet solid, FastJet vectorised dashed,
        FastJet one-at-a-time dotted; blue = jet regime, orange = event regime.
Bottom: speedup = FastJet vectorised / flashjet, WITHIN each regime.
        Dimensionless, so the two regimes are directly comparable here even
        though the absolute times above are per-jet vs per-event.
"""
import json, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ATRES = os.environ.get("ATRES", "/eos/home-c/cgupta/flashjet/bench_atlas/results_h100")
EVRES = os.environ.get("EVRES", "/eos/home-c/cgupta/flashjet/bench_event/results")
OUT   = os.environ.get("OUT",   "/eos/home-c/cgupta/flashjet/bench_atlas/fig_h100")
BINS  = ["lo", "mid", "hi", "vhi"]
JETC, EVC = "#1f77b4", "#d95f02"
plt.rcParams.update({"font.size": 13, "axes.labelsize": 13, "legend.fontsize": 11,
                     "xtick.labelsize": 12, "ytick.labelsize": 12})


def load(pat):
    d = {}
    for p in glob.glob(pat):
        j = json.load(open(p)); d[(j["alg"], j["R"], j["bin"])] = j
    return d


def series(f, s, nkey, tkey):
    """-> N, flashjet, fastjet-vec, fastjet-classic, speedup (sorted by N)"""
    rows = []
    for b in BINS:
        k = ("antikt", 1.0, b)
        if k in f and k in s:
            a, q = f[k], s[k]
            rows.append((a[nkey], a[tkey], q["awkward"][tkey], q["classic"][tkey]))
    rows.sort()
    N  = np.array([r[0] for r in rows]); fj = np.array([r[1] for r in rows])
    aw = np.array([r[2] for r in rows]); cl = np.array([r[3] for r in rows])
    return N, fj, aw, cl, aw / fj


def main():
    os.makedirs(OUT, exist_ok=True)
    jf = load(f"{ATRES}/at_atlastop-top_*_flashjet.json")
    js = load(f"{ATRES}/at_atlastop-top_*_fastjet.json")
    ef = load(f"{EVRES}/ev_*_flashjet.json")
    es = load(f"{EVRES}/ev_*_fastjet.json")
    gpu = sorted({j["gpu"] for j in jf.values()} | {j["gpu"] for j in ef.values()})
    gpu = gpu[0] if len(gpu) == 1 else " / ".join(gpu)

    jN, jfj, jaw, jcl, jsp = series(jf, js, "mean_const_per_jet", "us_per_jet")
    eN, efj, eaw, ecl, esp = series(ef, es, "mean_const_per_event", "us_per_event")

    fig, (ax, rx) = plt.subplots(
        2, 1, figsize=(7.4, 6.2), sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.15], "hspace": 0.07})

    # ---- top: absolute time per unit ----
    for N, fj, aw, cl, c in [(jN, jfj, jaw, jcl, JETC), (eN, efj, eaw, ecl, EVC)]:
        ax.plot(N, cl, ":",  color=c, lw=2.0, marker="^", ms=7, mfc="none")
        ax.plot(N, aw, "--", color=c, lw=2.0, marker="s", ms=7, mfc="none")
        ax.plot(N, fj, "-",  color=c, lw=2.6, marker="o", ms=8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylabel("time per unit [$\\mu$s]\n"
                  r"($\mu$s/jet or $\mu$s/event)", fontsize=11)
    ax.grid(alpha=.3, which="both")
    ax.set_title(f"flashjet vs FastJet, both regimes   [{gpu}]", fontsize=13)

    # two-part legend: colour = regime, linestyle = implementation
    from matplotlib.lines import Line2D
    reg = [Line2D([], [], color=JETC, lw=3, label="jet regime (unit = one jet)"),
           Line2D([], [], color=EVC,  lw=3, label="event regime (unit = one event)")]
    imp = [Line2D([], [], color="0.35", lw=2.4, ls="-",  marker="o", ms=7, label="flashjet (GPU)"),
           Line2D([], [], color="0.35", lw=2.0, ls="--", marker="s", ms=7, mfc="none", label="FastJet vectorised"),
           Line2D([], [], color="0.35", lw=2.0, ls=":",  marker="^", ms=7, mfc="none", label="FastJet one at a time")]
    l1 = ax.legend(handles=reg, loc="upper left", framealpha=.92)
    ax.add_artist(l1)
    ax.legend(handles=imp, loc="lower right", framealpha=.92)

    # ---- bottom: speedup within each regime ----
    rx.plot(jN, jsp, "-o", color=JETC, lw=2.6, ms=8)
    rx.plot(eN, esp, "-o", color=EVC,  lw=2.6, ms=8)
    rx.axhline(1, color="k", lw=.9, ls="--")
    rx.set_yticks([0, 50, 100])
    for N, sp, c in [(jN, jsp, JETC), (eN, esp, EVC)]:
        i = int(np.argmax(sp))
        rx.annotate(f"{sp[i]:.0f}$\\times$", xy=(N[i], sp[i]),
                    xytext=(0, 7), textcoords="offset points",
                    color=c, fontsize=11, fontweight="bold", ha="center")
    rx.set_xscale("log")
    rx.set_xlabel("particles per unit, $N$")
    rx.set_ylabel("speedup\n(FastJet vec. / flashjet)", fontsize=11)
    rx.grid(alpha=.3, which="both")
    rx.set_ylim(0, max(jsp.max(), esp.max()) * 1.28)

    fig.savefig(f"{OUT}/combined_regimes.png", dpi=140, bbox_inches="tight")
    print("wrote combined_regimes.png")
    print("jet   speedup %.0f-%.0fx | event speedup %.0f-%.0fx" %
          (jsp.min(), jsp.max(), esp.min(), esp.max()))


if __name__ == "__main__":
    main()
