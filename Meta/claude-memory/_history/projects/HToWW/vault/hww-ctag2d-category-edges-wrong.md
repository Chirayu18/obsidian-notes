---
name: hww-ctag2d-category-edges-wrong
description: "HToWW analysis/corrections/ctag2d.py uses one hard-coded set of 2D category edges that do NOT match the official per-era PNet HPC_ctag_WPs (HiggsDNA); found 2026-10-23, not yet fixed"
metadata:
  node_type: memory
  type: project
  originSessionId: fa3f94a0-dcf2-4e38-9258-aa10947cdbbd
  modified: 2026-10-23T14:12:09.231Z
---

In the live HToWW repo (`higgscharm_thomas_new/higgscharm`, commit 5174c7c, 2026-08-12),
`analysis/corrections/ctag2d.py` lines 29-30 hard-code
`X_HFVLF_EDGES=[0,0.250,0.452,0.808,1]` and `Y_BVC_EDGES=[0,0.006,0.017,0.055,0.761,0.944,0.985,0.995,1]`
for all eras. The official HiggsDNA `Era2022_v1.json` `HPC_ctag_WPs` (PNet) give
b+c edges 0.16/0.332/0.706 and b-vs-c edges 0.036/0.09/0.261/0.799/0.933/0.978/0.993 (2022preEE),
and they differ per era. So the SF category lookup lands jets in the wrong WP bin.
Saranya (HcZZ fork, README_HcZZ.md) found this when porting the file and says the old edges are 2024 UParT ones.
Her fixed `BOUNDARIES_BY_ERA` matches HiggsDNA exactly.
The code comment says the edges "mirror the analysis MVA one-hot binning", so they may be right for the MVA features but wrong for the SF lookup.

**Why:** it biases the CMS_ctag2d central SF and its nuisance, see [[Meta/claude-memory/_history/projects/HToWW/vault/hww-ctag2d-sf-total-decision|hww-ctag2d-sf-total-decision]].
**How to apply:** check this before any new HToWW card or production; the fix is per-era edges from HPC_ctag_WPs.
