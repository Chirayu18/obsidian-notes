import glob, os, pyarrow.parquet as pq

B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
print("=== structure of finished 0J partitions ===")
dirs = sorted(glob.glob(f"{B}/WtoLNu_2Jets_0J_*"))
print("n partition dirs:", len(dirs))
withbase = [d for d in dirs if os.path.isdir(f"{d}/base")]
print("dirs WITH base/ (surviving events):", len(withbase))
print("dirs with ONLY sumw_records      :", len(dirs) - len(withbase))

# total sumw and event counts across finished partitions
tot_sumw = 0.0; tot_rows = 0; nfiles = 0
for d in dirs:
    for f in glob.glob(f"{d}/sumw_records/*.parquet"):
        t = pq.read_table(f); nfiles += 1
        cols = t.column_names
        if "sumw" in cols:
            tot_sumw += sum(t.column("sumw").to_pylist())
        tot_rows += t.num_rows
print(f"\nsumw_record files: {nfiles}  rows: {tot_rows}")
print(f"total sumw so far: {tot_sumw:,.1f}")
if nfiles:
    t = pq.read_table(glob.glob(f"{dirs[0]}/sumw_records/*.parquet")[0])
    print("sumw_records columns:", t.column_names)
    print(t.to_pandas().head(3).to_string())

# surviving events
print("\n=== surviving events in base/ ===")
n = 0
for d in withbase[:200]:
    for f in glob.glob(f"{d}/base/*.parquet"):
        n += pq.ParquetFile(f).metadata.num_rows
print("rows in base/ so far:", n)
if withbase:
    f = glob.glob(f"{withbase[0]}/base/*.parquet")[0]
    t = pq.read_table(f)
    print("\nbase columns (first 25):", t.column_names[:25])
    print("has weight_negrw:", "weight_negrw" in t.column_names)
    print("has weight_negrw_std:", "weight_negrw_std" in t.column_names)
