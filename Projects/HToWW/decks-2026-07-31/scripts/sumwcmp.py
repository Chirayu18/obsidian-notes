import json, glob
import pyarrow.parquet as pq
sc = json.load(open("analysis/filesets/sumw_2022postEE.json"))
print(f"{'sample':22s} {'sidecar':>12s} {'parquet_md':>12s} {'ratio':>7s}")
for s in sorted(sc):
    md = 0.0
    for f in glob.glob(f"outputs/hww_combine_fixed/2022postEE/parquets_{s}/base/*.parquet"):
        m = pq.ParquetFile(f).schema_arrow.metadata
        if m and m.get(b"sumw"):
            md += float(m[b"sumw"])
    r = sc[s] / md if md else float("nan")
    flag = "  <-- undercount" if md and r > 1.5 else ""
    print(f"{s:22s} {sc[s]:12.4e} {md:12.4e} {r:7.3f}{flag}")
