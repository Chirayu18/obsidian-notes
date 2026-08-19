#!/usr/bin/env python3
"""Merge ONLY the 3 vjets samples into the combine inputs, using the REPO's own
merge_parquet_files (analysis.postprocess.utils) so the sumw/xsec/era metadata
handling matches the rest of the pipeline. Then the caller runs append_ctag2d.py.

Writes exactly the paths the combine histogram-maker reads:
    SAMPLE_DIR/<sample>.parquet                  (nominal, from base/*.parquet)
    SAMPLE_DIR/<shift>/<sample>.parquet          (12 object shifts, from base/<shift>/*.parquet)

Does NOT touch any other sample. Backs up existing targets once.
"""
import glob, os, shutil, sys
from pathlib import Path

sys.path.insert(0, "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
from analysis.postprocess.utils import merge_parquet_files  # the repo's tested merger

import time
D = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE"
# allow restricting to a subset via argv (EOS write/read race aborted the first run
# partway through WtoLNu). Idempotent + backs up once, so re-running is safe.
SAMPLES = sys.argv[1:] or ["DYto2L_2Jets_50", "DYto2L_2Jets_10to50", "WtoLNu_2Jets"]
SHIFTS = ["CMS_scale_j_2022Up", "CMS_scale_j_2022Down",
          "CMS_res_j_2022Up", "CMS_res_j_2022Down",
          "CMS_scale_e_2022Up", "CMS_scale_e_2022Down",
          "CMS_res_e_2022Up", "CMS_res_e_2022Down",
          "CMS_scale_m_2022Up", "CMS_scale_m_2022Down",
          "CMS_res_m_2022Up", "CMS_res_m_2022Down"]

def backup_once(dst):
    if os.path.exists(dst) and not os.path.exists(dst + ".bak_pre_negrw"):
        shutil.copy2(dst, dst + ".bak_pre_negrw")

def do(shards, dst):
    if not shards:
        return None
    backup_once(dst)
    ok = merge_parquet_files(shards, dst)   # repo function: flat concat + sumw aggregation
    if not ok:
        return None
    import pyarrow.parquet as pq
    # EOS can 500 on an immediate footer read right after write -> retry briefly
    last = None
    for _ in range(6):
        try:
            pf = pq.ParquetFile(dst)
            return pf.metadata.num_rows, ("weight_negrw" in pf.schema.names)
        except Exception as e:
            last = e; time.sleep(2)
    raise last

for s in SAMPLES:
    base = [f for f in glob.glob(f"{D}/{s}_*/base/*.parquet") if "sumw_records" not in f]
    r = do(base, f"{D}/{s}.parquet")
    print(f"{s:24s} NOMINAL shards={len(base):4d} -> rows={r[0]:6d} negrw={r[1]}")
    assert r[1], f"{s} nominal missing weight_negrw!"
    for sh in SHIFTS:
        shards = glob.glob(f"{D}/{s}_*/base/{sh}/*.parquet")
        os.makedirs(f"{D}/{sh}", exist_ok=True)
        r = do(shards, f"{D}/{sh}/{s}.parquet")
        if r:
            print(f"    {sh:22s} shards={len(shards):4d} -> rows={r[0]:6d} negrw={r[1]}")
            assert r[1], f"{s}/{sh} missing weight_negrw!"
        else:
            print(f"    {sh:22s} NO SHARDS")
print("\nMERGE DONE (via repo merge_parquet_files)")
