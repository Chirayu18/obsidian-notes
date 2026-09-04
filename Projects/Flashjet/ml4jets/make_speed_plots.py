"""Extra ATLAS plots for the ML4Jets deck: absolute timing vs multiplicity,
algorithm comparison, and the R-independence panel."""
import json, glob, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D="/eos/home-c/cgupta/flashjet/bench_atlas/results_v100"
OUT="/eos/home-c/cgupta/flashjet/bench_atlas"
ALGL={"antikt":r"anti-$k_t$","kt":r"$k_t$","cambridge":"C/A"}
BINS=["lo","mid","hi","vhi"]

fj={};fs={}
for p in glob.glob(D+"/at_*_flashjet.json"):
    d=json.load(open(p)); fj[(d["tag"],d["alg"],d["R"],d["bin"])]=d
for p in glob.glob(D+"/at_*_fastjet.json"):
    d=json.load(open(p)); fs[(d["tag"],d["alg"],d["R"],d["bin"])]=d

# --- 1. absolute time per jet: flashjet vs both FastJet interfaces, vs multiplicity
fig,axes=plt.subplots(1,2,figsize=(12,4.6))
for ax,tag,ttl in zip(axes,["atlastop-top","atlastop-qcd"],["boosted top","QCD (light q/g)"]):
    xs=[];yf=[];ya=[];yc=[]
    for b in BINS:
        k=(tag,"antikt",1.0,b)
        if k in fj and k in fs:
            xs.append(fj[k]["mean_const_per_jet"]); yf.append(fj[k]["us_per_jet"])
            ya.append((fs[k].get("awkward") or {}).get("us_per_jet",np.nan))
            yc.append(fs[k]["classic"]["us_per_jet"])
    o=np.argsort(xs); xs=np.array(xs)[o]
    ax.semilogy(xs,np.array(yf)[o],"o-",lw=2,label="flashjet (GPU)",color="#1f77b4")
    ax.semilogy(xs,np.array(ya)[o],"s-",lw=2,label="FastJet vectorised (CPU)",color="#ff7f0e")
    ax.semilogy(xs,np.array(yc)[o],"^-",lw=2,label="FastJet per-jet (CPU)",color="#2ca02c")
    ax.set_xlabel("mean constituents per jet"); ax.set_title(ttl)
    ax.grid(alpha=.3,which="both"); ax.set_ylabel(r"time per jet [$\mu$s]")
axes[0].legend(fontsize=9)
fig.suptitle(r"ATLAS Top Tagging Open Data — anti-$k_t$ $R=1.0$")
fig.tight_layout(); fig.savefig(f"{OUT}/atlas_abs_timing.png",dpi=150)

# --- 2. R-independence: flashjet us/jet vs R, all algorithms, bin=all
fig,ax=plt.subplots(figsize=(7,4.6))
for tag,ls in [("atlastop-top","-"),("atlastop-qcd","--")]:
    for alg,c in zip(["antikt","kt","cambridge"],["#1f77b4","#d62728","#2ca02c"]):
        R=[];y=[]
        for r in [0.4,0.6,0.8,1.0,1.2]:
            k=(tag,alg,r,"all")
            if k in fj: R.append(r); y.append(fj[k]["us_per_jet"])
        if R: ax.plot(R,y,ls,marker="o",color=c,
                      label=f"{ALGL[alg]} ({'top' if 'top' in tag else 'qcd'})")
ax.set_xlabel("jet radius $R$"); ax.set_ylabel(r"flashjet time per jet [$\mu$s]")
ax.set_ylim(0,2.0); ax.grid(alpha=.3)
ax.set_title("Cost is independent of $R$ and of algorithm")
ax.legend(fontsize=8,ncol=2)
fig.tight_layout(); fig.savefig(f"{OUT}/atlas_R_independence.png",dpi=150)

# --- 3. speedup vs multiplicity, all algorithms, both samples
fig,axes=plt.subplots(1,2,figsize=(12,4.6),sharey=True)
for ax,tag,ttl in zip(axes,["atlastop-top","atlastop-qcd"],["boosted top","QCD (light q/g)"]):
    for alg,c in zip(["antikt","kt","cambridge"],["#1f77b4","#d62728","#2ca02c"]):
        xs=[];ys=[]
        for b in BINS:
            k=(tag,alg,1.0,b)
            if k in fj and k in fs:
                aw=(fs[k].get("awkward") or {}).get("us_per_jet")
                if aw: xs.append(fj[k]["mean_const_per_jet"]); ys.append(aw/fj[k]["us_per_jet"])
        if xs:
            o=np.argsort(xs)
            ax.plot(np.array(xs)[o],np.array(ys)[o],"o-",lw=2,color=c,label=ALGL[alg])
    ax.set_xlabel("mean constituents per jet"); ax.grid(alpha=.3); ax.set_title(ttl)
axes[0].set_ylabel("speedup vs vectorised FastJet"); axes[0].legend(fontsize=9)
fig.suptitle(r"Speedup vs multiplicity — $R=1.0$ (all points 100% $n_{jets}$ agreement)")
fig.tight_layout(); fig.savefig(f"{OUT}/atlas_speedup_algs.png",dpi=150)
print("wrote atlas_abs_timing.png atlas_R_independence.png atlas_speedup_algs.png")
