"""Which samples have sumw_records, and how do they compare to the sidecar?"""
import glob, json, re
from pathlib import Path
import pyarrow.parquet as pq

OUT="outputs/hww_combine_fixed/2022postEE"
sidecar=json.load(open("analysis/filesets/sumw_2022postEE.json"))

def records(sample):
    ds=glob.glob(f"{OUT}/{sample}_*/sumw_records")+glob.glob(f"{OUT}/{sample}/sumw_records")
    ds=[d for d in ds if re.fullmatch(rf"{re.escape(sample)}(_\d+)?", Path(d).parent.name)]
    fs=[f for d in ds for f in glob.glob(f"{d}/*.parquet")]
    if not fs: return None
    return sum(float(sum(pq.read_table(f,columns=["sumw"])["sumw"].to_pylist())) for f in fs)

miss=[]; ok=[]
for s in sorted(sidecar):
    r=records(s)
    if r is None or r==0: miss.append(s)
    else: ok.append((s, r, sidecar[s], r/sidecar[s]))

print(f"HAVE sumw_records: {len(ok)}     MISSING: {len(miss)}\n")
print("--- ratio records/sidecar, sorted (worst first) ---")
for s,r,sc,ra in sorted(ok, key=lambda t:abs(t[3]-1), reverse=True)[:18]:
    flag="  <-- differs >1%" if abs(ra-1)>0.01 else ""
    print(f"  {s:28s} {r:11.4e} / {sc:11.4e} = {ra:6.4f}{flag}")
print(f"\n--- MISSING sumw_records ({len(miss)}) ---")
for s in miss: print("  ", s)
