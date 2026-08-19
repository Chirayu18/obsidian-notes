import uproot
D="/eos/user/c/cgupta/higgscharm/outputs/combine/"
CH=("SR_hplusc","CR_higgsbkg","CR_tt","CR_st","CR_diboson","CR_vjets")
P=("hplusc","higgsbkg","tt","st","diboson","vjets")
old=uproot.open(D+"v11_hplusc_v4.root.bak_sidecar_20260731")
new=uproot.open(D+"v11_hplusc_v4.root")
print(f"{'process':10s} {'sidecar':>12s} {'records':>12s} {'ratio':>7s}   (summed over all 6 channels)")
for p in P:
    o=sum(old[c+"_"+p].values().sum() for c in CH)
    n=sum(new[c+"_"+p].values().sum() for c in CH)
    print(f"{p:10s} {o:12.2f} {n:12.2f} {n/o:7.4f}")
print()
o=old["SR_hplusc_hplusc"].values().sum(); n=new["SR_hplusc_hplusc"].values().sum()
print(f"SR signal  {o:12.4f} {n:12.4f} {n/o:7.4f}")
o=old["SR_hplusc_vjets"].values().sum(); n=new["SR_hplusc_vjets"].values().sum()
print(f"SR vjets   {o:12.2f} {n:12.2f} {n/o:7.4f}")
