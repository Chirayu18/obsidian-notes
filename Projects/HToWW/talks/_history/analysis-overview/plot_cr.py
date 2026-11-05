"""Kinematic + SR-overlap plots for the two control regions.

Top CR      : mTl2 > 30 & mTll <= 60   (inverts the SR mTll cut)
High-mll CR : mll > 72                  (inverts the SR mll<=72 cut)

Class choice is driven by measured population (cr_populations.txt):
  Top CR      -- argmax=hplusc has only 66 events (0.01%), because the CR is
                 defined inside the model's own signal-dead zone. So the split is
                 the four populated background classes; signal is reported but NOT
                 drawn as a shape (no stats).
  High-mll CR -- hplusc has 21,607, enough to draw. Split is signal / higgs / top
                 (tt+st) / diboson / vjets.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO=Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0,str(REPO)); sys.path.insert(0,str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR="2022postEE"; WF="hww_combine_fixed"
MVA=Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR/"mva"
OUT=Path(sys.argv[1] if len(sys.argv)>1 else "."); OUT.mkdir(parents=True,exist_ok=True)
CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
samples=sorted({s for v in c2s.values() for s in v})

need=SC+["mtll","mtl2","dilepton_mass"]
ch=[]
for s in samples:
    p=MVA/f"{s}.parquet"
    if not p.exists(): continue
    av=set(pq.read_schema(p).names)
    if not set(SC).issubset(av): continue
    ch.append(pd.read_parquet(p,columns=[c for c in need if c in av]))
df=pd.concat(ch,ignore_index=True)
sc=df[SC].to_numpy(float); am=np.argmax(sc,axis=1)
mtll=df.mtll.to_numpy(float); mtl2=df.mtl2.to_numpy(float); mll=df.dilepton_mass.to_numpy(float)
p_sig=sc[:,0]
print(f"pooled {len(df):,}")

TOPCR=(mtl2>30)&(mtll<=60)
HIMLL=(mll>72)
MIN_N=50

VARS={"dilepton_mass":(r"$m_{\ell\ell}$ [GeV]","mll"),
      "mtll":(r"$m_T^{\ell\ell}$ [GeV]","mTll"),
      "mtl2":(r"$m_T^{\ell_2}$ [GeV]","mTl2")}
ARR={"dilepton_mass":mll,"mtll":mtll,"mtl2":mtl2}

def grouping(region):
    """(display name, argmax indices, colour) tuples per region."""
    if region=="topcr":
        # no signal: 66 events. top split into tt / st since both are populated.
        return [("tt (argmax)",[2],"#8c564b"),
                ("single-t (argmax)",[3],"#e377c2"),
                ("higgs bkg (argmax)",[1],"#1f77b4"),
                ("diboson (argmax)",[4],"#2ca02c"),
                ("V+jets (argmax)",[5],"#ff7f0e")]
    return [("signal (argmax)",[0],"#d62728"),
            ("higgs bkg (argmax)",[1],"#1f77b4"),
            ("top: tt+st (argmax)",[2,3],"#8c564b"),
            ("diboson (argmax)",[4],"#2ca02c"),
            ("V+jets (argmax)",[5],"#ff7f0e")]

REGIONS=[("topcr", TOPCR, "Top CR  ($m_T^{\\ell_2}>30$, $m_T^{\\ell\\ell}\\leq 60$)"),
         ("himll", HIMLL, "High-$m_{\\ell\\ell}$ CR  ($m_{\\ell\\ell}>72$)")]

# ---------- per-region class-split kinematics ----------
for tag,mask,title in REGIONS:
    groups=grouping(tag)
    ranges={"dilepton_mass":(0,200) if tag=="himll" else (0,140),
            "mtll":(0,300),"mtl2":(0,200)}
    for v,(lab,key) in VARS.items():
        lo,hi=ranges[v]; bins=np.linspace(lo,hi,71)
        ctr=0.5*(bins[1:]+bins[:-1])
        fig,axes=plt.subplots(1,2,figsize=(13.5,5.0))
        for name,idxs,col in groups:
            m=mask & np.isin(am,idxs)
            n=int(m.sum())
            if n<MIN_N: continue
            h,_=np.histogram(ARR[v][m],bins=bins)
            axes[0].step(ctr,h,where="mid",color=col,lw=1.8,label=f"{name}  (N={n:,})")
            s=h.sum()
            axes[1].step(ctr,h/s if s else h,where="mid",color=col,lw=1.8,label=name)
        axes[0].set_yscale("log")
        axes[0].set_ylabel("raw events / bin (unweighted)")
        axes[0].set_title("raw counts (log)")
        axes[1].set_ylabel("fraction of class"); axes[1].set_title("shape within each argmax class")
        for a in axes:
            a.set_xlabel(lab); a.grid(alpha=0.25,ls=":"); a.legend(fontsize=7.5,frameon=False)
            a.set_xlim(lo,hi)
        ntot=int(mask.sum())
        fig.suptitle(f"{lab} by v11 argmax class - {title}\n{YEAR} MC pooled, raw/unweighted, N={ntot:,}",
                     fontsize=10.5)
        fig.tight_layout()
        f=OUT/f"cr_{tag}_{key}.png"; fig.savefig(f,dpi=140,bbox_inches="tight"); plt.close(fig)
        print("wrote",f)

# ---------- 2D planes, per region, with SR cut lines ----------
for tag,mask,title in REGIONS:
    is_sig=(am==0).astype(float)
    xb=np.linspace(0,300,61); yb=np.linspace(0,160,41)
    n_all,_,_=np.histogram2d(mtll[mask],mtl2[mask],bins=[xb,yb])
    n_sig,_,_=np.histogram2d(mtll[mask],mtl2[mask],bins=[xb,yb],weights=is_sig[mask])
    with np.errstate(invalid="ignore",divide="ignore"):
        frac=np.where(n_all>=MIN_N,n_sig/n_all,np.nan)
    fig,ax=plt.subplots(figsize=(8.4,6.0))
    vmax=np.nanmax(100*frac) if np.isfinite(frac).any() else 1.0
    pcm=ax.pcolormesh(xb,yb,100*frac.T,cmap="inferno",vmin=0,vmax=max(vmax,1e-3))
    cb=fig.colorbar(pcm,ax=ax); cb.set_label("% of events with argmax = signal")
    ax.axvline(60,color="#00e5ff",lw=2.0,ls="--",label=r"SR cut $m_T^{\ell\ell}>60$")
    ax.axhline(30,color="#7CFC00",lw=2.0,ls="--",label=r"SR cut $m_T^{\ell_2}>30$")
    ax.set_xlabel(r"$m_T^{\ell\ell}$ [GeV]"); ax.set_ylabel(r"$m_T^{\ell_2}$ [GeV]")
    ax.set_title(f"argmax=signal density - {title}\nN={int(mask.sum()):,}, max={vmax:.2f}%",fontsize=10)
    ax.legend(loc="upper right",fontsize=8.5,framealpha=0.85)
    fig.tight_layout()
    f=OUT/f"cr_{tag}_2d_plane.png"; fig.savefig(f,dpi=145,bbox_inches="tight"); plt.close(fig)
    print("wrote",f, f" max argmax-sig frac = {vmax:.3f}%")

# ---------- summary ----------
print("\n=== argmax=signal rate per region ===")
for tag,mask,title in REGIONS:
    n=int(mask.sum()); ns=int((am[mask]==0).sum())
    print(f"{tag:<6s} N={n:>9,d}  argmax=signal={ns:>8,d}  ({100*ns/max(n,1):.4f}%)  "
          f"max P(hplusc)={p_sig[mask].max():.4f}")
print("done")
