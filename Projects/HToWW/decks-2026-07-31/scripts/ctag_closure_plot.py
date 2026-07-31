"""C3: the with/without-SF closure, measured 2026-07-31 from freshly rebuilt inputs."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="/eos/user/c/cgupta/HToWW/plots/ctag"

stages=["stat-only","freeze\nautoMCStats","full\n(all syst)"]
nosf=[668,941,1172]
sf  =[676,976,1192]
x=np.arange(3)

fig,(ax,axr)=plt.subplots(1,2,figsize=(10.4,4.2),
                          gridspec_kw={"width_ratios":[1.55,1]})
ax.plot(x,nosf,"o-",ms=10,lw=2.4,color="#1a7f37",label="no c-tag SF")
ax.plot(x,sf,  "s-",ms=10,lw=2.4,color="#b2182b",label="+ $CMS\\_ctag2d\\_2022$")
for xi,(a,b) in enumerate(zip(nosf,sf)):
    ax.annotate(f"{a}",(xi,a),textcoords="offset points",xytext=(0,-20),
                ha="center",color="#1a7f37",fontsize=11,fontweight="bold")
    ax.annotate(f"{b}",(xi,b),textcoords="offset points",xytext=(0,13),
                ha="center",color="#b2182b",fontsize=11,fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(stages,fontsize=10.5)
ax.set_ylabel("expected $r_{95}$"); ax.set_ylim(600,1300)
ax.grid(alpha=.3); ax.legend(fontsize=10.5,loc="upper left")
ax.set_title("2D c-tag SF closure  (2022postEE, blind Asimov, sumw_records norm.)",fontsize=11)

d=[b-a for a,b in zip(nosf,sf)]
pct=[100*(b-a)/a for a,b in zip(nosf,sf)]
bars=axr.bar(x,d,0.55,color=["#9ecae1","#6baed6","#b2182b"],edgecolor="k",lw=.6)
for xi,(dd,pp) in enumerate(zip(d,pct)):
    axr.annotate(f"+{dd}\n(+{pp:.1f}%)",(xi,dd),textcoords="offset points",
                 xytext=(0,4),ha="center",fontsize=10)
axr.set_xticks(x); axr.set_xticklabels(stages,fontsize=10.5)
axr.set_ylabel(r"$\Delta r_{95}$  (SF $-$ no SF)"); axr.set_ylim(0,50)
axr.grid(alpha=.3,axis="y"); axr.set_title("cost of the SF")
fig.tight_layout(); fig.savefig(f"{OUT}/C3_sf_closure.png",dpi=150); plt.close(fig)
print("wrote C3_sf_closure.png")
for s,a,b,dd,pp in zip(["stat-only","freeze-aMCS","full"],nosf,sf,d,pct):
    print(f"  {s:12s} {a:5d} -> {b:5d}   +{dd:3d}  (+{pp:.1f}%)")
