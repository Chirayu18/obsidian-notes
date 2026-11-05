import uproot
CH=("SR_hplusc","CR_higgsbkg","CR_tt","CR_st","CR_diboson","CR_vjets")
D="/eos/user/c/cgupta/higgscharm/outputs/combine/"
for tag,fn in (("sfchk (rebuild, SF)","v11_hplusc_sfchk.root"),
               ("nosf  (rebuild, noSF)","v11_hplusc_nosf.root"),
               ("v4    (reference, SF)","v11_hplusc_v4.root")):
    f=uproot.open(D+fn)
    sr=f["SR_hplusc_vjets"].values().sum()
    tot=sum(f[c+"_vjets"].values().sum() for c in CH)
    srtot=sum(f["SR_hplusc_"+p].values().sum() for p in ("hplusc","higgsbkg","tt","st","diboson","vjets"))
    print(f"{tag:24s} SR_vjets={sr:8.1f}  all-ch vjets={tot:9.1f}  SR_total={srtot:9.1f}")
