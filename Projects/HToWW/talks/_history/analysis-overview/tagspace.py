"""Where do signal and ggH sit inside the medium-WP region?

The parquets contain ONLY jets already passing medium (CvB>0.304 & CvL>0.160), so we
cannot measure loose-WP recovery directly. What we CAN measure is how close the
surviving signal sits to the threshold: if signal piles up near the boundary, a looser
cut (or a continuous treatment) recovers a lot; if it sits far inside, it recovers
little.

Also reports the 2D-category composition per process -- which categories carry signal
vs ggH -- since that is what the 2dcat model actually sees.
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
cfg=WorkflowConfigBuilder(workflow=WF).build_workflow_config()
c2s=gather_samples(YEAR,cfg.combine["process_map"]); lumi=load_lumi(YEAR)

M_CVL, M_CVB = 0.160, 0.304
TARGETS={"H+c":["HplusCharm_HtoWW"],
         "ggH":["GluGluHto2Wto2L2Nu"],
         "tt":["TTto2L2Nu"],
         "WW":["WW"]}
cols=["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","weight_nominal"]
print(f"medium WP: CvL>{M_CVL}  CvB>{M_CVB}\n")
print(f"{'proc':<6s} {'N':>8s} {'CvL p10':>8s} {'p25':>7s} {'p50':>7s} "
      f"{'CvB p10':>8s} {'p25':>7s} {'p50':>7s} {'near-thr':>9s}")
print("-"*76)
store={}
for name,samples in TARGETS.items():
    cl,cb,ws=[],[],[]
    for s in samples:
        p=MVA/f"{s}.parquet"
        if not p.exists(): continue
        av=set(pq.read_schema(p).names)
        if not {"cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet"}.issubset(av): continue
        d=pd.read_parquet(p,columns=[c for c in cols if c in av])
        d=d.dropna(subset=["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet"])
        if len(d)==0: continue
        cl.append(d["cjet_cand_cvsl_pnet"].to_numpy(float))
        cb.append(d["cjet_cand_cvsb_pnet"].to_numpy(float))
        ws.append(d["weight_nominal"].to_numpy(float)*read_scale(s,YEAR,BASE,lumi))
    if not cl: continue
    cl=np.concatenate(cl); cb=np.concatenate(cb); ws=np.concatenate(ws)
    store[name]=(cl,cb,ws)
    # "near threshold" = within 20% above the medium cut in EITHER variable
    near=((cl<M_CVL*1.5)|(cb<M_CVB*1.3)).mean()
    q=lambda a,p: np.percentile(a,p)
    print(f"{name:<6s} {len(cl):>8,d} {q(cl,10):>8.3f} {q(cl,25):>7.3f} {q(cl,50):>7.3f} "
          f"{q(cb,10):>8.3f} {q(cb,25):>7.3f} {q(cb,50):>7.3f} {100*near:>8.1f}%")

print("\n=== how discriminating is CvL between H+c and ggH (inside medium)? ===")
if "H+c" in store and "ggH" in store:
    for var,i in (("CvL",0),("CvB",1)):
        s=store["H+c"][i]; g=store["ggH"][i]
        print(f"  {var}: H+c median={np.median(s):.3f}   ggH median={np.median(g):.3f}"
              f"   separation={np.median(s)-np.median(g):+.3f}")
    # AUC-like overlap: P(random H+c jet more charm-like than random ggH jet)
    for var,i in (("CvL",0),("CvB",1)):
        s=store["H+c"][i]; g=store["ggH"][i]
        gs=np.sort(g)
        auc=np.searchsorted(gs,s,side="left").mean()/len(gs)
        print(f"  AUC({var}) H+c vs ggH = {auc:.4f}   (0.5 = no separation)")
