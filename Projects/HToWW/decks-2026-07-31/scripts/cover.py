"""Do the 80 sumw_records tile every file's full event range exactly once?"""
import glob, re, os
from collections import defaultdict
import pyarrow.parquet as pq
from urllib.parse import unquote

D="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
files=glob.glob(f"{D}/HplusCharm_HtoWW_*/sumw_records/*.parquet")
print(f"{len(files)} record files")

per=defaultdict(list); tot=0.0
for f in files:
    b=unquote(os.path.basename(f)[:-8])
    m=re.match(r"(?P<uuid>[0-9a-f-]+)_(?P<tree>.+?)_(?P<lo>\d+)-(?P<hi>\d+)$", b)
    if not m:
        print("  UNPARSED:", b); continue
    s=float(pq.read_table(f,columns=["sumw"])["sumw"][0].as_py())
    tot+=s
    per[m["uuid"]].append((int(m["lo"]), int(m["hi"]), s))

print(f"distinct file UUIDs: {len(per)}")
gaps=0; overlaps=0
for u,segs in per.items():
    segs.sort()
    if segs[0][0]!=0: gaps+=1; print(f"  {u[:8]}: does not start at 0 -> {segs[0][0]}")
    for a,b in zip(segs, segs[1:]):
        if b[0]>a[1]: gaps+=1; print(f"  {u[:8]}: GAP {a[1]}->{b[0]}")
        elif b[0]<a[1]: overlaps+=1; print(f"  {u[:8]}: OVERLAP at {b[0]}")
print(f"\ngaps={gaps} overlaps={overlaps}")
print(f"chunks per file: min={min(len(v) for v in per.values())} max={max(len(v) for v in per.values())}")
print(f"total events covered = {sum(max(h for _,h,_ in v) for v in per.values())}")
print(f"TOTAL sumw = {tot:.6e}")
