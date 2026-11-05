import glob
import numpy as np, pandas as pd
D="/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE"
fs=sorted(glob.glob(f"{D}/HplusCharm_HtoWW*/base/*.parquet"))
cols=["cjet_cand_cvsl_pnet","cjet_cand_cvsb_pnet","cjet_cand_pt","cjet_cand_hadronflavour"]
d=None
for f in fs[:40]:
    import pyarrow.parquet as pq
    av=set(pq.read_schema(f).names)
    use=[c for c in cols if c in av]
    x=pd.read_parquet(f,columns=use)
    d=x if d is None else pd.concat([d,x],ignore_index=True)
print("columns present:", list(d.columns))
a=d.cjet_cand_cvsl_pnet.to_numpy(float)
b=d.cjet_cand_cvsb_pnet.to_numpy(float)
m=(a==-1)
print(f"\nCvL==-1: {m.sum()}   CvB==-1: {(b==-1).sum()}   both: {(m&(b==-1)).sum()}")
print("CvL range for NON-sentinel events: %.4f .. %.4f"%(a[~m].min(),a[~m].max()))
print("CvB range for NON-sentinel events: %.4f .. %.4f"%(b[~(b==-1)].min(),b[~(b==-1)].max()))
if "cjet_cand_hadronflavour" in d.columns:
    h=d.cjet_cand_hadronflavour.to_numpy(float)
    print("hadronFlavour for CvL==-1:", np.unique(h[m]))
    print("hadronFlavour==-1 count:", (h==-1).sum())
