import uproot, numpy as np, awkward as ak, subprocess
DS={
 "INCL":"/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM",
 "0J":"/WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3/NANOAODSIM",
 "1J":"/WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM",
 "2J":"/WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM",
}
BR=["LHE_Njets","LHE_Vpt","LHE_HT","LHE_Nb","LHE_Nc","genWeight"]
print(f"{'samp':5s} {'Njets':>14s} {'Vpt p50/p99':>16s} {'HT p50/p99':>16s} {'Nb>0':>7s} {'Nc>0':>7s}")
for tag,ds in DS.items():
    f=subprocess.run(["dasgoclient","-query",f"file dataset={ds}"],capture_output=True,text=True).stdout.split()[0]
    t=uproot.open("root://cms-xrd-global.cern.ch/"+f)["Events"]
    a=t.arrays(BR,entry_stop=200000)
    nj=ak.to_numpy(a["LHE_Njets"]); v=ak.to_numpy(a["LHE_Vpt"]); ht=ak.to_numpy(a["LHE_HT"])
    nb=ak.to_numpy(a["LHE_Nb"]); nc=ak.to_numpy(a["LHE_Nc"])
    print(f"{tag:5s} {str(sorted(set(nj.tolist()))):>14s} "
          f"{np.percentile(v,50):7.1f}/{np.percentile(v,99):7.1f} "
          f"{np.percentile(ht,50):7.1f}/{np.percentile(ht,99):7.1f} "
          f"{100*(nb>0).mean():6.2f}% {100*(nc>0).mean():6.2f}%")
