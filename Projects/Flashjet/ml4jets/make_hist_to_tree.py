"""hist_* arrays -> the binary tree they encode, on ONE real ATLAS jet.

Makes the point of the `It returns the tree` slide concrete: the three history
rows in the table ARE the drawing on the right. Small jet (8 constituents) so
every merge step is visible and the arrays fit on a slide.
"""
import numpy as np, h5py
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC="/eos/opendata/atlas/datascience/ATL-PHYS-PUB-2022-039/test.h5"
OUT="/eos/home-c/cgupta/flashjet/bench_atlas/fig_tree"
TREE="#9aa3b0"; INK="#4a5462"; ACC="#B00020"; HI="#1D4ED8"

def ca_cluster(P,R=1.0):
    pt=list(P[:,0]); y=list(P[:,1]); ph=list(P[:,2])
    kids={i:None for i in range(len(P))}; alive=list(range(len(P))); nxt=len(P)
    order=[]
    while len(alive)>1:
        best=None
        for ii,i in enumerate(alive):
            for j in alive[ii+1:]:
                dphi=abs(ph[i]-ph[j]); dphi=min(dphi,2*np.pi-dphi)
                d=((y[i]-y[j])**2+dphi**2)/R**2
                if best is None or d<best[0]: best=(d,i,j)
        d,i,j=best; tot=pt[i]+pt[j]
        pt.append(tot); y.append((pt[i]*y[i]+pt[j]*y[j])/tot); ph.append((pt[i]*ph[i]+pt[j]*ph[j])/tot)
        kids[nxt]=(i,j); order.append((i,j,nxt,np.sqrt(d)*R))
        alive=[a for a in alive if a not in (i,j)]+[nxt]; nxt+=1
    return alive[0],kids,order

f=h5py.File(SRC,"r")
N=4000
pt=f["fjet_clus_pt"][:N]/1000.; eta=f["fjet_clus_eta"][:N]; phi=f["fjet_clus_phi"][:N]
lab=f["labels"][:N]

# smallest top jet with exactly 8 constituents -> 7 merges, a readable tree
pick=None
for i in range(N):
    n=int((pt[i]>0).sum())
    if n!=8 or lab[i]!=1: continue
    m=pt[i]>0
    P=np.stack([pt[i][m],eta[i][m],phi[i][m]],1)
    P=P[np.argsort(-P[:,0])]
    pick=(i,P); break
i,P=pick
n0=len(P)
root,kids,order=ca_cluster(P)
print("jet",i,"n",n0,"merges",len(order))

fig,(axL,axR)=plt.subplots(1,2,figsize=(13.0,4.0),gridspec_kw={"width_ratios":[1.02,1.0]})

# ---- left: the three history arrays, as the slide's table names them
axL.axis("off")
p1=[o[0] for o in order]; p2=[o[1] for o in order]; ch=[o[2] for o in order]
dd=[o[3] for o in order]
rows=[("hist_p1",p1,"%d"),("hist_p2",p2,"%d"),("hist_child",ch,"%d"),("hist_d",dd,"%.3f")]
axL.text(.0,.95,"what the kernel writes out  (step $\\to$)",transform=axL.transAxes,
         fontsize=11,color=INK,va="top")
y0=.80
for name,vals,fmt in rows:
    axL.text(.0,y0,name,transform=axL.transAxes,fontsize=11.5,family="monospace",
             color="#1a1f27",va="center",weight="bold")
    for k,v in enumerate(vals):
        axL.text(.30+k*.098,y0,fmt%v,transform=axL.transAxes,fontsize=11.5,
                 family="monospace",color=ACC if name=="hist_child" else "#1a1f27",
                 va="center",ha="center")
    y0-=.135
axL.text(.0,y0-.02,"step",transform=axL.transAxes,fontsize=9.5,color="#79828f",va="center")
for k in range(len(order)):
    axL.text(.30+k*.098,y0-.02,str(k),transform=axL.transAxes,fontsize=9.5,
             color="#79828f",va="center",ha="center")
axL.text(.0,.12,"each column is one merge: particles $p_1,p_2$ join into $child$,\n"
                 "at distance $d$.  Indices $\\geq$ %d are merged pseudo-particles."%n0,
         transform=axL.transAxes,fontsize=10,color=INK,va="top")

# ---- right: the tree those columns encode
depth={}
def sd(nd,d):
    depth[nd]=d
    if kids[nd] is not None:
        a,b=kids[nd]; sd(a,d+1); sd(b,d+1)
sd(root,0)
def leaves(nd):
    if kids[nd] is None: return [nd]
    a,b=kids[nd]; return leaves(a)+leaves(b)
lv=leaves(root); pos={l:k for k,l in enumerate(lv)}
def xof(nd):
    if nd in pos: return pos[nd]
    a,b=kids[nd]; return .5*(xof(a)+xof(b))
X={nd:xof(nd) for nd in depth}
for nd in depth:
    if kids[nd] is None: continue
    a,b=kids[nd]
    for c in (a,b):
        axR.plot([X[nd],X[c]],[-depth[nd],-depth[c]],"-",color=TREE,lw=1.3,zorder=1)
for nd in depth:
    leaf = kids[nd] is None
    axR.plot(X[nd],-depth[nd],"o",ms=15 if not leaf else 11,
             mfc="white",mec=ACC if not leaf else HI,mew=1.8,zorder=3)
    axR.text(X[nd],-depth[nd],str(nd),ha="center",va="center",fontsize=8.5,
             family="monospace",color=ACC if not leaf else HI,zorder=4)
axR.set_xlim(-.7,n0-.3); axR.set_ylim(-max(depth.values())-.6,.7)
axR.set_xticks([]); axR.set_yticks([])
for s_ in axR.spines.values(): s_.set_visible(False)
axR.set_title("the binary tree those rows encode",fontsize=11.5,color=INK,pad=8)
axR.text(.5,-.07,"blue = the %d input particles     red = merged pseudo-particles"%n0,
         transform=axR.transAxes,ha="center",va="top",fontsize=10,color=INK)

fig.tight_layout(rect=(0,.02,1,1))
fig.savefig(f"{OUT}/hist_to_tree.png",dpi=200,facecolor="white")
print("wrote",OUT+"/hist_to_tree.png")
