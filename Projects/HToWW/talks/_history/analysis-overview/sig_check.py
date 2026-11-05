"""Is the sidecar or sumw_records right for HplusCharm? Compare to the raw genWeight sum."""
import glob, json
import pyarrow.parquet as pq

D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
S = "HplusCharm_HtoWW"

rec = 0.0; nrec = 0
for f in glob.glob(f"{D}/{S}_*/sumw_records/*.parquet"):
    rec += float(sum(pq.read_table(f, columns=["sumw"])["sumw"].to_pylist())); nrec += 1

meta = 0.0; nmeta = 0
for f in glob.glob(f"{D}/parquets_{S}/base/*.parquet"):
    m = pq.ParquetFile(f).schema_arrow.metadata
    if m and m.get(b"sumw"):
        meta += float(m[b"sumw"]); nmeta += 1

sc = json.load(open("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/"
                    "higgscharm/analysis/filesets/sumw_2022postEE.json"))[S]

print(f"sumw_records  : {rec:.6e}   ({nrec} record files)")
print(f"shard metadata: {meta:.6e}   ({nmeta} shards)")
print(f"sidecar json  : {sc:.6e}")
print(f"\nrecords/sidecar = {rec/sc:.4f}   meta/sidecar = {meta/sc:.4f}   records/meta = {rec/meta if meta else float('nan'):.4f}")
