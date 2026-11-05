import json, uproot, time, re
R="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm"
p=json.load(open(f"{R}/condor/hww_combine_2dcat/2022postEE/WtoLNu_2Jets_1J/partitions.json"))
key = "81" if "81" in p else (81 if 81 in p else None)
files = p[key] if key is not None else None
print("partition 81 files:", len(files) if files else "NOT FOUND")
if files:
    ok=fail=0
    for u in files:
        h=re.match(r"root://([^/]+)",u).group(1)
        t0=time.time()
        try:
            n=uproot.open(u, timeout=40)["Events"].num_entries
            print(f"  OK   {time.time()-t0:5.1f}s {n:8d} ev  {h}"); ok+=1
        except Exception as e:
            print(f"  FAIL {time.time()-t0:5.1f}s {type(e).__name__}  {h}"); fail+=1
    print(f"\n{ok} ok / {fail} fail")
