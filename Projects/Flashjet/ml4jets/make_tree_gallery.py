"""C/A merge-tree gallery from REAL ATLAS Top Tagging Open Data jets.

Picks representative jets by label (boosted top vs light quark/gluon), clusters
them with C/A, runs soft drop, and draws in the artifact style.
"""
import numpy as np, h5py
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SRC="/tmp/cgupta_toptag_test.h5"
OUT="/eos/home-c/cgupta/flashjet/bench_atlas"
TREE="#9aa3b0"; KEPT="#3f7d54"; DROP="#b04434"; STOP="#b8791c"; INK="#4a5462"

def ca_cluster(P,R=1.0):
    pt=list(P[:,0]); y=list(P[:,1]); ph=list(P[:,2])
    kids={i:None for i in range(len(P))}; alive=list(range(len(P))); nxt=len(P)
    while len(alive)>1:
        best=None
        for ii,i in enumerate(alive):
            for j in alive[ii+1:]:
                dphi=np.abs(ph[i]-ph[j]); dphi=min(dphi,2*np.pi-dphi)
                d=((y[i]-y[j])**2+dphi**2)/R**2
                if best is None or d<best[0]: best=(d,i,j)
        d,i,j=best; tot=pt[i]+pt[j]
        pt.append(tot); y.append((pt[i]*y[i]+pt[j]*y[j])/tot); ph.append((pt[i]*ph[i]+pt[j]*ph[j])/tot)
        kids[nxt]=(i,j,np.sqrt(d)*R); alive=[a for a in alive if a not in (i,j)]+[nxt]; nxt+=1
    return alive[0],kids,np.array(pt),np.array(y),np.array(ph)

def softdrop(root,kids,pt,zcut=.1,beta=0.,R=1.0):
    spine=[root]; dropped=[]; nd=root; n=0; stop=None
    while kids[nd] is not None:
        i,j,dR=kids[nd]
        hard,soft=(i,j) if pt[i]>=pt[j] else (j,i)
        z=pt[soft]/(pt[i]+pt[j])
        if z>zcut*(dR/R)**beta: stop=nd; break
        dropped.append(soft); n+=1; nd=hard; spine.append(nd)
    return spine,dropped,stop,n

def leaves(nd,kids,n0):
    if nd<n0: return [nd]
    i,j,_=kids[nd]; return leaves(i,kids,n0)+leaves(j,kids,n0)

def mass(idx,P):
    s=P[idx]
    px=(s[:,0]*np.cos(s[:,2])).sum(); py=(s[:,0]*np.sin(s[:,2])).sum()
    pz=(s[:,0]*np.sinh(s[:,1])).sum(); E=(s[:,0]*np.cosh(s[:,1])).sum()
    return np.sqrt(max(E*E-px*px-py*py-pz*pz,0.))

f=h5py.File(SRC,"r")
N=6000
pt=f["fjet_clus_pt"][:N]/1000.; eta=f["fjet_clus_eta"][:N]; phi=f["fjet_clus_phi"][:N]
lab=f["labels"][:N]; jm=f["fjet_m"][:N]/1000.

def getjet(i,cap=26):
    m=pt[i]>0
    P=np.stack([pt[i][m],eta[i][m],phi[i][m]],1)
    P=P[np.argsort(-P[:,0])][:cap]                  # hardest cap constituents
    return P

# choose: a QCD jet with many drops, a top jet whose SD mass lands near mt, and one near mW
cands={"qcd":[], "top":[]}
for i in range(N):
    n=(pt[i]>0).sum()
    if not (14<=n<=40): continue
    P=getjet(i)
    if len(P)<10: continue
    try: root,kids,ptv,y,ph=ca_cluster(P)
    except Exception: continue
    sp,dr,stop,nd=softdrop(root,kids,ptv)
    mu=mass(list(range(len(P))),P); ms_=mass(leaves(stop,kids,len(P)),P) if stop is not None else 0.
    rec=(i,P,root,kids,sp,dr,stop,nd,mu,ms_)
    cands["top" if lab[i]==1 else "qcd"].append(rec)
    if len(cands["qcd"])>90 and len(cands["top"])>90: break

qcd=sorted(cands["qcd"],key=lambda r:-r[7])[0]                       # most drops
top=sorted(cands["top"],key=lambda r:abs(r[9]-173.))[0]              # SD mass near m_t
wln=sorted(cands["top"],key=lambda r:abs(r[9]-80.4))[0]              # SD mass near m_W
print("qcd ndrop",qcd[7],"m",round(qcd[8]),round(qcd[9]))
print("top ndrop",top[7],"m",round(top[8]),round(top[9]))
print("W   ndrop",wln[7],"m",round(wln[8]),round(wln[9]))

def draw(ax,rec,title,caption):
    i,P,root,kids,spine,dropped,stop,ndrop,mu,ms_=rec
    n0=len(P); depth={}
    def sd(nd,d):
        depth[nd]=d
        if kids[nd] is not None:
            a,b,_=kids[nd]; sd(a,d+1); sd(b,d+1)
    sd(root,0); maxd=max(depth.values())
    order=leaves(root,kids,n0); pos={lf:k for k,lf in enumerate(order)}
    def xof(nd):
        if nd in pos: return pos[nd]
        a,b,_=kids[nd]; return .5*(xof(a)+xof(b))
    X={nd:xof(nd) for nd in depth}
    for nd in depth:
        if kids[nd] is None: continue
        a,b,_=kids[nd]
        for c in (a,b):
            ax.plot([X[nd],X[c]],[-depth[nd],-depth[c]],"-",color=TREE,lw=1.0,alpha=.75,zorder=1)
    for nd in depth:
        if kids[nd] is None:
            ax.plot(X[nd],-depth[nd],"o",ms=3.4,mfc=TREE,mec="none",zorder=2)
    for nd in spine:
        ax.plot(X[nd],-depth[nd],"o",ms=7.0,mfc="none",mec=KEPT,mew=1.9,zorder=4)
    for nd in dropped:
        ax.plot(X[nd],-depth[nd],"o",ms=5.8,mfc="none",mec=DROP,mew=1.7,zorder=4)
    if stop is not None:
        ax.plot(X[stop],-depth[stop],"o",ms=11,mfc="none",mec=STOP,mew=2.6,zorder=5)
    ax.set_title(title,fontsize=11,weight="bold",color="#1a1f27",pad=7)
    ax.text(.5,-.09,caption,transform=ax.transAxes,ha="center",va="top",fontsize=8.8,color=INK)
    ax.text(.5,-.225,f"$n_{{drop}}$ = {ndrop}      $m$: {mu:.0f} $\\to$ {ms_:.0f} GeV",
            transform=ax.transAxes,ha="center",va="top",fontsize=9.2,family="monospace",color="#1a1f27")
    ax.set_xlim(-.9,len(order)-.1); ax.set_ylim(-maxd-.6,.6)
    ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_visible(False)

fig,axes=plt.subplots(1,3,figsize=(13.2,4.6))
draw(axes[0],qcd,"Light quark / gluon jet","a long spine: soft prong after soft prong\nis stripped, and the mass collapses")
draw(axes[1],wln,"Boosted top — a clean two-prong core","the very first split is already balanced,\nso nothing is groomed away")
draw(axes[2],top,"Boosted top — the full $t\\to bW$ system","also stops at once, but on a wider split,\nso the whole decay is kept")
h=[Line2D([],[],marker="o",ls="",mfc="none",mec=KEPT,mew=1.9,ms=8,label="soft-drop spine"),
   Line2D([],[],marker="o",ls="",mfc="none",mec=DROP,mew=1.7,ms=7,label="dropped prong"),
   Line2D([],[],marker="o",ls="",mfc="none",mec=STOP,mew=2.4,ms=10,label="grooming stops here"),
   Line2D([],[],marker="o",ls="",mfc=TREE,mec="none",ms=5,label="constituent")]
fig.legend(handles=h,loc="lower center",ncol=4,fontsize=9.2,frameon=False,bbox_to_anchor=(.5,.005))
fig.suptitle("C/A merge trees of real jets — root at top, constituents at the bottom",
             fontsize=12.5,weight="bold",color="#1a1f27")
fig.text(.5,.905,"ATLAS Top Tagging Open Data  ·  vertical = declustering depth  ·  horizontal = angular ordering",
         ha="center",fontsize=8.8,color="#79828f")
fig.tight_layout(rect=(0,.075,1,.885))
fig.savefig(f"{OUT}/tree_gallery.png",dpi=170,facecolor="white")
print("wrote",OUT+"/tree_gallery.png")
