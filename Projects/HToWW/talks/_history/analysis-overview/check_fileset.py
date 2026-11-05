import json, sys
R = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets"
base = R + "/fileset_2022postEE_nanov12_lxplus.json"
for tag in ["", ".bak_presiteredir", ".bak_pre_genrw", ".bak_presignal"]:
    p = base + tag
    label = tag if tag else "(live)"
    try:
        d = json.load(open(p))
    except Exception as e:
        print("%-20s -> ERR %s" % (label, e))
        continue
    vj = [k for k in d if "DYto2L" in k or "WtoLNu" in k]
    def nfiles(v):
        if isinstance(v, dict) and "files" in v:
            return len(v["files"])
        if isinstance(v, dict):
            return len(v)
        return len(v)
    tot = sum(nfiles(d[k]) for k in vj)
    print("%-20s datasets=%3d  vjets_datasets=%3d  vjets_files=%5d" % (label, len(d), len(vj), tot))
    if vj and tag == "":
        for k in sorted(vj):
            print("      live vjets: %-30s %d files" % (k, nfiles(d[k])))
