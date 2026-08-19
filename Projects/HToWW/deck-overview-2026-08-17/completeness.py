"""How complete is each tree, per key sample? Compares shard counts and event counts
against the baseline, to size what the missing jobs actually cost."""
import glob
import numpy as np, pyarrow.parquet as pq

BASE="/eos/user/c/cgupta/higgscharm/outputs"
Y="2022postEE"
TREES={"baseline":"hww_combine_2dcat","nocjet":"hww_2dcat_nocjet",
       "looseWP":"hww_2dcat_looseWP","v3(nocjet_kin)":"hww_2dcat_nocjet_kin"}
SAMPLES=["HplusCharm_HtoWW","GluGluHto2Wto2L2Nu","TTto2L2Nu"]

print(f"{'tree':<16s} {'sample':<22s} {'shards':>8s} {'events':>12s}")
print("-"*62)
for tname,t in TREES.items():
    for s in SAMPLES:
        fs=sorted(glob.glob(f"{BASE}/{t}/{Y}/{s}/base/*.parquet"))+\
           sorted(glob.glob(f"{BASE}/{t}/{Y}/{s}_*/base/*.parquet"))
        if not fs:
            print(f"{tname:<16s} {s:<22s} {'--':>8s} {'--':>12s}"); continue
        n=0
        for f in fs:
            try: n+=pq.read_metadata(f).num_rows
            except Exception: pass
        print(f"{tname:<16s} {s:<22s} {len(fs):>8d} {n:>12,d}")
    print()
