import sys, glob, numpy as np, yaml
sys.path.insert(0,"/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
import importlib
base=importlib.import_module("scripts.combine.make_combine_inputs_v2")
R="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
cfg=yaml.safe_load(open(f"{R}/analysis/filesets/2022postEE_nanov12.yaml"))
GG={"ggH"}
gg=[k for k,v in cfg.items() if str(v.get("process","")).strip() in GG]
rest=[k for k,v in cfg.items() if str(v.get("process","")).strip() in
      {"H+b","VBF","ZH","ggZH","WH","ttHnonBB","ttHtoBB","H(125)"}]
print("ggH samples:",gg)
def scaled(sample):
    try:
        s=base.read_scale(sample,"2022postEE")
    except Exception as e:
        return None
    tot=0.0
    for f in glob.glob(f"/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE/parquets_{sample}/base/*.parquet"):
        import pyarrow.parquet as pq
        t=pq.read_table(f,columns=["weight_nominal"])
        tot+=float(np.sum(t.column("weight_nominal").to_numpy()))
    return tot*s
a=0.0
for s in gg:
    v=scaled(s)
    if v: a+=v; print(f"  {s:32s} {v:12.3f}")
b=0.0
for s in rest:
    v=scaled(s)
    if v: b+=v
print(f"\nggH  scaled yield = {a:.3f}")
print(f"rest scaled yield = {b:.3f}")
if a+b>0:
    fr=a/(a+b)
    print(f"\nggH fraction of higgsbkg = {100*fr:.1f}%")
    print(f"diluted lnN (option A)   = {1+0.5*fr:.4f}")
