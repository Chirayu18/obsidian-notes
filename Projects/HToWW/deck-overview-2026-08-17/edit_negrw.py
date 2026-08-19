import shutil, datetime, sys
P="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml"
bak=P+".bak_pre_wjets_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(P,bak); print("backup:",bak)
s=open(P).read()
old="""  datasets:
    - DYto2L_2Jets_10to50
    - DYto2L_2Jets_50
    - WtoLNu_2Jets
"""
new="""  datasets:
    - DYto2L_2Jets_10to50
    - DYto2L_2Jets_50
    # W+jets jet-binned (replaced the inclusive WtoLNu_2Jets, 2026-08-13).
    # The SAME ensemble applies: P+(x) is a generator property of amc@NLO FxFx,
    # and these are the same generator/tune/merging sliced by jet multiplicity --
    # lhe_njets is already an input feature. Verified no extrapolation: the
    # jet-binned gen phase space sits inside the inclusive sample's support
    # (2J beyond incl. max Vpt: 0.002%, beyond max HT: 0.000%).
    - WtoLNu_2Jets_0J
    - WtoLNu_2Jets_1J
    - WtoLNu_2Jets_2J
"""
if old not in s: print("FATAL: negrw datasets block not found"); sys.exit(1)
open(P,"w").write(s.replace(old,new)); print("written")
import yaml
d=yaml.safe_load(open(P)); b=yaml.safe_load(open(bak))
print("negrw datasets:", d["negrw"]["datasets"])
print("negrw model unchanged:", d["negrw"]["model"]==b["negrw"]["model"])
ks=[k for k in b if b[k]!=d.get(k)]
print("top-level blocks changed:", ks)
