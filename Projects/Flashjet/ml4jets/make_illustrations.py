import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

rng = np.random.default_rng(11)
OUT = "/home/cgupta/obsidian-notes/Projects/Flashjet/ml4jets/fig"

def make_jet(n_soft=26, pt=500., m=80.4):
    z = rng.uniform(0.32, 0.45)
    dR = m/(np.sqrt(z*(1-z))*pt); ang = rng.uniform(0, 2*np.pi)
    prongs=[(pt*(1-z), .5*dR*np.cos(ang), .5*dR*np.sin(ang)),
            (pt*z, -.5*dR*np.cos(ang), -.5*dR*np.sin(ang))]
    parts=[]
    for p,y,phi in prongs:
        for f in rng.dirichlet(np.ones(4)*3):
            parts.append((p*f, y+rng.normal(0,.045), phi+rng.normal(0,.045)))
    for _ in range(n_soft):
        parts.append((abs(rng.exponential(6.)), rng.normal(0,.34), rng.normal(0,.34)))
    return np.array(parts)

# ============ FIG 1: clustering steps (well-separated pair) ============
P = make_jet()
pt,y,ph = P[:,0],P[:,1],P[:,2]; n=len(P)
# pick the smallest-d_ij pair that is also visually separated
best=None
for i in range(n):
    for j in range(i+1,n):
        d2=(y[i]-y[j])**2+(ph[i]-ph[j])**2
        if np.sqrt(d2) < 0.10: continue          # need visible separation
        d=min(pt[i]**-2,pt[j]**-2)*d2/0.8**2
        if best is None or d<best[0]: best=(d,i,j)
_,i,j = best

fig,axes = plt.subplots(1,3,figsize=(13.5,4.5))
S = lambda a: np.clip(a*2.2, 8, 420)
for ax in axes:
    ax.set_xlim(-0.85,0.85); ax.set_ylim(-0.65,0.65)
    ax.set_aspect("equal"); ax.grid(alpha=.25); ax.set_xlabel("rapidity $y$")
axes[0].set_ylabel(r"azimuth $\phi$")

axes[0].scatter(y,ph,s=S(pt),alpha=.8,c="#1f77b4",edgecolors="k",linewidths=.4,zorder=3)
axes[0].set_title("1. constituents",fontsize=12,weight="bold")
axes[0].text(.03,.97,"marker area $\\propto p_T$",transform=axes[0].transAxes,
             fontsize=9,va="top",bbox=dict(fc="w",ec="0.7",alpha=.95))

axes[1].scatter(y,ph,s=S(pt),alpha=.25,c="#999999",edgecolors="none",zorder=2)
axes[1].plot(y[[i,j]],ph[[i,j]],"-",color="#d62728",lw=2.4,zorder=3)
axes[1].scatter(y[[i,j]],ph[[i,j]],s=S(pt[[i,j]]),c="#d62728",
                edgecolors="k",linewidths=.7,zorder=4)
axes[1].set_title("2. find the smallest $d_{ij}$",fontsize=12,weight="bold")
axes[1].text(.03,.97,
    r"$d_{ij}=\min(p_{Ti}^{2p},p_{Tj}^{2p})\,\Delta R_{ij}^2/R^2$"+"\n"+
    r"$d_{iB}=p_{Ti}^{2p}$"+"\n"+
    r"$p=-1$ anti-$k_t$ $\cdot$ $+1$ $k_t$ $\cdot$ $0$ C/A",
    transform=axes[1].transAxes,fontsize=9,va="top",
    bbox=dict(fc="w",ec="0.7",alpha=.95))

keep=[k for k in range(n) if k not in (i,j)]
axes[2].scatter(y[keep],ph[keep],s=S(pt[keep]),alpha=.45,c="#999999",
                edgecolors="none",zorder=2)
mp=pt[i]+pt[j]; my=(pt[i]*y[i]+pt[j]*y[j])/mp; mph=(pt[i]*ph[i]+pt[j]*ph[j])/mp
axes[2].scatter([my],[mph],s=S(np.array([mp]))[0],c="#2ca02c",marker="D",
                edgecolors="k",linewidths=.8,zorder=4)
axes[2].set_title("3. merge, record, repeat",fontsize=12,weight="bold")
axes[2].text(.03,.97,"the pair becomes its sum;\nthe step is written to\n"
             r"$\mathtt{hist\_p1},\ \mathtt{hist\_p2},\ \mathtt{hist\_d}$",
             transform=axes[2].transAxes,fontsize=9,va="top",
             bbox=dict(fc="#eaffea",ec="#2ca02c",alpha=.95))
fig.suptitle("Sequential recombination — and what flashjet keeps from it",
             fontsize=13,weight="bold")
fig.tight_layout(rect=(0,0,1,.94))
fig.savefig(f"{OUT}/clustering_steps.png",dpi=160); print("clustering_steps ok")

# ============ FIG 2: soft drop ============
def jm(s):
    px=(s[:,0]*np.cos(s[:,2])).sum(); py=(s[:,0]*np.sin(s[:,2])).sum()
    pz=(s[:,0]*np.sinh(s[:,1])).sum(); E=(s[:,0]*np.cosh(s[:,1])).sum()
    return np.sqrt(max(E**2-px**2-py**2-pz**2,0.))
mu,mg=[],[]
for _ in range(4000):
    J=make_jet(); mu.append(jm(J)); mg.append(jm(J[np.argsort(-J[:,0])][:8]))
mu,mg=np.array(mu),np.array(mg)

fig,axes=plt.subplots(1,2,figsize=(12.5,4.5))
ax=axes[0]; b=np.linspace(0,260,60)
ax.hist(mu,bins=b,histtype="step",lw=2.2,color="#777777",density=True,label="ungroomed")
ax.hist(mg,bins=b,histtype="step",lw=2.2,color="#d62728",density=True,label="soft-dropped")
ax.axvline(80.4,color="k",ls="--",lw=1.4)
ax.annotate(r"$m_W$",xy=(80.4,ax.get_ylim()[1]*.80),xytext=(96,ax.get_ylim()[1]*.86),
            fontsize=12,arrowprops=dict(arrowstyle="->",lw=1.2))
ax.set_xlabel("jet mass [GeV]"); ax.set_ylabel("normalized"); ax.set_xlim(0,260)
ax.set_title("F2: grooming removes soft wide-angle radiation",fontsize=11.5,weight="bold")
ax.legend(fontsize=9,loc="upper right"); ax.grid(alpha=.25)

ax=axes[1]; ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.set_aspect("equal")
ax.text(5,9.5,"the soft-drop walk on the C/A tree",ha="center",fontsize=12,weight="bold")
nodes={"j":(5,8.2),"a":(3.2,6.4),"b":(7.4,6.4),"c":(1.8,4.6),"d":(4.4,4.6),
       "e":(3.4,2.8),"f":(5.6,2.8)}
for u,v in [("j","a"),("j","b"),("a","c"),("a","d"),("d","e"),("d","f")]:
    ax.plot([nodes[u][0],nodes[v][0]],[nodes[u][1],nodes[v][1]],"-",color="0.55",lw=1.7,zorder=1)
drop={"b","c"}
for k,(x,yy) in nodes.items():
    ax.add_patch(Circle((x,yy),.36,fc=("#d62728" if k in drop else "#2ca02c"),
                        ec="k",lw=.9,zorder=3))
ax.annotate("",xy=nodes["d"],xytext=nodes["j"],
            arrowprops=dict(arrowstyle="-|>",lw=2.4,color="#1f77b4",shrinkA=13,shrinkB=13))
ax.text(5.7,7.0,"follow the\nharder prong",fontsize=9.5,color="#1f77b4")
ax.plot([],[],"o",color="#2ca02c",ms=8,label="kept")
ax.plot([],[],"o",color="#d62728",ms=8,label=r"dropped (fails $z>z_{cut}$)")
ax.legend(loc="upper left",bbox_to_anchor=(-0.04,0.22),fontsize=9,frameon=True)
ax.text(5.0,0.55,r"stop when $z=\dfrac{\min(p_{T1},p_{T2})}{p_{T1}+p_{T2}}"
                 r">z_{cut}\left(\dfrac{\Delta R}{R}\right)^{\beta}$",
        fontsize=10.5,ha="center",bbox=dict(fc="w",ec="0.7"))
fig.tight_layout()
fig.savefig(f"{OUT}/softdrop_walk.png",dpi=160); print("softdrop_walk ok")
