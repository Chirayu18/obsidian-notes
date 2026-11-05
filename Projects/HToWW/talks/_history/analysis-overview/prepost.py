#!/usr/bin/env python3
"""Prefit vs postfit stacked templates from a combine FitDiagnostics output.

  python3 prepost.py --input fitDiagnostics.root --output prepost.png [--channel SR_hplusc]
"""
import argparse, uproot, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PR=["tt","st","vjets","diboson","higgsbkg"]
COL={"tt":"#4c78a8","st":"#f58518","vjets":"#54a24b","diboson":"#b279a2","higgsbkg":"#e45756"}

def stack(f, d, ch, ax, title):
    base=f"{d}/{ch}"
    bot=None; edges=None
    for p in PR:
        k=f"{base}/{p}"
        if k not in f: continue
        h=f[k]; v=h.values()
        if edges is None:
            edges=h.axis().edges(); x=(edges[:-1]+edges[1:])/2; bot=np.zeros_like(v)
        ax.bar(x, v, width=np.diff(edges), bottom=bot, label=p, color=COL[p],
               edgecolor="white", linewidth=.3)
        bot=bot+v
    k=f"{base}/total"
    if k in f:
        tot=f[k]; ax.step(edges, np.append(tot.values(),tot.values()[-1]),
                          where="post", color="k", lw=1.2)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("MVA discriminant bin", fontsize=10)
    ax.grid(alpha=.2, axis="y")
    return bot

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True); ap.add_argument("--output",required=True)
    ap.add_argument("--channel",default="SR_hplusc")
    a=ap.parse_args()
    f=uproot.open(a.input)
    fig,axes=plt.subplots(1,2,figsize=(11,4.4),sharey=True)
    stack(f,"shapes_prefit",a.channel,axes[0],f"Prefit — {a.channel}")
    stack(f,"shapes_fit_s",a.channel,axes[1],f"Postfit (S+B) — {a.channel}")
    axes[0].set_ylabel("events",fontsize=11)
    axes[1].legend(fontsize=9,ncol=2)
    fig.tight_layout(); fig.savefig(a.output,dpi=160)
    print("wrote",a.output)
