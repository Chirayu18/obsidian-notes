---
tags:
  - hww
status: active
pinned: false
related:
date: 2026-07-11
---

# Untitled

> `BUTTON[toggle-status, toggle-pin]`  `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

---

## Commands

```bash

```

---

## Tasks

- [ ] Implement WP 

---

## Log
- [gitlab file with working points](https://gitlab.cern.ch/cms-analysis/general/HiggsDNA/-/blob/master/higgs_dna/metaconditions/Era2022_v1.json?ref_type=heads#L567-645)
- [Here](https://etsai.web.cern.ch/2DCalibration/SFbc-2D/docs.html) is the documentation for 2024, which is in terms of code and method identical.
- this is the order of argument for the evaluation:

`evaluator.evaluate( "central", nth_jet_hFlav, wp_evaluate, nth_jet_abs_eta, nth_jet_pt, )`

- Idea of this 2d phase tagging method here: /home/cgupta/mnt/lxplus-eos/HToWW/ctag.py
- Plan is to replace the current ctag variables with these ones. To be added in the processing step later. A quick script for now that appends these columns in the parquets should do. Then retrain both versions of MVA and hopefully not much difference in the results. Refer to this for running framework: https://github.com/Chirayu18/higgscharm/blob/migration-v2/QUICKSTART.md 

---

## Key finding (2026-07-12): no reprocessing needed — B is recoverable from CvsL/CvsB

`ctag.py` was written against Saranya's `hplusc/base` parquets, which store four columns
(`jet_btagPNetB`, `jet_btagPNetCvB`, `jet_btagPNetCvL`, `jet_hadronFlavour`). **My `hww` parquets
do not store the raw B score** — they only have `cjet_cand_cvsl_pnet`, `cjet_cand_cvsb_pnet`
(+ `cjet_cand_flavour` for truth), same for `leadingjet_*`. See schema:
`/eos/home-c/cgupta/higgscharm/outputs/hww/2022postEE/*/base/*.parquet`.

**But B does not need to be stored — it is exactly recoverable from CvL and CvB.**
CMS PNet AK4 discriminants share one 3-simplex (b, c, L≡uds+g):
- `CvsL = P_c/(P_c+P_L)`, `CvsB = P_c/(P_c+P_b)`, `BvsAll = P_b` (= `P_b/(P_b+P_c+P_L)`).
- 3 eqns (CvL, CvB, ΣP=1), 3 unknowns ⇒ unique solution:

  ```
  B = CvL·(CvB−1) / (CvB·CvL − CvB − CvL)
  ```

- The two 2D-tagging coordinates then reduce to functions of only the stored columns:

  ```
  pBvsC  = 1 − CvB
  pB+C   = CvL / (CvL + CvB·(1 − CvL))      # = B + (1−B)·CvL, algebraically
  ```

**Verified 3 ways:**
1. Symbolic (sympy): unique closed form.
2. Synthetic (2M random valid triplets): max |B_rec − B| = 4e-16 (machine precision).
3. Real data (30k jets, `Jet_btagPNet*` from a Run3Summer22 NanoAODv12 DY file via xrootd):
   median |B_rec − B| = 2.8e-5, 95pct = 1.4e-4, max = 4.6e-4 — consistent with NanoAOD
   float-storage rounding only (a gluon-class mismatch would give O(0.1–1) errors, not O(1e-5)).

**Consequence:** the "quick script that appends columns" can compute the 2D categories directly
from `cjet_cand_cvsl_pnet` / `cjet_cand_cvsb_pnet` (and `leadingjet_*`) — no B storage, no
reprocessing of NanoAOD. Truth label for optimizing the bins = `cjet_cand_flavour`
(0=light, 4=c, 5=b), which is already present.

