"""Show that the v11 argmax=signal region coincides with the SR kinematic cuts.

Three panels:
  (1) 2D (mTll, mTl2) plane coloured by the FRACTION of events with argmax=signal,
      with the SR cut lines mTll=60 / mTl2=30 drawn on top.
  (2) P(argmax=signal) vs mTll, with the mTll=60 cut marked, plus the mean P(hplusc)
      score on a twin axis -- the smooth score ceiling behind the hard argmax edge.
  (3) the same vs mTl2 with the mTl2=30 cut marked -- the SOFT edge, showing the
      asymmetry between the two cuts.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR="2022postEE"; WF="hww_combine_fixed"
MVA = Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR/"mva"
OUT = Path(sys.argv[1] if len(sys.argv)>1 else ".")
OUT.mkdir(parents=True, exist_ok=True)

CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
samples=sorted({s for v in c2s.values() for s in v})

need=SC+["mtll","mtl2","dilepton_mass"]
chunks=[]
for s in samples:
    p=MVA/f"{s}.parquet"
    if not p.exists(): continue
    av=set(pq.read_schema(p).names)
    if not set(SC).issubset(av): continue
    chunks.append(pd.read_parquet(p,columns=[c for c in need if c in av]))
df=pd.concat(chunks,ignore_index=True)
sc=df[SC].to_numpy(dtype=np.float64)
am=np.argmax(sc,axis=1)
is_sig=(am==0).astype(float)
p_sig=sc[:,0]
mtll=df["mtll"].to_numpy(float); mtl2=df["mtl2"].to_numpy(float)
print(f"pooled events: {len(df):,}   argmax=signal: {int(is_sig.sum()):,}")

MIN_N = 50   # suppress cells with too few events to be meaningful

# ---------------- (1) 2D plane ----------------
xb=np.linspace(0,300,61); yb=np.linspace(0,160,41)
n_all,_,_ = np.histogram2d(mtll,mtl2,bins=[xb,yb])
n_sig,_,_ = np.histogram2d(mtll,mtl2,bins=[xb,yb],weights=is_sig)
with np.errstate(invalid="ignore",divide="ignore"):
    frac = np.where(n_all>=MIN_N, n_sig/n_all, np.nan)

fig,ax=plt.subplots(figsize=(8.4,6.2))
pcm=ax.pcolormesh(xb,yb,100*frac.T,cmap="inferno",vmin=0,vmax=np.nanmax(100*frac))
cb=fig.colorbar(pcm,ax=ax); cb.set_label("% of events with argmax = signal")
ax.axvline(60,color="#00e5ff",lw=2.2,ls="--",label=r"SR cut  $m_T^{\ell\ell}>60$")
ax.axhline(30,color="#7CFC00",lw=2.2,ls="--",label=r"SR cut  $m_T^{\ell_2}>30$")
ax.set_xlabel(r"$m_T^{\ell\ell}$ [GeV]"); ax.set_ylabel(r"$m_T^{\ell_2}$ [GeV]")
ax.set_title("v11 argmax=signal density vs the SR cuts\n"
             "(2022postEE MC pooled, raw; cells with N<%d blank)"%MIN_N,fontsize=10)
ax.legend(loc="upper right",fontsize=9,framealpha=0.85)
fig.tight_layout(); f=OUT/"internalised_2d_plane.png"; fig.savefig(f,dpi=145,bbox_inches="tight"); plt.close(fig)
print("wrote",f)

# ---------------- (2) profile vs mTll ----------------
def profile(v, vb):
    n_all,_ = np.histogram(v,bins=vb)
    n_sig,_ = np.histogram(v,bins=vb,weights=is_sig)
    s_sum,_ = np.histogram(v,bins=vb,weights=p_sig)
    ctr=0.5*(vb[1:]+vb[:-1])
    ok=n_all>=MIN_N
    frac=np.where(ok,n_sig/np.maximum(n_all,1),np.nan)
    mean_p=np.where(ok,s_sum/np.maximum(n_all,1),np.nan)
    # binomial error on the fraction
    err=np.where(ok,np.sqrt(np.maximum(frac*(1-frac),0)/np.maximum(n_all,1)),np.nan)
    return ctr,frac,err,mean_p,n_all

for var,v,vb,cut,cutlab,fn in [
    ("mTll", mtll, np.linspace(0,300,61), 60, r"SR cut $m_T^{\ell\ell}>60$", "internalised_profile_mTll.png"),
    ("mTl2", mtl2, np.linspace(0,160,41), 30, r"SR cut $m_T^{\ell_2}>30$",  "internalised_profile_mTl2.png"),
]:
    ctr,frac,err,mean_p,n_all = profile(v,vb)
    fig,ax=plt.subplots(figsize=(8.6,5.4))
    ax.errorbar(ctr,100*frac,yerr=100*err,fmt="o-",ms=3.4,lw=1.6,color="#d62728",
                label="P(argmax = signal)")
    ax.axvline(cut,color="#1f77b4",lw=2.2,ls="--",label=cutlab)
    ax.axvspan(vb[0],cut,color="#1f77b4",alpha=0.07)
    ax.set_xlabel(rf"$m_T^{{\ell\ell}}$ [GeV]" if var=="mTll" else rf"$m_T^{{\ell_2}}$ [GeV]")
    ax.set_ylabel("% of events assigned argmax = signal",color="#d62728")
    ax.tick_params(axis="y",labelcolor="#d62728")
    ax.grid(alpha=0.25,ls=":")
    ax2=ax.twinx()
    ax2.plot(ctr,mean_p,lw=1.6,color="#555555",alpha=0.85,label="mean P(hplusc) score")
    ax2.set_ylabel("mean P(hplusc) score",color="#555555")
    ax2.tick_params(axis="y",labelcolor="#555555")
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax.legend(h1+h2,l1+l2,fontsize=9,loc="upper right",framealpha=0.9)
    ax.set_title(f"argmax=signal rate vs {var} - the MVA's own boundary vs the SR cut\n"
                 "2022postEE MC pooled, raw/unweighted",fontsize=10)
    ax.set_xlim(vb[0],vb[-1])
    fig.tight_layout(); f=OUT/fn; fig.savefig(f,dpi=145,bbox_inches="tight"); plt.close(fig)
    print("wrote",f)
    lo=(v<cut); hi=(v>=cut)
    print(f"   {var}: below cut argmax-sig rate = {100*is_sig[lo].mean():.4f}%  "
          f"| above = {100*is_sig[hi].mean():.3f}%  "
          f"| signal-argmax events below cut = {int(is_sig[lo].sum()):,}")
print("done")
