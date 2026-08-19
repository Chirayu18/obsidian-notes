"""Estimate loose-WP acceptance from the UNTAGGED nocjet tree (2022postEE).

hww_2dcat_nocjet has no c-tag applied, so its cjet_cand_* columns hold the raw
CvL/CvB of the leading-CvL good jet. Applying the two WPs offline to that same
sample gives a like-for-like loose-vs-medium efficiency ratio -- no new processing.
"""
import glob, os
import numpy as np
import pyarrow.parquet as pq

BASE = "/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet/2022postEE"
MED = (0.160, 0.304)
LOO = (0.054, 0.182)
COLS = ["cjet_cand_cvsl_pnet", "cjet_cand_cvsb_pnet"]

cvsl, cvsb = [], []
nf = 0
for p in glob.glob(BASE + "/HplusCharm_HtoWW*/base/*.parquet"):
    try:
        t = pq.read_table(p, columns=COLS)
    except Exception:
        continue
    cvsl.append(t[COLS[0]].to_numpy(zero_copy_only=False))
    cvsb.append(t[COLS[1]].to_numpy(zero_copy_only=False))
    nf += 1

if not cvsl:
    raise SystemExit("no parquets read")

cvsl = np.concatenate(cvsl).astype(float)
cvsb = np.concatenate(cvsb).astype(float)
n = len(cvsl)

# -1 sentinel = no c-jet candidate / PNet undefined
real = (cvsl >= 0) & (cvsb >= 0)
med = real & (cvsl > MED[0]) & (cvsb > MED[1])
loo = real & (cvsl > LOO[0]) & (cvsb > LOO[1])

print("H+c signal, 2022postEE, untagged tree (%d parquets)" % nf)
print("  total events (>=1 good jet) : %s" % format(n, ","))
print("  with real CvL/CvB           : %s (%.1f%%)" % (format(int(real.sum()), ","), 100 * real.mean()))
print()
print("  %-14s %10s %10s" % ("WP", "N", "eff of base"))
print("  " + "-" * 36)
print("  %-14s %10s %9.1f%%" % ("medium", format(int(med.sum()), ","), 100 * med.mean()))
print("  %-14s %10s %9.1f%%" % ("loose", format(int(loo.sum()), ","), 100 * loo.mean()))
print("  %-14s %10s %9.1f%%" % ("no tag", format(n, ","), 100.0))
print()
if med.sum():
    print("  loose / medium signal ratio = %.2fx" % (loo.sum() / med.sum()))
    print("  notag / medium signal ratio = %.2fx" % (n / med.sum()))
