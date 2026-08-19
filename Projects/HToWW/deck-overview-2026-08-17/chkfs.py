import json
p = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
d = json.load(open(p))
print("samples in fileset:", len(d))
tot = 0
for k in sorted(d):
    n = len(d[k]); tot += n
    print(f"  {k:30s} {n:6d} files")
print("total files:", tot)
exp = {"WtoLNu_2Jets_0J": 3432, "WtoLNu_2Jets_1J": 2669, "WtoLNu_2Jets_2J": 2135}
ok = True
for k, v in exp.items():
    got = len(d.get(k, []))
    good = got == v
    ok &= good
    print(f"  CHECK {k}: got {got} expected {v} -> {'OK' if good else 'MISMATCH'}")
print("\nALL COUNTS OK" if ok else "\n*** COUNT MISMATCH ***")
u = d.get("WtoLNu_2Jets_0J", [None])[0]
print("sample url:", u)
print("old inclusive present?", "WtoLNu_2Jets" in d)
