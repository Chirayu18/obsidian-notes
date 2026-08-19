import json, glob, os, shutil, datetime

D = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets"
cur = f"{D}/fileset_2022postEE_nanov12_lxplus.json"
baks = sorted(glob.glob(f"{cur}.bak_2*"))
print("backups found:", [os.path.basename(b) for b in baks])
bak = baks[-1]
print("using backup:", os.path.basename(bak))

new = json.load(open(cur))       # the 3 W+jets samples just built
old = json.load(open(bak))       # everything that was there before
print(f"new(3 wjets)={len(new)}  old={len(old)}")
print("old keys:", sorted(old))

merged = dict(old)
merged.pop("WtoLNu_2Jets", None)          # drop the replaced inclusive
merged.update(new)                        # add the three jet-binned

shutil.copy2(cur, cur + ".onlywjets_" + datetime.datetime.now().strftime("%H%M%S"))
json.dump(merged, open(cur, "w"), indent=4, sort_keys=True)

d = json.load(open(cur))
print(f"\nMERGED: {len(d)} samples, {sum(len(v) for v in d.values())} files")
for k in sorted(d):
    print(f"  {k:32s} {len(d[k]):6d}")
print("\ninclusive removed:", "WtoLNu_2Jets" not in d)
print("all three present:", all(f"WtoLNu_2Jets_{j}" in d for j in ("0J","1J","2J")))
