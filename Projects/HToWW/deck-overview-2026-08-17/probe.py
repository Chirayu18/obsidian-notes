import json, random, uproot, time, re, collections
FS="/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
d=json.load(open(FS))
random.seed(1)
hosts=collections.Counter()
ok=fail=0
for s in ("WtoLNu_2Jets_0J","WtoLNu_2Jets_1J","WtoLNu_2Jets_2J"):
    for u in random.sample(d[s], 5):
        h=re.match(r"root://([^/]+)",u).group(1)
        t0=time.time()
        try:
            n=uproot.open(u, timeout=45)["Events"].num_entries
            dt=time.time()-t0; ok+=1
            print(f"  OK   {dt:5.1f}s  {n:8d} ev  {h}")
        except Exception as e:
            dt=time.time()-t0; fail+=1
            print(f"  FAIL {dt:5.1f}s  {type(e).__name__}  {h}")
        hosts[h]+=1
print(f"\nprobe: {ok} ok, {fail} fail out of {ok+fail}")
