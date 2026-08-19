#!/usr/bin/env python3
"""Merge the fresh vjets re-run shards (with weight_negrw) into the per-sample combine
inputs the histogram-maker reads:
    <sample>.parquet                    <- base/*.parquet  (nominal, has weight_negrw)
    <shift>{Up,Down}/<sample>.parquet   <- base/<shift>/*.parquet  (12 object shifts)

Only the 3 vjets samples. sumw_records excluded. Backs up any existing target first.
"""
import glob, os, shutil, sys
import pandas as pd
import pyarrow.parquet as pq

D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
SAMPLES = ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]
SHIFTS = ["CMS_scale_j_2022Up", "CMS_scale_j_2022Down",
          "CMS_res_j_2022Up", "CMS_res_j_2022Down",
          "CMS_scale_e_2022Up", "CMS_scale_e_2022Down",
          "CMS_res_e_2022Up", "CMS_res_e_2022Down",
          "CMS_scale_m_2022Up", "CMS_scale_m_2022Down",
          "CMS_res_m_2022Up", "CMS_res_m_2022Down"]

def merge(shards, dst, expect_negrw):
    if not shards:
        return None
    df = pd.concat([pd.read_parquet(f) for f in shards], ignore_index=True)
    has = "weight_negrw" in df.columns
    if expect_negrw and not has:
        sys.exit(f"FATAL: {dst} has no weight_negrw column!")
    # back up existing target once
    if os.path.exists(dst) and not os.path.exists(dst + ".bak_pre_negrw"):
        shutil.copy2(dst, dst + ".bak_pre_negrw")
    df.to_parquet(dst)
    return len(df), has

for s in SAMPLES:
    # nominal
    base = [f for f in glob.glob(f"{D}/{s}_*/base/*.parquet") if "sumw_records" not in f]
    r = merge(base, f"{D}/{s}.parquet", expect_negrw=True)
    print(f"{s:24s} NOMINAL  shards={len(base):4d} -> rows={r[0]:6d}  weight_negrw={r[1]}")
    # shifts
    for sh in SHIFTS:
        shards = glob.glob(f"{D}/{s}_*/base/{sh}/*.parquet")
        os.makedirs(f"{D}/{sh}", exist_ok=True)
        r = merge(shards, f"{D}/{sh}/{s}.parquet", expect_negrw=True)
        if r:
            print(f"    {sh:22s} shards={len(shards):4d} -> rows={r[0]:6d}  negrw={r[1]}")
        else:
            print(f"    {sh:22s} NO SHARDS")
print("\nMERGE DONE")
