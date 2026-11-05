#!/usr/bin/env python3
"""Generate the analysis-overview deck plots from combine outputs.

  python3 make_deck_plots.py --outdir <dir> [--what all|cascade|freeze|neff|anbreak]

Inputs are hard-coded measured numbers (see --help for provenance) so the plots
are reproducible without re-running combine. Re-run scripts/combine/freeze_scan.sh
first if the card has changed, then update the dicts at the top of this file.
"""
import argparse, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, RED, GREY, GREEN = "#1f4e79", "#a01c1c", "#8c959d", "#2f6b3c"

# --- measured inputs -------------------------------------------------------
CASCADE   = [("early\ncard",1371),("negrw +\nsumw fix",1150),
             ("+ 2D\nc-tag SF",1164),("W+jets\njet-binned",1034)]
AN_SCALED = 980
FREEZE_OLD = {"autoMCStats\n(all)":255,"autoMCStats\n(SR only)":225,
              "scalevar_muF":69,"CMS_ctag2d":35}
FREEZE_NEW = {"autoMCStats\n(all)":78,"autoMCStats\n(SR only)":67,
              "scalevar_muF":90,"CMS_ctag2d":70,"4FS/5FS":113,"rate_tt":23}
NEFF_SR   = {"hplusc":314.9,"higgsbkg":17886.6,"tt":787376.7,
             "st":73148.6,"diboson":8845.1,"vjets":279.8}
VJETS     = (279.8, 1169.6)
# AN-comparable groups: label -> (ours %, AN Table 17 1POI %)
AN_BREAK  = {"Statistical":(37.7,73.8),"MC statistical":(17.6,5.4),
             "Signal theory\n(cH/bH)":(29.8,8.5),"Bkg-Higgs":(2.7,7.6),
             "Other background":(1.9,1.4),"tt norm.":(2.3,0.7),
             "Charm tagging":(12.4,1.1),"JES/JER":(6.3,1.1)}


def cascade(out):
    labs=[a for a,_ in CASCADE]; vals=[b for _,b in CASCADE]
    fig,ax=plt.subplots(figsize=(9,4.6))
    ax.plot(range(len(vals)),vals,"o-",color=BLUE,lw=2.5,ms=11,zorder=3)
    for i,v in enumerate(vals):
        ax.annotate(str(v),(i,v),textcoords="offset points",xytext=(0,14),
                    ha="center",fontsize=15,fontweight="bold",
                    color=GREEN if v==min(vals) else BLUE)
    ax.axhline(AN_SCALED,ls="--",color=GREY,lw=1.6)
    ax.text(len(vals)-0.7,AN_SCALED+5,"AN-23-102 scaled",fontsize=10,color=GREY)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs,fontsize=11)
    ax.set_ylabel("expected UL (95% CL)",fontsize=12)
    ax.set_ylim(900,1450); ax.grid(alpha=.25,axis="y")
    ax.set_title("Expected upper limit — 2022postEE, 26.7 fb$^{-1}$",fontsize=13,fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{out}/limit_cascade.png",dpi=160); plt.close(fig)


def freeze(out):
    labs=list(FREEZE_NEW); x=np.arange(len(labs)); w=.38
    old=[FREEZE_OLD.get(k,np.nan) for k in labs]; new=[FREEZE_NEW[k] for k in labs]
    fig,ax=plt.subplots(figsize=(10,4.8))
    ax.bar(x-w/2,old,w,label="before W+jets fix (1160 card)",color=GREY)
    ax.bar(x+w/2,new,w,label="current (1034 card)",color=BLUE)
    for i,v in enumerate(new):
        ax.text(i+w/2,v+3,f"{v:.0f}",ha="center",fontsize=11,fontweight="bold",color=BLUE)
    for i,v in enumerate(old):
        if not np.isnan(v): ax.text(i-w/2,v+3,f"{v:.0f}",ha="center",fontsize=10,color=GREY)
    ax.set_ylabel("limit improvement when frozen",fontsize=12)
    ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=10)
    ax.legend(fontsize=10); ax.grid(alpha=.25,axis="y")
    ax.set_title("Nuisance impact — the ranking has changed",fontsize=13,fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{out}/freeze_scan_new.png",dpi=160); plt.close(fig)


def neff(out):
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    ps=list(NEFF_SR); vs=[NEFF_SR[p] for p in ps]
    axes[0].barh(ps,vs,color=[GREY]*5+[RED]); axes[0].set_xscale("log")
    axes[0].set_xlabel("$n_{eff}$ in SR (log)",fontsize=11)
    axes[0].set_title("Before: V+jets starved",fontsize=12,fontweight="bold")
    axes[0].grid(alpha=.25,axis="x")
    b=axes[1].bar(["before","after"],list(VJETS),color=[RED,GREEN],width=.55)
    for r,v in zip(b,VJETS):
        axes[1].text(r.get_x()+r.get_width()/2,v+30,f"{v:.0f}",ha="center",
                     fontsize=13,fontweight="bold")
    axes[1].set_ylabel("V+jets $n_{eff}$ in SR",fontsize=11); axes[1].set_ylim(0,1400)
    axes[1].set_title(f"After: x{VJETS[1]/VJETS[0]:.1f}",fontsize=12,fontweight="bold")
    axes[1].grid(alpha=.25,axis="y")
    fig.tight_layout(); fig.savefig(f"{out}/vjets_neff.png",dpi=160); plt.close(fig)


def anbreak(out):
    ks=list(AN_BREAK); x=np.arange(len(ks)); w=.38
    ours=[AN_BREAK[k][0] for k in ks]; an=[AN_BREAK[k][1] for k in ks]
    fig,ax=plt.subplots(figsize=(11,4.9))
    ax.bar(x-w/2,ours,w,label="this analysis (26.7 fb$^{-1}$)",color=BLUE)
    ax.bar(x+w/2,an,w,label="AN-23-102 Table 17 (1POI, 138 fb$^{-1}$)",color=GREY)
    for i,k in enumerate(ks):
        ax.text(i-w/2,ours[i]+0.7,f"{ours[i]:.1f}",ha="center",fontsize=10,
                fontweight="bold",color=BLUE)
        ax.text(i+w/2,an[i]+0.7,f"{an[i]:.1f}",ha="center",fontsize=9,color="#5a6169")
    ax.set_xticks(x); ax.set_xticklabels(ks,fontsize=10)
    ax.set_ylabel(r"$|\Delta r|/r$  [%]",fontsize=12)
    ax.legend(fontsize=10); ax.grid(alpha=.25,axis="y")
    ax.set_title("Uncertainty breakdown vs the published analysis (AN metric)",
                 fontsize=13,fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{out}/breakdown_vs_AN_new.png",dpi=160); plt.close(fig)


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir",required=True)
    ap.add_argument("--what",default="all",
                    choices=["all","cascade","freeze","neff","anbreak"])
    a=ap.parse_args()
    fns={"cascade":cascade,"freeze":freeze,"neff":neff,"anbreak":anbreak}
    for k,f in fns.items():
        if a.what in ("all",k): f(a.outdir); print(f"wrote {k}")
