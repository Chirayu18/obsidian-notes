import uproot, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
f=uproot.open("/tmp/deepscan/higgsCombine_scan_cur.MultiDimFit.mH120.root")["limit"]
r=f["r"].array(library="np"); n=f["deltaNLL"].array(library="np")
m=(n>=0)&np.isfinite(n)&(r>0); r,n=r[m],n[m]
o=np.argsort(r); r,n=r[o],n[o]
q=2*n
fig,ax=plt.subplots(figsize=(7.6,4.6))
ax.plot(r,q,color="#1f4e79",lw=2.4)
for lv,lab,c in [(1,"68%","#8c959d"),(3.84,"95%","#a01c1c")]:
    ax.axhline(lv,ls="--",color=c,lw=1.5)
    ax.text(r.max()*0.98,lv+0.12,lab,color=c,fontsize=10,ha="right")
ax.set_xlabel("r  (signal strength)",fontsize=12)
ax.set_ylabel(r"$-2\Delta\ln L$",fontsize=12)
ax.set_ylim(0,8); ax.set_xlim(0,r.max())
ax.grid(alpha=.25)
ax.set_title("Asimov likelihood scan — current card",fontsize=13,fontweight="bold")
fig.tight_layout()
fig.savefig("/home/cgupta/obsidian-notes/Projects/HToWW/deck-overview-2026-08-17/img/nll_scan.png",dpi=160)
print("wrote nll_scan.png; r range", r.min(), r.max())
