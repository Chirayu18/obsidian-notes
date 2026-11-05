"""Scan candidate CR definitions on the three axes that matter for a rateParam CR:
   purity in TRUE tt, size, and SR contamination (signal leakage).

The datacard floats only `tt` (rate_params: [tt]), so a CR earns its place by pinning
the tt rate: high true-tt purity, enough events, and negligible signal.
Yields are weighted (lumi*xsec/sumw) since a rateParam constrains a RATE.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO=Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0,str(REPO)); sys.path.insert(0,str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples, read_scale, load_lumi

YEAR="2022postEE"; WF="hww_combine_fixed"
BASE=Path("/eos/user/c/cgupta/higgscharm/outputs")/WF/YEAR
MVA=BASE/"mva"
CLASSES=["hplusc","higgsbkg","tt","st","diboson","vjets"]
SC=[f"mva_score_{c}" for c in CLASSES]
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
lumi=load_lumi(YEAR)
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
    d["w"]=w*read_scale(s,YEAR,BASE,lumi)
    d["true_proc"]=cp
    fr.append(d)
df=pd.concat(fr,ignore_index=True)
sc=df[SC].to_numpy(float); am=np.argmax(sc,axis=1)
mtll=df.mtll.to_numpy(float); mtl2=df.mtl2.to_numpy(float); mll=df.dilepton_mass.to_numpy(float)
w=df.w.to_numpy(float); truth=df.true_proc.to_numpy()
print(f"pooled {len(df):,}   total weighted {w.sum():,.1f}\n")

SR=(mtl2>30)&(mtll>60)&(mll<=72)

CANDS=[
 # --- top-CR style: want high true-tt purity ---
 ("CURRENT Top CR: mTl2>30 & mTll<=60",           (mtl2>30)&(mtll<=60)),
 ("A1 mll>100                       ",            (mll>100)),
 ("A2 mll>110                       ",            (mll>110)),
 ("A3 mll>100 & mTll>60             ",            (mll>100)&(mtll>60)),
 ("A4 mll>110 & mTll>60 & mTl2>30   ",            (mll>110)&(mtll>60)&(mtl2>30)),
 ("A5 argmax=tt & mll>100           ",            (am==2)&(mll>100)),
 ("A6 argmax=tt & mll>72            ",            (am==2)&(mll>72)),
 ("A7 argmax=tt (inclusive)         ",            (am==2)),
 ("A8 argmax=tt & mTll>60 & mTl2>30 ",            (am==2)&(mtll>60)&(mtl2>30)),
 # --- high-mll CR style ---
 ("CURRENT High-mll CR: mll>72      ",            (mll>72)),
 ("B1 72<mll<=100                   ",            (mll>72)&(mll<=100)),
 ("B2 72<mll<=100 & mTll>60         ",            (mll>72)&(mll<=100)&(mtll>60)),
 ("B3 mll>72 & mTll>60 & mTl2>30    ",            (mll>72)&(mtll>60)&(mtl2>30)),
]
hdr=(f"{'definition':<38s} {'N_raw':>10s} {'yield':>11s} {'tt-pur':>8s} "
     f"{'sig-yld':>9s} {'S/B':>8s} {'SRoverlap':>10s}")
print(hdr); print("-"*len(hdr))
sr_w=w[SR].sum()
for name,m in CANDS:
    n=int(m.sum())
    if n==0:
        print(f"{name:<38s} {'0':>10s}"); continue
    tot=w[m].sum()
    tt=w[m&(truth=="tt")].sum()
    sig=w[m&(truth=="hplusc")].sum()
    ov=w[m&SR].sum()
    print(f"{name:<38s} {n:>10,d} {tot:>11,.1f} {100*tt/tot:>7.2f}% "
          f"{sig:>9.3f} {sig/max(tot-sig,1e-9)*100:>7.3f}% {100*ov/max(sr_w,1e-9):>9.2f}%")
print(f"\nSR yield (reference) = {sr_w:,.1f}   SR true-tt purity = "
      f"{100*w[SR&(truth=='tt')].sum()/sr_w:.2f}%")
print(f"SR signal yield = {w[SR&(truth=='hplusc')].sum():.3f}")
