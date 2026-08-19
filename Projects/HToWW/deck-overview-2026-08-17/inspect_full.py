import json
R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets"
d = json.load(open(R + "/fileset_2022postEE_nanov12_lxplus.json.bak_presiteredir"))

def nfiles(v):
    if isinstance(v, dict) and "files" in v:
        return len(v["files"])
    return len(v)

vj = sorted([k for k in d if "DYto2L" in k or "WtoLNu" in k])
print("=== vjets datasets in FULL fileset ===")
for k in vj:
    print("  %-32s %4d files" % (k, nfiles(d[k])))
print("  TOTAL vjets files:", sum(nfiles(d[k]) for k in vj))

print("\n=== ALL dataset names (to confirm the negrw substring gate) ===")
for k in sorted(d):
    mark = "  <-- VJETS" if k in vj else ""
    print("  %s%s" % (k, mark))

print("\n=== gate check: which datasets match negrw.datasets [DYto2L, WtoLNu] ===")
pats = ["DYto2L", "WtoLNu"]
for k in sorted(d):
    if any(p in k for p in pats):
        print("   MATCH:", k)
