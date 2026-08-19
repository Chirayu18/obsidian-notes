import uproot, numpy as np, glob, os
# The v32 card splits ggH into its own process -- use it to get the true fraction.
B="/eos/user/c/cgupta/higgscharm/outputs/combine/"
cands=sorted(glob.glob(B+"*v32*.root"))+sorted(glob.glob(B+"*kappa*.root"))
print("v32/kappa cards available:", [os.path.basename(c) for c in cands][:5])
for c in cands[:1]:
    f=uproot.open(c)
    ks=[k.split(";")[0] for k in f.keys()]
    sr=[k for k in ks if k.startswith("SR_hplusc_")]
    print("\nprocesses in", os.path.basename(c), ":")
    tot=0; vals={}
    for k in sorted(set(sr)):
        p=k.replace("SR_hplusc_","")
        if any(x in p for x in ["Up","Down","data_obs"]): continue
        v=f[k].values().sum(); vals[p]=v
        print(f"   {p:14s} {v:10.3f}")
