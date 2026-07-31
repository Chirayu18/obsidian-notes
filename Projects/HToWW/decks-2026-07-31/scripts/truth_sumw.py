"""Ground truth: sum genEventSumw from the NanoAOD Runs tree over all 80 signal files."""
import json, uproot, sys

FS = "analysis/filesets/fileset_2022postEE_nanov12_lxplus.json"
d = json.load(open(FS))
v = d["HplusCharm_HtoWW"]
files = v["files"] if isinstance(v, dict) and "files" in v else v
files = list(files.keys()) if isinstance(files, dict) else list(files)
print(f"{len(files)} files")

tot = 0.0; nok = 0; bad = []
for i, f in enumerate(files):
    try:
        with uproot.open(f + ":Runs") as r:
            tot += float(r["genEventSumw"].array(library="np").sum())
        nok += 1
    except Exception as e:
        bad.append((f.split("/")[-1], str(e)[:60]))
    if (i + 1) % 20 == 0:
        print(f"  {i+1}/{len(files)}  running total {tot:.6e}", flush=True)

print(f"\nTRUE genEventSumw (Runs tree, {nok}/{len(files)} files) = {tot:.6e}")
if bad:
    print(f"  FAILED {len(bad)}:")
    for b in bad[:5]: print("   ", b)
print()
print(f"  sumw_records = 7.822690e+04   ratio truth/records = {tot/7.822690e+04:.4f}")
print(f"  sidecar json = 9.265575e+04   ratio truth/sidecar = {tot/9.265575e+04:.4f}")
