import json, re, shutil, datetime
FS="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
BADHOST="xroot01.ncg.ingrid.pt"
d=json.load(open(FS))
bak=FS+".bak_pre_ncg_"+datetime.datetime.now().strftime("%H%M%S"); shutil.copy2(FS,bak)
targets=[(s,i,u) for s in d for i,u in enumerate(d[s]) if BADHOST in u]
print(f"files on {BADHOST}: {len(targets)}")
from rucio.client.replicaclient import ReplicaClient
rc=ReplicaClient()
BADRSE={"T3_US_Rutgers","T2_KR_KISTI","T2_UA_KIPT","T2_PT_NCG_Lisbon"}
fixed=kept=0
for s,i,u in targets:
    lfn=re.search(r"(/store/.*)$",u).group(1)
    got=None
    for r in rc.list_replicas([{"scope":"cms","name":lfn}], schemes=["root"]):
        for rse,urls in r.get("rses",{}).items():
            if rse not in BADRSE and urls:
                got=urls[0]; break
    if got: d[s][i]=got; fixed+=1
    else: kept+=1
print(f"repointed {fixed}, kept {kept}")
old=json.load(open(bak))
assert all(len(d[k])==len(old[k]) for k in old), "COUNT CHANGED"
json.dump(d,open(FS,"w"),indent=4,sort_keys=True)
d2=json.load(open(FS))
print("remaining on bad host:", sum(1 for s in d2 for u in d2[s] if BADHOST in u))
print("total files:", sum(len(v) for v in d2.values()))
