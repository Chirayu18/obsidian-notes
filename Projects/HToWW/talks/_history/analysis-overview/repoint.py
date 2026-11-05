#!/usr/bin/env python3
"""Repoint fileset entries away from three failing XRootD endpoints.

Uses rucio to find ALL replicas of each affected LFN and picks a healthy one
from the site whitelist. NEVER drops a file: if no good replica exists, the
original URL is kept and reported, so the file count can only stay constant.
"""
import json, re, shutil, datetime, collections, sys

FS = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
BAD_HOSTS = ["ruhex-osgce.rutgers.edu", "cms-t2-se01.sdfarm.kr", "cms-se0.kipt.kharkov.ua"]

d = json.load(open(FS))
bak = FS + ".bak_pre_repoint_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(FS, bak)
print("backup:", bak.split("/")[-1])

def lfn(url):
    m = re.search(r"(/store/.*)$", url)
    return m.group(1) if m else None

# collect the LFNs that need repointing
need = collections.defaultdict(list)
for s in d:
    for i, u in enumerate(d[s]):
        if any(b in u for b in BAD_HOSTS):
            need[s].append((i, lfn(u)))
tot = sum(len(v) for v in need.values())
print(f"files needing repoint: {tot}")
for s, v in need.items():
    print(f"   {s}: {len(v)}")

from rucio.client.replicaclient import ReplicaClient
rc = ReplicaClient()

BADRSE = {"T3_US_Rutgers", "T2_KR_KISTI", "T2_UA_KIPT"}
fixed = kept = 0
for s, items in need.items():
    lfns = [l for _, l in items if l]
    reps = {}
    for chunk_start in range(0, len(lfns), 500):
        chunk = lfns[chunk_start:chunk_start+500]
        dids = [{"scope": "cms", "name": l} for l in chunk]
        for r in rc.list_replicas(dids, schemes=["root"]):
            good = [(rse, u) for rse, urls in r.get("rses", {}).items()
                    for u in urls if rse not in BADRSE]
            if good:
                reps[r["name"]] = good[0][1]
    for idx, l in items:
        if l in reps:
            d[s][idx] = reps[l]; fixed += 1
        else:
            kept += 1

print(f"\nrepointed: {fixed}   kept original (no good replica): {kept}")

old = json.load(open(bak))
assert all(len(d[k]) == len(old[k]) for k in old), "FILE COUNT CHANGED -- aborting"
print("file counts unchanged:", {k: len(v) for k, v in d.items()})
json.dump(d, open(FS, "w"), indent=4, sort_keys=True)

# verify
d2 = json.load(open(FS))
left = sum(1 for s in d2 for u in d2[s] if any(b in u for b in BAD_HOSTS))
print(f"\nremaining URLs on bad hosts: {left}")
print("total files:", sum(len(v) for v in d2.values()))
