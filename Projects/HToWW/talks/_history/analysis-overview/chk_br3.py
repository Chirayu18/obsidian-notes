import json, uproot
fs='/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json'
d=json.load(open(fs))
ks=list(d.keys()); print("n keys:",len(ks)); print("sample keys:",ks[:10])
