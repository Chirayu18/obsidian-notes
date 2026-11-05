"""Population of the two CRs, by argmax class AND by true process group.

Top CR    : mTl2 > 30 && mTll <= 60      (inverts the SR mTll cut)
High-mll CR: mll > 72                     (inverts the SR mll<=72 cut)

Decides which classes have enough stats to be worth plotting separately.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples

YEAR="2022postEE"; WF="hww_combine_fixed"
MVA=Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR/"mva"
CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
# sample -> its combine process (true origin)
s2p={s:cp for cp,ss in c2s.items() for s in ss}

need=SC+["mtll","mtl2","dilepton_mass"]
frames=[]
for s,cp in sorted(s2p.items()):
    p=MVA/f"{s}.parquet"
    if not p.exists(): continue
    av=set(pq.read_schema(p).names)
    if not set(SC).issubset(av): continue
    d=pd.read_parquet(p,columns=[c for c in need if c in av])
    if len(d)==0: continue
    d["true_proc"]=cp
    frames.append(d)
df=pd.concat(frames,ignore_index=True)
sc=df[SC].to_numpy(float); am=np.argmax(sc,axis=1)
df["argmax"]=[CLASSES[i] for i in am]
mtll=df.mtll.to_numpy(float); mtl2=df.mtl2.to_numpy(float); mll=df.dilepton_mass.to_numpy(float)

REGIONS={
 "SR (mTl2>30 & mTll>60 & mll<=72)": (mtl2>30)&(mtll>60)&(mll<=72),
 "Top CR (mTl2>30 & mTll<=60)":      (mtl2>30)&(mtll<=60),
 "High-mll CR (mll>72)":             (mll>72),
 "High-mll CR & SR-mT (mll>72 & mTl2>30 & mTll>60)": (mll>72)&(mtl2>30)&(mtll>60),
}
print(f"pooled: {len(df):,}\n")
for name,m in REGIONS.items():
    print(f"=== {name} :  N={int(m.sum()):,} ({100*m.mean():.2f}% of pool) ===")
    sub=df[m]
    print("  by ARGMAX class:")
    vc=sub["argmax"].value_counts()
    for c in CLASSES:
        n=int(vc.get(c,0))
        print(f"    {c:<10s} {n:>9,d}  ({100*n/max(len(sub),1):5.2f}%)")
    print("  by TRUE process:")
    vt=sub["true_proc"].value_counts()
    for c in CLASSES:
        n=int(vt.get(c,0))
        print(f"    {c:<10s} {n:>9,d}  ({100*n/max(len(sub),1):5.2f}%)")
    print()
