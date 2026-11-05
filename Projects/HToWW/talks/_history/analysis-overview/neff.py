import uproot, numpy as np, awkward as ak, subprocess, json

DS = {
 "0J":  ("/WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3/NANOAODSIM", 55760., 678397952),
 "1J":  ("/WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM", 9529., 522553517),
 "2J":  ("/WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM", 3532., 344572777),
 "INCL":("/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM", 67710., 281543551),
}
print(f"{'samp':5s} {'nev(DAS)':>13s} {'negfrac':>8s} {'neff/N':>7s} {'xsec':>8s} {'eff.lumi/fb':>12s}")
tot_eq = 0.0
for tag,(ds,xs,nev) in DS.items():
    f = subprocess.run(["dasgoclient","-query",f"file dataset={ds}"],
                       capture_output=True,text=True).stdout.split()[0]
    url = "root://cms-xrd-global.cern.ch/" + f
    t = uproot.open(url)["Events"]
    w = ak.to_numpy(t["genWeight"].array(entry_stop=200000))
    negf = (w<0).mean()
    neff_frac = (w.sum()**2/(w**2).sum())/len(w)
    # effective lumi with the n_eff correction folded in
    eqlumi = nev*neff_frac/xs/1000.
    tot_eq += eqlumi if tag!="INCL" else 0.0
    print(f"{tag:5s} {nev:13,d} {100*negf:7.2f}% {neff_frac:7.4f} {xs:8.0f} {eqlumi:12.4f}")
print(f"\njet-binned combined effective lumi: {tot_eq:.4f} /fb")
incl = DS['INCL']
f = subprocess.run(["dasgoclient","-query",f"file dataset={incl[0]}"],capture_output=True,text=True).stdout.split()[0]
w = ak.to_numpy(uproot.open("root://cms-xrd-global.cern.ch/"+f)["Events"]["genWeight"].array(entry_stop=200000))
nf=(w.sum()**2/(w**2).sum())/len(w)
il = incl[2]*nf/incl[1]/1000.
print(f"inclusive        effective lumi: {il:.4f} /fb")
print(f"\nGAIN in effective statistics: {tot_eq/il:.2f}x")
