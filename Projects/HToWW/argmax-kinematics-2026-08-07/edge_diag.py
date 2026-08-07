"""Quantify the mTll edge seen in the argmax=signal class.

Two questions:
 (1) how sharp is the wall -- what fraction of ALL events below mTll<60 get
     argmax=signal, vs just above?
 (2) is it a training-region artifact? mTll is NOT a v11 input feature, so if the
     wall is real the network must be reconstructing mTll from the features it has.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR="2022postEE"; WF="hww_combine_fixed"
MVA = Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR/"mva"
CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
samples=sorted({s for v in c2s.values() for s in v})

need=SC+["mtll","dilepton_mass","mtl2","mtl1","met_pt","dilepton_pt"]
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
is_sig=(am==0)
mtll=df["mtll"].to_numpy(dtype=np.float64)
print(f"total pooled events: {len(df):,}\n")

# (1) sharpness: P(argmax=signal | mTll bin)
print("=== P(argmax = signal) vs mTll  [the wall] ===")
print(f"{'mTll bin':>16s} {'N_all':>10s} {'N_sig':>9s} {'P(sig)':>9s} {'max P_hplusc':>13s}")
edges=[0,10,20,30,40,45,50,52,53,54,55,56,58,60,62,65,70,80,100,150,200,250,400]
for lo,hi in zip(edges[:-1],edges[1:]):
    m=(mtll>=lo)&(mtll<hi)
    n=int(m.sum())
    if n==0: continue
    ns=int(is_sig[m].sum())
    mx=sc[m,0].max()
    print(f"{f'[{lo},{hi})':>16s} {n:>10d} {ns:>9d} {100.0*ns/n:>8.3f}% {mx:>13.4f}")

print("\n=== exact wall location ===")
sig_mtll=mtll[is_sig]
print("min mTll with argmax=signal:", f"{sig_mtll.min():.4f}")
for q in [0,0.001,0.01,0.05,0.1,0.5,1.0]:
    print(f"  p{q:<6} = {np.percentile(sig_mtll,q):9.3f}")
lo=np.sort(sig_mtll)[:25]
print("  25 lowest:", np.round(lo,2))

# how many events exist below the wall at all?
below=(mtll<52.76)
print(f"\nevents with mTll < 52.76 : {int(below.sum()):,} "
      f"({100.0*below.mean():.2f}% of pool)")
print(f"  of these, argmax=signal : {int(is_sig[below].sum()):,}")
print(f"  their max P(hplusc)     : {sc[below,0].max():.4f}")
print(f"  their mean P(hplusc)    : {sc[below,0].mean():.4f}")

# (2) is the SR cut mTll>60 the cause? check the mTl2>30 companion cut too
print("\n=== SR cuts are mTl2>30 AND mTll>60 ===")
mtl2=df["mtl2"].to_numpy(dtype=np.float64)
sr=(mtl2>30)&(mtll>60)
print(f"events passing SR kinematic cuts : {int(sr.sum()):,} ({100.0*sr.mean():.2f}%)")
print(f"argmax=signal INSIDE  SR cuts    : {int(is_sig[sr].sum()):,} "
      f"({100.0*is_sig[sr].mean():.2f}% of SR)")
print(f"argmax=signal OUTSIDE SR cuts    : {int(is_sig[~sr].sum()):,} "
      f"({100.0*is_sig[~sr].mean():.4f}% of non-SR)")
frac_out = is_sig[~sr].sum()/is_sig.sum()
print(f"fraction of ALL signal-argmax events outside SR cuts: {100*frac_out:.3f}%")

# where exactly do the outside-SR signal events sit?
osr = is_sig & (~sr)
if osr.sum():
    print(f"  their mTll : min={mtll[osr].min():.2f} max={mtll[osr].max():.2f}")
    print(f"  their mTl2 : min={mtl2[osr].min():.2f} max={mtl2[osr].max():.2f}")
    print(f"  n with mTll<=60: {int((mtll[osr]<=60).sum()):,}")
    print(f"  n with mTl2<=30: {int((mtl2[osr]<=30).sum()):,}")
