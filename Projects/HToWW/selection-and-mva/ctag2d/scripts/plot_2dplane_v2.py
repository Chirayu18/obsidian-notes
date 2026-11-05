"""2D-CTAG plane with official SFbc-2D frozen bins + zoom insets for the thin bands."""
import numpy as np, matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import pyarrow.parquet as pq

XE=[0.0,0.250,0.452,0.808,1.000]
YE=[0.0,0.006,0.017,0.055,0.761,0.944,0.985,0.995,1.0]
CATS=["L0","C0","C1","C2","C3","C4","B0","B1","B2","B3","B4"]
ID={c:i for i,c in enumerate(CATS)}
BOX={ "L0":(XE[0],XE[1],0,1), "C0":(XE[1],XE[2],0,1), "C1":(XE[2],XE[3],0,1),
      "C4":(XE[3],1,YE[0],YE[1]), "C3":(XE[3],1,YE[1],YE[2]), "C2":(XE[3],1,YE[2],YE[3]),
      "B0":(XE[3],1,YE[3],YE[4]), "B1":(XE[3],1,YE[4],YE[5]), "B2":(XE[3],1,YE[5],YE[6]),
      "B3":(XE[3],1,YE[6],YE[7]), "B4":(XE[3],1,YE[7],1.0) }

def cat_of(cvl,cvb):
    den=cvl+cvb*(1-cvl); x=np.where(den!=0,cvl/den,np.nan); y=1-cvb
    c=np.full(x.shape,-1,np.int8); g=np.isfinite(x)&np.isfinite(y)
    L=g&(x<XE[3]); R=g&(x>=XE[3])
    c[L&(x<XE[1])]=ID["L0"]; c[L&(x>=XE[1])&(x<XE[2])]=ID["C0"]; c[L&(x>=XE[2])]=ID["C1"]
    c[R&(y<YE[1])]=ID["C4"]; c[R&(y>=YE[1])&(y<YE[2])]=ID["C3"]; c[R&(y>=YE[2])&(y<YE[3])]=ID["C2"]
    c[R&(y>=YE[3])&(y<YE[4])]=ID["B0"]; c[R&(y>=YE[4])&(y<YE[5])]=ID["B1"]
    c[R&(y>=YE[5])&(y<YE[6])]=ID["B2"]; c[R&(y>=YE[6])&(y<YE[7])]=ID["B3"]; c[R&(y>=YE[7])]=ID["B4"]
    return c,x,y

base="/eos/home-c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
CVL=[];CVB=[];HF=[]
for nm in ["tt.parquet","H+c.parquet","DY+Jets.parquet","Single Top.parquet","WW.parquet"]:
    f=os.path.join(base,nm)
    if not os.path.exists(f): continue
    t=pq.read_table(f,columns=["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","cjet_cand_flavour"]).to_pandas().dropna()
    if len(t)>400000: t=t.sample(400000,random_state=1)
    CVL.append(t.cjet_cand_cvsl_pnet.values);CVB.append(t.cjet_cand_cvsb_pnet.values);HF.append(t.cjet_cand_flavour.values)
cvl=np.concatenate(CVL);cvb=np.concatenate(CVB);hf=np.concatenate(HF).astype(int)
cat,x,y=cat_of(cvl,cvb)

def comp(nm):
    m=cat==ID[nm]; n=int(m.sum())
    if n==0: return None
    return dict(n=n,b=100*np.mean(hf[m]==5),c=100*np.mean(hf[m]==4),l=100*np.mean(hf[m]==0))

LC=(1,.66,.1); CC=(.15,.55,1); BC=(.85,.12,.12)
COL={"L0":LC,"C0":CC,"C1":CC,"C2":CC,"C3":CC,"C4":CC,"B0":BC,"B1":BC,"B2":BC,"B3":BC,"B4":BC}

fig=plt.figure(figsize=(17,8.5))
gs=fig.add_gridspec(2,3,width_ratios=[2.05,1,1],hspace=.32,wspace=.24)
axm=fig.add_subplot(gs[:,0]); axc=fig.add_subplot(gs[0,1]); axb=fig.add_subplot(gs[1,1]); axt=fig.add_subplot(gs[:,2]); axt.axis("off")

def draw(ax,xlim,ylim,label_all=True,fs=12,ann=True):
    h=ax.hist2d(x,y,bins=[np.linspace(0,1,300),np.linspace(0,1,300)],
                cmap="Greys",norm=mcolors.LogNorm(),alpha=.6)
    for nm,(x0,x1,y0,y1) in BOX.items():
        if x1<xlim[0] or x0>xlim[1] or y1<ylim[0] or y0>ylim[1]: continue
        ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor=COL[nm],edgecolor="k",lw=1.5,alpha=.3,zorder=3))
        cx=min(max((x0+x1)/2,xlim[0]),xlim[1]); cy=min(max((y0+y1)/2,ylim[0]),ylim[1])
        st=comp(nm)
        ax.text(cx,cy,nm,ha="center",va="center",fontweight="bold",fontsize=fs,zorder=6)
        if ann and st:
            ax.text(cx,cy,"\n\nb%.0f c%.0f l%.0f%%\nN=%s"%(st["b"],st["c"],st["l"],f"{st['n']:,}"),
                    ha="center",va="center",fontsize=7.5,zorder=6)
        elif ann and not st:
            ax.text(cx,cy,"\n\n(empty)",ha="center",va="center",fontsize=7,zorder=6,style="italic")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    return h

h=draw(axm,(0,1),(0,1),fs=14)
plt.colorbar(h[3],ax=axm,label="jets / bin",pad=.015)
axm.set_xlabel(r"HFvLF $=P_b+P_c=\mathrm{CvL}/[\mathrm{CvL}+\mathrm{CvB}(1-\mathrm{CvL})]$",fontsize=12)
axm.set_ylabel(r"BvC $=1-\mathrm{CvB}$",fontsize=12)
axm.set_title("Full plane — 11 frozen bins",fontsize=13)
for e in XE[1:-1]: axm.axvline(e,color="k",lw=1,ls="--",alpha=.55,zorder=4)

draw(axc,(XE[3],1.0),(0,0.075),fs=11)
axc.set_title("Zoom: charm band C4/C3/C2  (HFvLF>0.808, BvC<0.055)",fontsize=10)
axc.set_xlabel("HFvLF",fontsize=9); axc.set_ylabel("BvC",fontsize=9)

draw(axb,(XE[3],1.0),(0.74,1.0),fs=11)
axb.set_title("Zoom: b band B1–B4  (BvC>0.761)",fontsize=10)
axb.set_xlabel("HFvLF",fontsize=9); axb.set_ylabel("BvC",fontsize=9)

rows=[("cat","N","%b","%c","%l")]
for nm in CATS:
    st=comp(nm)
    rows.append((nm,"—","—","—","—") if st is None else
                (nm,f"{st['n']:,}",f"{st['b']:.1f}",f"{st['c']:.1f}",f"{st['l']:.1f}"))
tb=axt.table(cellText=rows[1:],colLabels=rows[0],loc="center",cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1,1.45)
for j in range(5): tb[0,j].set_facecolor("#dddddd"); tb[0,j].set_text_props(fontweight="bold")
for i,nm in enumerate(CATS,start=1):
    tb[i,0].set_facecolor((*COL[nm][:3],.30)); tb[i,0].set_text_props(fontweight="bold")
axt.set_title("Flavour composition per bin\n(2022postEE MC: tt+H+c+DY+ST+WW, candidate c-jet)",fontsize=11,pad=16)

fig.suptitle("2D-CTAG plane — official SFbc-2D frozen bins, applied to PNet axes  (H$\\to$WW)",fontsize=15,y=.985)
for ext in ["png","pdf"]:
    o=f"/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.{ext}"
    plt.savefig(o,dpi=140,bbox_inches="tight"); print("saved",o)
print("total jets:",len(cat))
