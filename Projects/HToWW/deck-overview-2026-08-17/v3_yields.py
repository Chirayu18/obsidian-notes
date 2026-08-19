"""Variant 3: signal and background yields vs the 2dcat baseline.

Both trees are read the same way (per-sample base/ shards, lumi*xsec/sumw via
read_scale, negrw applied to vjets) so the comparison is like-for-like.
The point: variant 3 gains signal but admits more ggH/tt -- does S/sqrt(B) improve?
"""
import sys, glob
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

REPO=Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0,str(REPO)); sys.path.insert(0,str(REPO/"scripts"/"combine"))
from analysis.workflows.config import WorkflowConfigBuilder
from make_combine_inputs import gather_samples, read_scale, load_lumi

YEAR="2022postEE"
OUT=Path("/eos/user/c/cgupta/higgscharm/outputs")
lumi=load_lumi(YEAR)
cfg=WorkflowConfigBuilder(workflow="hww_combine_2dcat").build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"])
s2p={s:cp for cp,ss in c2s.items() for s in ss}

def tree_yields(wf):
    base=OUT/wf/YEAR
    out={}
    for s,cp in s2p.items():
        fs=sorted(glob.glob(f"{base}/{s}/base/*.parquet"))+sorted(glob.glob(f"{base}/{s}_*/base/*.parquet"))
        if not fs: continue
        tot=0.0; n=0
        for f in fs:
            try:
                av=set(pq.read_schema(f).names)
                cols=["weight_nominal"]+(["weight_negrw"] if (cp=="vjets" and "weight_negrw" in av) else [])
                d=pd.read_parquet(f,columns=cols)
            except Exception: continue
            if len(d)==0: continue
            w=d["weight_nominal"].to_numpy(float)
            if cp=="vjets" and "weight_negrw" in d.columns:
                g=d["weight_negrw"].to_numpy(float); sw,swg=w.sum(),(np.abs(w)*g).sum()
                w=np.abs(w)*g*((sw/swg) if swg else 1.0)
            tot+=w.sum(); n+=len(d)
        try: sc=read_scale(s,YEAR,base,lumi)
        except Exception: sc=1.0
        out.setdefault(cp,[0,0.0])
        out[cp][0]+=n; out[cp][1]+=tot*sc
    return out

for wf,label in [("hww_combine_2dcat","BASELINE (medium WP)"),
                 ("hww_2dcat_nocjet_kin","VARIANT 3 (no tag + kin)")]:
    y=tree_yields(wf)
    if not y:
        print(f"\n=== {label}: no data ==="); continue
    sig=y.get("hplusc",[0,0.0])[1]
    bkg=sum(v[1] for k,v in y.items() if k!="hplusc")
    ggh=y.get("higgsbkg",[0,0.0])[1]
    print(f"\n=== {label} ===")
    print(f"{'process':<10s} {'raw N':>12s} {'yield':>14s}")
    for k in ["hplusc","higgsbkg","tt","st","diboson","vjets"]:
        n,w=y.get(k,[0,0.0]); print(f"{k:<10s} {n:>12,d} {w:>14.3f}")
    print(f"{'TOTAL BKG':<10s} {'':<12s} {bkg:>14.3f}")
    if bkg>0:
        print(f"  S/sqrt(B) = {sig/np.sqrt(bkg):.6f}")
        print(f"  S/B       = {sig/bkg:.3e}")
        print(f"  higgsbkg/S = {ggh/sig:.1f}" if sig else "")
