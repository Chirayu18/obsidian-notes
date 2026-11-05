"""Early PLuM gain vs Lund splittings per class -- the falsification test for
the "gain tracks Lund structure / attention share" hypothesis.

Numbers from 2026-09-11-plum-final-verdict.md:
  - gains: PLuM/baseline background rejection ratio @90% signal efficiency
  - splittings: full-tree C/A splittings per jet, measured on 100k real
    JetClass jets (JetClass_test_mod/file_0.lz4)
Both 40k and 100k are shown because the ranking is NOT stable between them.
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK="#1a1f27"; SUB="#4a5462"; GRID="#dfe3e8"
C40="#B00020"; C100="#1D4ED8"

# class: (splittings/jet, gain40k, err40k, gain100k, err100k)
D={
 "Wqq" :(21.6, 1.036,0.004, 1.001,0.004),
 "Zqq" :(23.4, 1.011,0.004, 1.002,0.004),
 "Hcc" :(26.8, 1.027,0.008, 1.027,0.009),
 "Hbb" :(28.9, 1.009,0.019, 1.037,0.022),
 "H4q" :(35.2, 1.037,0.007, 1.012,0.007),
 "Tbqq":(36.3, 1.095,0.016, 1.026,0.018),
 "Hgg" :(42.9, 1.009,0.003, 1.022,0.003),
}
names=list(D); x=np.array([D[k][0] for k in names])
g40=np.array([D[k][1] for k in names]); e40=np.array([D[k][2] for k in names])
g100=np.array([D[k][3] for k in names]); e100=np.array([D[k][4] for k in names])

def wpearson(x,y,e):
    """Pearson r, and the same weighted by 1/e^2 (the errors differ by 6x)."""
    r=np.corrcoef(x,y)[0,1]
    w=1/e**2; mx=np.average(x,weights=w); my=np.average(y,weights=w)
    cov=np.average((x-mx)*(y-my),weights=w)
    rw=cov/np.sqrt(np.average((x-mx)**2,weights=w)*np.average((y-my)**2,weights=w))
    return r,rw

def pval(r,n):
    """two-sided p for Pearson r via the t transform, no scipy."""
    from math import sqrt,erf
    if abs(r)>=1: return 0.
    t=r*sqrt((n-2)/(1-r*r))
    # normal approx is adequate at n=7 for a "not significant" statement
    z=abs(t)/sqrt(1+t*t/(2*(n-2)))*sqrt(n-2)/sqrt(n-2)
    return 2*(1-0.5*(1+erf(abs(t)/sqrt(2*(1+t*t/(n-2))))))

r40,rw40=wpearson(x,g40,e40); r100,rw100=wpearson(x,g100,e100)

fig,axes=plt.subplots(1,3,figsize=(15.2,4.9),
    gridspec_kw={"width_ratios":[1,1,0.82]})
axes[1].sharey(axes[0])
for ax,(g,e,r,rw,ttl,col) in zip(axes[:2],[
        (g40,e40,r40,rw40,"40k iterations",C40),
        (g100,e100,r100,rw100,"100k iterations",C100)]):
    ax.axhline(1.0,color=SUB,lw=1.1,ls="--",zorder=1)
    ax.errorbar(x,g,yerr=e,fmt="o",ms=8,color=col,mfc="white",mew=2.0,
                ecolor=col,elinewidth=1.6,capsize=4,zorder=3)
    # Wqq/Zqq sit ~2 splittings apart and collide at 100k -- push them apart
    off={"Wqq":(-13,9),"Zqq":(14,9)}
    for k,xi,gi,ei in zip(names,x,g,e):
        dx,dy=off.get(k,(0,0))
        ax.annotate(k,(xi,gi),textcoords="offset points",
                    xytext=(dx,dy+11+ei*260),
                    ha="center",fontsize=10.5,color=INK,weight="bold")
    # unweighted least-squares line, for the eye only
    b,a=np.polyfit(x,g,1)
    xs=np.linspace(x.min()-1.5,x.max()+1.5,50)
    ax.plot(xs,a+b*xs,"-",color=col,lw=1.3,alpha=.45,zorder=2)
    ax.set_title(ttl,fontsize=12.5,color=INK,weight="bold",pad=9)
    ax.set_xlabel("C/A splittings per jet  (full tree, measured)",fontsize=11,color=SUB)
    ax.text(.03,.955,f"Pearson $r$ = {r:+.2f}\n"
                     f"$1/\\sigma^2$-weighted $r$ = {rw:+.2f}",
            transform=ax.transAxes,va="top",ha="left",fontsize=10.5,color=INK,
            bbox=dict(fc="white",ec=GRID,lw=1,pad=6))
    ax.grid(True,color=GRID,lw=.8,zorder=0); ax.set_axisbelow(True)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)

axes[0].set_ylabel("PLuM / baseline rejection @90 % eff.",fontsize=11,color=SUB)
plt.setp(axes[1].get_yticklabels(),visible=False)

# --- panel 3: the ranking itself is not stable between the two checkpoints
ax=axes[2]
o40=list(np.argsort(-g40)); o100=list(np.argsort(-g100))
for rank40,i in enumerate(o40):
    rank100=o100.index(i)
    ax.plot([0,1],[rank40,rank100],"-",color="#c8ccd2",lw=1.6,zorder=1)
    ax.plot(0,rank40,"o",ms=7,color=C40,mfc="white",mew=1.8,zorder=3)
    ax.plot(1,rank100,"o",ms=7,color=C100,mfc="white",mew=1.8,zorder=3)
    ax.annotate(names[i],(0,rank40),textcoords="offset points",xytext=(-9,0),
                ha="right",va="center",fontsize=10.5,color=INK,weight="bold")
    ax.annotate(names[i],(1,rank100),textcoords="offset points",xytext=(9,0),
                ha="left",va="center",fontsize=10.5,color=INK,weight="bold")
ax.set_xlim(-.52,1.52); ax.set_ylim(len(names)+.35,-.75)
ax.set_xticks([0,1]); ax.set_xticklabels(["40k","100k"],fontsize=11.5,color=INK)
ax.set_yticks([]); ax.set_ylabel("rank by gain  (1st at top)",fontsize=11,color=SUB)
ax.set_title("the ranking reverses",fontsize=12.5,color=INK,weight="bold",pad=9)
ax.text(.5,.012,"Spearman between the two orderings = $-$0.32",
        transform=ax.transAxes,ha="center",fontsize=10.5,color=INK,
        bbox=dict(fc="white",ec=GRID,lw=1,pad=5))
for s_ in ("top","right","left","bottom"): ax.spines[s_].set_visible(False)
fig.suptitle("Early PLuM gain does not track the amount of Lund structure",
             fontsize=13.5,weight="bold",color=INK,y=.985)
fig.text(.5,.925,"if the gain came from redirecting attention to the Lund plane, "
                 "these should slope up — and the ranking should be stable",
         ha="center",fontsize=10.3,color=SUB)
fig.tight_layout(rect=(0,0,1,.905))
fig.savefig("gain_vs_splittings.png",dpi=200,facecolor="white")

print(f"40k : r={r40:+.3f}  weighted r={rw40:+.3f}  p~{pval(r40,7):.2f}")
print(f"100k: r={r100:+.3f}  weighted r={rw100:+.3f}  p~{pval(r100,7):.2f}")
print("\nrank by gain, 40k :", [names[i] for i in np.argsort(-g40)])
print("rank by gain, 100k:", [names[i] for i in np.argsort(-g100)])
print("rank by splittings:", [names[i] for i in np.argsort(-x)])
# Sitian's named set
S=["Hbb","Tbqq","H4q","Hcc"]
oth=[k for k in names if k not in S]
for lbl,g in (("40k",g40),("100k",g100)):
    ms=np.mean([g[names.index(k)] for k in S]); mo=np.mean([g[names.index(k)] for k in oth])
    print(f"{lbl}: Sitian's four mean {ms:.4f} vs others {mo:.4f}  diff {ms-mo:+.4f}")
