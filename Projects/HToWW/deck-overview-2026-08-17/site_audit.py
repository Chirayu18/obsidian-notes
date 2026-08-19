import json, collections, re

P = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
d = json.load(open(P))
BAD = ["ruhex-osgce.rutgers.edu", "cms-t2-se01.sdfarm.kr", "cms-se0.kipt.kharkov.ua"]

print("=== replica host distribution per sample ===")
for s in sorted(d):
    if not s.startswith("WtoLNu_2Jets_"): continue
    hosts = collections.Counter()
    for u in d[s]:
        m = re.match(r"root://([^/]+)", u)
        hosts[m.group(1) if m else "?"] += 1
    tot = sum(hosts.values())
    nbad = sum(v for k, v in hosts.items() if any(b in k for b in BAD))
    print(f"\n{s}: {tot} files, {nbad} on BAD sites ({100*nbad/tot:.1f}%)")
    for h, n in hosts.most_common(8):
        flag = "  <-- BAD" if any(b in h for b in BAD) else ""
        print(f"    {h:45s} {n:5d}{flag}")
