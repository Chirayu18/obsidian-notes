import uproot, numpy as np, awkward as ak, subprocess
DS={
 "INCL":"/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM",
 "2J":"/WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM",
}
# how much of the jet-binned phase space lies BEYOND the inclusive sample's coverage?
f=subprocess.run(["dasgoclient","-query",f"file dataset={DS['INCL']}"],capture_output=True,text=True).stdout.split()[0]
a=uproot.open("root://cms-xrd-global.cern.ch/"+f)["Events"].arrays(["LHE_Vpt","LHE_HT","LHE_Njets"],entry_stop=400000)
iv=ak.to_numpy(a["LHE_Vpt"]); ih=ak.to_numpy(a["LHE_HT"])
print(f"INCLUSIVE support: Vpt max={iv.max():.1f}  HT max={ih.max():.1f}")
print(f"  Vpt p99.9={np.percentile(iv,99.9):.1f}  HT p99.9={np.percentile(ih,99.9):.1f}")
f=subprocess.run(["dasgoclient","-query",f"file dataset={DS['2J']}"],capture_output=True,text=True).stdout.split()[0]
b=uproot.open("root://cms-xrd-global.cern.ch/"+f)["Events"].arrays(["LHE_Vpt","LHE_HT"],entry_stop=400000)
bv=ak.to_numpy(b["LHE_Vpt"]); bh=ak.to_numpy(b["LHE_HT"])
print(f"\n2J events beyond inclusive p99.9:")
print(f"  Vpt > {np.percentile(iv,99.9):.1f} : {100*(bv>np.percentile(iv,99.9)).mean():.2f}%")
print(f"  HT  > {np.percentile(ih,99.9):.1f} : {100*(bh>np.percentile(ih,99.9)).mean():.2f}%")
print(f"  beyond ABSOLUTE incl max Vpt {iv.max():.0f}: {100*(bv>iv.max()).mean():.3f}%")
print(f"  beyond ABSOLUTE incl max HT  {ih.max():.0f}: {100*(bh>ih.max()).mean():.3f}%")
