import uproot
CH=("SR_hplusc","CR_higgsbkg","CR_tt","CR_st","CR_diboson","CR_vjets")
P=("hplusc","higgsbkg","tt","st","diboson","vjets")
D="/eos/user/c/cgupta/higgscharm/outputs/combine/"
for tag,fn in (("v4 SF   sidecar","v11_hplusc_v4.root.bak_sidecar_20260731"),
               ("v4 SF   records","v11_hplusc_v4.root"),
               ("nosf    records","v11_hplusc_nosf.root")):
    f=uproot.open(D+fn)
    sig=f["SR_hplusc_hplusc"].values().sum()
    srv=f["SR_hplusc_vjets"].values().sum()
    tot=sum(f[c+"_vjets"].values().sum() for c in CH)
    print(f"{tag:16s} SR_signal={sig:7.4f}  SR_vjets={srv:8.1f}  all-vjets={tot:9.1f}")
