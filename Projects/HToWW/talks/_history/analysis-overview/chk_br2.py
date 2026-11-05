import glob, json, sys, uproot

fs = '/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json'
d = json.load(open(fs))
cands = [k for k in d if 'TT' in k or 'WtoLNu' in k or 'DY' in k]
print("candidate samples:", cands[:6])
url = None
for k in cands:
    v = d[k]
    files = v.get('files') if isinstance(v, dict) else v
    lst = list(files.keys()) if isinstance(files, dict) else files
    for u in lst:
        if 'maite' not in u:
            url, samp = u, k
            break
    if url: break
print("sample:", samp)
print("url:", url)
f = uproot.open(url)["Events"] if ":" not in url[8:] else uproot.open(url)
keys = set(f.keys())
want = ["Muon_pt","Muon_eta","Muon_pfRelIso03_all","Muon_miniPFRelIso_chg",
        "Muon_miniPFRelIso_all","Muon_jetNDauCharged","Muon_jetPtRelv2",
        "Muon_jetIdx","Muon_jetRelIso","Muon_sip3d","Muon_dxy","Muon_dz",
        "Muon_segmentComp","Muon_mvaTTH",
        "Electron_mvaIso","Electron_jetNDauCharged","Electron_jetPtRelv2",
        "Electron_jetRelIso","Electron_mvaTTH","Electron_sip3d",
        "Jet_btagDeepFlavB"]
print("\n%-32s %s" % ("BRANCH","PRESENT"))
miss=[]
for w in want:
    ok = w in keys
    if not ok: miss.append(w)
    print("%-32s %s" % (w, "YES" if ok else "*** MISSING ***"))
print("\nMISSING COUNT:", len(miss), miss)
