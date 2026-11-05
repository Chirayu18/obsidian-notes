import uproot, numpy as np, awkward as ak
files={
 "0J":"root://cms-xrd-global.cern.ch//store/mc/Run3Summer22EENanoAODv12/WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v3/2560000/3d1c47c6-c80e-4905-80de-ffd344fedf46.root",
}
for tag,url in files.items():
    f=uproot.open(url)["Events"]
    ks=set(f.keys())
    print(f"=== {tag}  nEvents={f.num_entries}")
    for b in ["LHE_Vpt","LHE_Njets","LHE_HT","genWeight"]:
        print(f"   {b:12s}", "YES" if b in ks else "MISSING")
    a=f.arrays(["LHE_Vpt","LHE_Njets","genWeight"],entry_stop=200000)
    v=ak.to_numpy(a["LHE_Vpt"]); nj=ak.to_numpy(a["LHE_Njets"]); w=ak.to_numpy(a["genWeight"])
    print(f"   LHE_Vpt: min={v.min():.1f} max={v.max():.1f} frac<100={100*(v<100).mean():.2f}%")
    print(f"   LHE_Njets values: {np.unique(nj)}")
    neg=(w<0).mean()
    print(f"   negative-weight fraction: {100*neg:.2f}%")
    print(f"   n_eff/N for this file: {(w.sum()**2/ (w**2).sum())/len(w):.4f}")
