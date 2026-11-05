import glob, json, sys
import uproot

fs = sorted(glob.glob('/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/*2022postEE*.json'))
print("filesets:", [f.split('/')[-1] for f in fs])
if not fs:
    sys.exit(0)
d = json.load(open(fs[0]))
# find first file url
url = None
for k, v in d.items():
    if isinstance(v, dict):
        files = v.get('files') or v
        if isinstance(files, dict):
            url = list(files.keys())[0]
        elif isinstance(files, list):
            url = files[0]
    elif isinstance(v, list):
        url = v[0]
    if url:
        print("sample:", k)
        break
print("url:", url)
f = uproot.open(url + ":Events" if ':' not in url.split('//')[-1] else url)
keys = set(f.keys())
want = ["Muon_pt","Muon_eta","Muon_pfRelIso03_all","Muon_miniPFRelIso_chg",
        "Muon_miniPFRelIso_all","Muon_jetNDauCharged","Muon_jetPtRelv2",
        "Muon_jetIdx","Muon_jetRelIso","Muon_sip3d","Muon_dxy","Muon_dz",
        "Muon_segmentComp","Muon_mvaTTH",
        "Electron_mvaIso","Electron_jetNDauCharged","Electron_jetPtRelv2",
        "Electron_jetRelIso","Electron_mvaTTH","Jet_btagDeepFlavB"]
print("\n%-32s %s" % ("BRANCH","PRESENT"))
for w in want:
    print("%-32s %s" % (w, "YES" if w in keys else "*** MISSING ***"))
