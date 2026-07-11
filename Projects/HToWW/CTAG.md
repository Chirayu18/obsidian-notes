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

---

## Official 2D calibration scheme (AN-25-222 / SFbc-2D docs)

Docs page (CERN SSO): https://etsai.web.cern.ch/2DCalibration/SFbc-2D/docs.html — snapshotted PDF
committed at `References/HToWW/2D-SFbc-calibration-AN-25-222.pdf`. **Use the official frozen
edges below so the published SFs apply** (don't invent our own edges as `ctag.py` does — that
re-randomizes bins each run and would break SF lookup).

**Axes & discriminator definitions** (from docs, tagger = **UParT v2**, NanoAODv15):
- x-axis **HFvLF** = score(HF vs LF) = `(B + C) / (B + C + S + UDG)` where
  `B = (1 − CvB)·C / CvB`, `C = CvL·(S+UDG)/(1 − CvL)` (UParT raw probs).
- y-axis **BvC** = score(B vs C) = `1 − btagUParTAK4CvB`.

**Frozen bin edges (latest, 2026.06.29):**
```
HFvLF (x): [0.0, 0.250, 0.452, 0.808, 1.000]                              # 4 columns: L/C0, C1, ... , HF band
BvC   (y): [0.0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.000]  # 8 rows
```
**Categories:** L0, C0, C1, C2, C3, C4, B0, B1, B2, B3, B4 (11). These are the `wp` argument in
`evaluate("central", hadronFlavour, wp, abs_eta, pt)`. SF json (2024):
`/eos/cms/store/group/phys_top/Run3Vcb/flavTagSFs/20260428/flavTaggingSF_2024.json.gz`
(2025 also available under same dir, "very preliminary").

### Mapping onto our stored PNet scores
Both axes are functions of the stored `cvsl` (CvL) and `cvsb` (CvB) via the recovered
3-simplex (see finding above):
```
BvC  (y) = 1 − CvB
HFvLF(x) = P_b + P_c = 1 − P_L,   P_L = CvB·(CvL−1)/(CvB·CvL − CvB − CvL)
         = CvL / (CvL + CvB·(1 − CvL))          # equals pB+C
```
Apply the **official frozen edges** above to these two axes and assign the 11 categories
(L0,C0–C4,B0–B4) as an integer `ctag_2d_cat` column appended to each parquet.

