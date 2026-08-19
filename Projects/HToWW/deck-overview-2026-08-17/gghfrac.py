import glob, pyarrow.parquet as pq, yaml, json, numpy as np, os
R="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
B="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
cfg=yaml.safe_load(open(f"{R}/analysis/filesets/2022postEE_nanov12.yaml"))
# which samples carry process == ggH vs the rest of higgsbkg
groups={"ggH":["ggH"],"rest":["H+b","VBF","ZH","ggZH","WH","ttHnonBB","ttHtoBB","H(125)"]}
inv={}
for k,v in cfg.items():
    p=str(v.get("process","")).strip()
    for g,ps in groups.items():
        if p in ps: inv.setdefault(g,[]).append(k)
print("ggH samples :", inv.get("ggH"))
print("rest samples:", inv.get("rest"))
# sum weight_nominal in the SR-ish base parquet for each
def yield_of(samples):
    tot=0.0
    for s in samples or []:
        for f in glob.glob(f"{B}/parquets_{s}/base/*.parquet"):
            try:
                t=pq.read_table(f, columns=["weight_nominal"])
                tot+=float(np.sum(t.column("weight_nominal").to_numpy()))
            except Exception: pass
    return tot
a=yield_of(inv.get("ggH")); b=yield_of(inv.get("rest"))
print(f"\nggH  (unscaled sum w) = {a:,.1f}")
print(f"rest (unscaled sum w) = {b:,.1f}")
if a+b>0:
    f=a/(a+b)
    print(f"\nggH fraction of higgsbkg = {100*f:.1f}%")
    print(f"diluted lnN for 50% on ggH = 1 + 0.50*{f:.3f} = {1+0.5*f:.3f}")
