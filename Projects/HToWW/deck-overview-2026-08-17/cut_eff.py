"""Signal vs background efficiency of the c-jet cut compared to the mT/mll cuts.

Question: the >=1 c-jet cut kills a lot of signal, while mTll/mll/mTl2 kill background
but not signal. Would dropping the c-jet cut (and leaning on the kinematic ones) give
more signal?

The scored parquets ALREADY have >=1 c-jet applied (it is in the base category), so
they cannot answer "what happens without it". We instead quantify, on the sample we
have, the S and B efficiency of each KINEMATIC cut, and read the c-jet efficiency off
the coffea cutflow / by comparing to the pre-cjet yield.

Weighted (lumi*xsec/sumw), which is what matters for a limit.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO=Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0,str(REPO)); sys.path.insert(0,str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples, read_scale, load_lumi

YEAR="2022postEE"; WF="hww_combine_fixed"
BASE=Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR; MVA=BASE/"mva"
CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"]); lumi=load_lumi(YEAR)
s2p={s:cp for cp,ss in c2s.items() for s in ss}

need=SC+["mtll","mtl2","dilepton_mass","weight_nominal"]
fr=[]
for s,cp in sorted(s2p.items()):
    p=MVA/f"{s}.parquet"
    if not p.exists(): continue
    av=set(pq.read_schema(p).names)
    if not set(SC).issubset(av): continue
    cols=[c for c in need if c in av]+(["weight_negrw"] if cp=="vjets" and "weight_negrw" in av else [])
    d=pd.read_parquet(p,columns=cols)
    if len(d)==0: continue
    w=d["weight_nominal"].to_numpy(float)
    if cp=="vjets" and "weight_negrw" in d.columns:
        g=d["weight_negrw"].to_numpy(float); sw,swg=w.sum(),(np.abs(w)*g).sum()
        w=np.abs(w)*g*((sw/swg) if swg else 1.0)
    d["w"]=w*read_scale(s,YEAR,BASE,lumi); d["true_proc"]=cp
    fr.append(d)
df=pd.concat(fr,ignore_index=True)
w=df.w.to_numpy(float); truth=df.true_proc.to_numpy()
mtll=df.mtll.to_numpy(float); mtl2=df.mtl2.to_numpy(float); mll=df.dilepton_mass.to_numpy(float)
S=(truth=="hplusc"); B=~S
s0,b0=w[S].sum(),w[B].sum()
print(f"AFTER >=1 c-jet (what the parquets contain):")
print(f"  signal yield     = {s0:.4f}")
print(f"  background yield = {b0:,.1f}")
print(f"  S/sqrt(B)        = {s0/np.sqrt(b0):.5f}\n")

CUTS=[("mTll > 60",            mtll>60),
      ("mTl2 > 30",            mtl2>30),
      ("mll <= 72",            mll<=72),
      ("mTll>60 & mTl2>30",    (mtll>60)&(mtl2>30)),
      ("ALL THREE (SR)",       (mtll>60)&(mtl2>30)&(mll<=72))]
hdr=f"{'cut':<22s} {'eff_S':>8s} {'eff_B':>8s} {'S':>9s} {'B':>12s} {'S/sqrtB':>9s} {'gain':>7s}"
print("Efficiency of each KINEMATIC cut (on top of >=1 c-jet):")
print(hdr); print("-"*len(hdr))
base_z=s0/np.sqrt(b0)
for name,m in CUTS:
    es=w[S&m].sum()/s0; eb=w[B&m].sum()/b0
    s1,b1=w[S&m].sum(),w[B&m].sum()
    z=s1/np.sqrt(b1) if b1>0 else 0
    print(f"{name:<22s} {es:>8.4f} {eb:>8.4f} {s1:>9.4f} {b1:>12,.1f} {z:>9.5f} {z/base_z:>6.2f}x")
