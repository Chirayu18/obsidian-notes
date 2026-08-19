import uproot
url="root://cms-xrd-global.cern.ch//store/mc/Run3Summer22EENanoAODv12/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2540000/62aea484-cae5-4c41-8803-08969f44c116.root"
f=uproot.open(url)["Events"]
keys=set(f.keys())
want=["Muon_pt","Muon_eta","Muon_pfRelIso03_all","Muon_miniPFRelIso_chg",
"Muon_miniPFRelIso_all","Muon_jetNDauCharged","Muon_jetPtRelv2","Muon_jetIdx",
"Muon_jetRelIso","Muon_sip3d","Muon_dxy","Muon_dz","Muon_segmentComp","Muon_mvaTTH",
"Electron_pt","Electron_eta","Electron_pfRelIso03_all","Electron_miniPFRelIso_chg",
"Electron_miniPFRelIso_all","Electron_jetNDauCharged","Electron_jetPtRelv2",
"Electron_jetIdx","Electron_jetRelIso","Electron_sip3d","Electron_dxy","Electron_dz",
"Electron_mvaIso","Electron_mvaTTH","Jet_btagDeepFlavB","Jet_btagPNetB"]
miss=[]
print("%-34s %s"%("BRANCH","PRESENT"))
for w in want:
    ok=w in keys
    if not ok: miss.append(w)
    print("%-34s %s"%(w,"YES" if ok else "*** MISSING ***"))
print("\nMISSING:",len(miss),miss)
