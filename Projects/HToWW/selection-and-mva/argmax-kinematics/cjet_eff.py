"""Per-process >=1 c-jet efficiency: post-cjet yield / pre-cjet yield.

Pre-cjet numbers come from the 2026-07-07 cutflow note (one_mu_one_e column, the last
step before the c-jet requirement). Post-cjet = the scored parquets.

CAVEAT: the cutflow predates the sumw fix, when signal normalisation was 18.4% HIGH
(sidecar 9.266e4 vs records 7.823e4). We divide that out of the signal pre-cjet number.
tt/st/diboson scales were exact (1.0000) and need no correction.
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

# post-cjet yields per SAMPLE (so we can pick out ggH specifically)
post={}
for cp,ss in c2s.items():
    for s in ss:
        p=MVA/f"{s}.parquet"
        if not p.exists(): continue
        av=set(pq.read_schema(p).names)
        if not set(SC).issubset(av): continue
        cols=["weight_nominal"]+(["weight_negrw"] if cp=="vjets" and "weight_negrw" in av else [])
        d=pd.read_parquet(p,columns=cols)
        if len(d)==0: continue
        w=d["weight_nominal"].to_numpy(float)
        if cp=="vjets" and "weight_negrw" in d.columns:
            g=d["weight_negrw"].to_numpy(float); sw,swg=w.sum(),(np.abs(w)*g).sum()
            w=np.abs(w)*g*((sw/swg) if swg else 1.0)
        post[s]=w.sum()*read_scale(s,YEAR,BASE,lumi)

# pre-cjet, from the cutflow note (one_mu_one_e). signal corrected for the sumw fix.
SUMW_CORR = 7.823e4/9.266e4     # records/sidecar = 0.8443
PRE = {
 "H+c":        1.49*SUMW_CORR,
 "ggH":        856.64,
 "VBF":        118.18,
 "ZH":          18.98,
 "ggZH":         4.21,
 "ttHnonBB":     3.72,
 "ttHtoBB":     66.18,
 "tt":       1.781e5,
 "Single Top":1.887e4,
 "WW":       1.254e4,
 "WZ":        1040.50,
 "ZZ":         104.74,
}
POST_MAP = {
 "H+c":["HplusCharm_HtoWW"],
 "ggH":["GluGluHto2Wto2L2Nu"],
 "VBF":["VBFHto2Wto2L2Nu"],
 "ZH":["ZH_ZtoAll_Hto2Wto2L2Nu"],
 "ggZH":["GluGluZH_ZtoAll_Hto2Wto2L2Nu"],
 "ttHtoBB":["ttHtoBB"],
 "tt":["TTto2L2Nu","TTto4Q","TTtoLNu2Q"],
 "Single Top":["TWminusto2L2Nu","TWminusto4Q","TWminustoLNu2Q","TbarWplusto2L2Nu",
               "TbarWplusto4Q","TbarWplustoLNu2Q","TBbarQ","TbarBQ",
               "TBbartoLplusNuBbar","TbarBtoLminusNuB","TQbarto2Q","TQbartoLNu",
               "TbarQto2Q","TbarQtoLNu"],
 "WW":["WW"], "WZ":["WZ"], "ZZ":["ZZ"],
}
print(f"{'process':<12s} {'pre-cjet':>11s} {'post-cjet':>11s} {'cjet eff':>9s}")
print("-"*48)
eff={}
for name,samples in POST_MAP.items():
    po=sum(post.get(s,0.0) for s in samples)
    pr=PRE.get(name,0.0)
    if pr<=0: continue
    eff[name]=po/pr
    print(f"{name:<12s} {pr:>11,.2f} {po:>11,.2f} {100*po/pr:>8.2f}%")

print("\n=== the number that matters: H+c vs ggH ===")
if "H+c" in eff and "ggH" in eff:
    print(f"  c-jet eff  H+c = {100*eff['H+c']:.2f}%")
    print(f"  c-jet eff  ggH = {100*eff['ggH']:.2f}%")
    print(f"  ENRICHMENT  H+c/ggH = {eff['H+c']/eff['ggH']:.2f}x")
    pre_r  = PRE["ggH"]/PRE["H+c"]
    post_r = sum(post.get(s,0) for s in POST_MAP["ggH"])/sum(post.get(s,0) for s in POST_MAP["H+c"])
    print(f"\n  ggH:H+c ratio BEFORE c-jet = {pre_r:,.1f} : 1")
    print(f"  ggH:H+c ratio AFTER  c-jet = {post_r:,.1f} : 1")
    print(f"  improvement = {pre_r/post_r:.2f}x")
    print(f"\n  5% lnN on higgsbkg (xsec_higgsbkg 1.05):")
    print(f"    before c-jet: 0.05*{PRE['ggH']:.1f} = {0.05*PRE['ggH']:.2f} events "
          f"= {0.05*PRE['ggH']/PRE['H+c']:.1f}x the signal")
    ggh_post=sum(post.get(s,0) for s in POST_MAP["ggH"]); hc_post=sum(post.get(s,0) for s in POST_MAP["H+c"])
    print(f"    after  c-jet: 0.05*{ggh_post:.1f} = {0.05*ggh_post:.2f} events "
          f"= {0.05*ggh_post/hc_post:.1f}x the signal")
