"""Three sumw sources compared: sumw_records (truth) vs parquet shard metadata vs sidecar json."""
import glob, json, re
from pathlib import Path
import pyarrow.parquet as pq

OUT = "outputs/hww_combine_fixed/2022postEE"
sidecar = json.load(open("analysis/filesets/sumw_2022postEE.json"))

def records(sample):
    rec_dirs = glob.glob(f"{OUT}/{sample}_*/sumw_records") + glob.glob(f"{OUT}/{sample}/sumw_records")
    rec_dirs = [d for d in rec_dirs
                if re.fullmatch(rf"{re.escape(sample)}(_\d+)?", Path(d).parent.name)]
    files = [f for d in rec_dirs for f in glob.glob(f"{d}/*.parquet")]
    if not files:
        return None
    return sum(float(sum(pq.read_table(f, columns=["sumw"])["sumw"].to_pylist())) for f in files)

def shardmeta(sample):
    t = 0.0
    for f in glob.glob(f"{OUT}/parquets_{sample}/base/*.parquet"):
        m = pq.ParquetFile(f).schema_arrow.metadata
        if m and m.get(b"sumw"):
            t += float(m[b"sumw"])
    return t

print(f"{'sample':24s} {'sumw_records':>13s} {'shard-meta':>13s} {'sidecar':>13s}  {'rec/meta':>8s} {'rec/side':>8s}")
for s in ["DYto2L_2Jets_50", "WtoLNu_2Jets", "DYto2L_2Jets_10to50",
          "TTto2L2Nu", "TbarQto2Q", "TbarWplusto4Q", "WW", "WWZ"]:
    r = records(s); m = shardmeta(s); sc = sidecar.get(s)
    rs = f"{r:13.4e}" if r else "         None"
    ms = f"{m:13.4e}" if m else "         None"
    ss = f"{sc:13.4e}" if sc else "         None"
    rm = f"{r/m:8.2f}" if (r and m) else "       -"
    rsd = f"{r/sc:8.3f}" if (r and sc) else "       -"
    print(f"{s:24s} {rs} {ms} {ss} {rm} {rsd}")
