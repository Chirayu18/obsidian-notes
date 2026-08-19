import pyarrow.parquet as pq
D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
for s in ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]:
    m = pq.ParquetFile(D + "/mva/" + s + ".parquet")
    n = m.schema.names
    ng = "weight_negrw" in n
    sc = sum(1 for c in n if c.startswith("mva_score_"))
    print("%-22s rows=%d negrw=%s scores=%d" % (s, m.metadata.num_rows, ng, sc))
m = pq.ParquetFile(D + "/CMS_scale_j_2022Up/mva/WtoLNu_2Jets.parquet")
n = m.schema.names
print("shift WtoLNu scale_j_Up: negrw=%s scores=%d rows=%d" %
      ("weight_negrw" in n, sum(1 for c in n if c.startswith("mva_score_")), m.metadata.num_rows))
