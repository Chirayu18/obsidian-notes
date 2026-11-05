#!/usr/bin/env python3
"""Plot an Asimov likelihood scan from a combine MultiDimFit output.

  python3 nll_scan.py --input higgsCombine_scan.MultiDimFit.mH120.root \
                      --output nll_scan.png

Produce the input with:
  combine -M MultiDimFit <ws.root> -t -1 --expectSignal 1 --algo grid \
          --points 60 --rMin 0 --rMax 3000 --mass 120 -n _scan
"""
import argparse, uproot, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ymax", type=float, default=8.0)
    a = ap.parse_args()

    t = uproot.open(a.input)["limit"]
    r = t["r"].array(library="np"); n = t["deltaNLL"].array(library="np")
    m = (n >= 0) & np.isfinite(n) & (r > 0)
    r, n = r[m], n[m]
    o = np.argsort(r); r, n = r[o], n[o]
    q = 2*n

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.plot(r, q, color="#1f4e79", lw=2.4)
    for lv, lab, c in [(1, "68%", "#8c959d"), (3.84, "95%", "#a01c1c")]:
        ax.axhline(lv, ls="--", color=c, lw=1.5)
        ax.text(r.max()*0.98, lv+0.12, lab, color=c, fontsize=10, ha="right")
    ax.set_xlabel("r  (signal strength)", fontsize=12)
    ax.set_ylabel(r"$-2\Delta\ln L$", fontsize=12)
    ax.set_ylim(0, a.ymax); ax.set_xlim(0, r.max()); ax.grid(alpha=.25)
    ax.set_title("Asimov likelihood scan", fontsize=13, fontweight="bold")
    fig.tight_layout(); fig.savefig(a.output, dpi=160)
    print("wrote", a.output)
