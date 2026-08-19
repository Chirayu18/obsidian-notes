import pyarrow.parquet as pq
D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
SAMPLES = ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]
SHIFTS = ["CMS_scale_j_2022Up", "CMS_scale_j_2022Down", "CMS_res_j_2022Up", "CMS_res_j_2022Down",
          "CMS_scale_e_2022Up", "CMS_scale_e_2022Down", "CMS_res_e_2022Up", "CMS_res_e_2022Down",
          "CMS_scale_m_2022Up", "CMS_scale_m_2022Down", "CMS_res_m_2022Up", "CMS_res_m_2022Down"]
bad = 0
ok = 0
for s in SAMPLES:
    paths = [D + "/" + s + ".parquet"] + [D + "/" + sh + "/" + s + ".parquet" for sh in SHIFTS]
    for p in paths:
        try:
            m = pq.ParquetFile(p)
            ng = "weight_negrw" in m.schema.names
            assert ng, p + " no negrw"
            ok += 1
        except Exception as e:
            print("BAD:", p.replace(D + "/", ""), str(e)[:45])
            bad += 1
print("verified %d merged files OK, %d bad" % (ok, bad))
for s in SAMPLES:
    m = pq.ParquetFile(D + "/" + s + ".parquet")
    ng = "weight_negrw" in m.schema.names
    ct = any("ctag2d" in c for c in m.schema.names)
    print("  %-22s rows=%d ncols=%d negrw=%s ctag2d=%s" % (s, m.metadata.num_rows, len(m.schema.names), ng, ct))
