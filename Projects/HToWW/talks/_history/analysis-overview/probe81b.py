import json, uproot, time, re
R="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
p=json.load(open(f"{R}/condor/hww_combine_2dcat/2022postEE/WtoLNu_2Jets_1J/partitions.json"))
files=list(p["81"].values())[0]
print("files in partition 81:", len(files))
ok=fail=0
for u in files:
    m=re.match(r"root://([^/]+)",u); h=m.group(1) if m else u[:40]
    t0=time.time()
    try:
        n=uproot.open(u, timeout=40)["Events"].num_entries
        print(f"  OK   {time.time()-t0:5.1f}s {n:8d} ev  {h}"); ok+=1
    except Exception as e:
        print(f"  FAIL {time.time()-t0:5.1f}s {type(e).__name__:16s} {h}"); fail+=1
print(f"\n{ok} ok / {fail} fail")
