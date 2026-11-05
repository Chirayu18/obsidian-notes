import glob
import numpy as np, pandas as pd
D="/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE"
fs=sorted(glob.glob(f"{D}/HplusCharm_HtoWW*/base/*.parquet"))
d=pd.concat([pd.read_parquet(f,columns=["cjet_cand_cvsl_pnet","cjet_cand_pt","njets" if False else "jet_multiplicity"]) for f in fs[:40]],ignore_index=True)
a=d.cjet_cand_cvsl_pnet.to_numpy(float); p=d.cjet_cand_pt.to_numpy(float)
m=(a==-1)
print(f"events: {len(d):,}   CvL==-1: {m.sum()}")
print("for those events, cjet_cand_pt values:", np.unique(p[m])[:10])
print("pt min overall:", np.nanmin(p), " any pt<20?", (p<20).sum())
print("\njet_multiplicity for CvL==-1 events:", np.unique(d.jet_multiplicity.to_numpy()[m])[:10])
