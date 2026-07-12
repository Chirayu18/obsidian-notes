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
# Append 2D-CTAG category column to the MVA-input parquets (idempotent, atomic writes).
# Script: /eos/user/c/cgupta/HToWW/b-hive/scripts/append_ctag2d.py
micromamba activate b_hive
python3 /eos/user/c/cgupta/HToWW/b-hive/scripts/append_ctag2d.py \
    /eos/home-c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE
# add --dry-run to preview. Builds cjet_cand_ctag_2d_cat (int8, 0..10, no nulls) from
# cjet_cand_cvsl_pnet / cjet_cand_cvsb_pnet using official SFbc-2D frozen edges.
```

---

## Tasks

- [x] Verify B is recoverable from CvsL/CvsB (done 2026-07-12 — see finding below)
- [x] Write append script for 2D-CTAG category column (`b-hive/scripts/append_ctag2d.py`)
- [x] Append `cjet_cand_ctag_2d_cat` to all 57 files in `hww_combine_fixed/2022postEE`
      (8.1M rows, zero nulls, range 0..10 — verified)
- [x] Store category as **11 one-hot columns** `cjet_cand_ctag2d_{L0..B4}` (int8 0/1) + keep the
      int `cjet_cand_ctag_2d_cat`. Appended to all 57 files (verified: every row sums to 1).
- [x] New training config `config/HPlusCHToWW_2dcats.yml` = multiclass config with the raw PNet
      `cvsl`/`cvsb` scores **removed** and the 11 one-hot features **added** (replacement, per plan).
- [x] New driver `train_v11_2dcats.sh` (copy of `train_v11.sh`, all versions suffixed `_2dcats`
      so it won't clobber baseline v11 outputs/caches). Both in `b-hive/` on lxplus + vault copy.
- [x] First submit **9071501** FAILED at Step 1a (DatasetConstructorTask, ~142s):
      `ValueError: key "cjet_cand_ctag2d_L0" does not exist (not in record)`.
      **Root cause:** training reads from `hww_combine_fixed/<year>/mva_labeled/{train,test}/`
      (output of make_mva_labeled.py + split_train_test.py), NOT the top-level parquets I'd
      appended to. Those labeled/split copies (all 3 years: 2022postEE, 2022preEE, 2023preBPix)
      had 0 one-hot cols. **Fix:** ran `append_ctag2d.py` on all 6 mva_labeled dirs (train+test ×
      3 years, 38 files, 4.08M rows) — verified 11 one-hot present, every row sums to 1, no nulls.
      (Recomputes from the still-present cjet_cand_cvsl/cvsb, so no re-labeling/re-split needed.)
      Removed the empty partial dataset dir so law re-runs clean.
- [x] **Retrain re-submitted** (H100 GPU) — cluster **9071502.0**, 2026-07-12 02:17.
      Same batch path: `submitter_mva_2dcats.sub` → `job_mva_2dcats.sh` (cd b-hive, activate
      b_hive, source setup.sh, law index, `./train_v11_2dcats.sh`). 5-step law chain.
      Output → `output/TrainingTask/HPlusCHToWW_2dcats/hwwcom_multiclass_v11_2dcats/`.
- [ ] Compare ROC vs baseline `HPlusCHToWW_multiclass / hwwcom_multiclass_v11` once done.
- [ ] Repeat append for `2023preBPix` once ready (other year present in hww_combine_fixed).

### How the MVA is trained (batch recipe, from AFS)
Production trains on **HTCondor with an H100 GPU** via `~/submitter_mva.sub` → `~/job_mva.sh`.
For the 2D-cats variant I added parallel files (don't touch the originals):
- `~/job_mva_2dcats.sh` — runs `./train_v11_2dcats.sh` (rest identical to `job_mva.sh`).
- `~/submitter_mva_2dcats.sub` — H100 / AlmaLinux9, `+JobFlavour="nextweek"`, separate log names.
- Submit: `condor_submit ~/submitter_mva_2dcats.sub`. Monitor: `condor_q <cluster>`;
  logs `~/job_2dcats.<cluster>.{out,err,log}`.
Both files also copied to this vault folder.

### Column layout written to each parquet
- `cjet_cand_ctag_2d_cat` — int8, 0..10 (L0,C0,C1,C2,C3,C4,B0,B1,B2,B3,B4), no nulls. Diagnostics/SF.
- `cjet_cand_ctag2d_L0 … cjet_cand_ctag2d_B4` — 11× int8 one-hot (exactly one =1 per row). **MVA input.**
- The MVA (`HPlusCHToWW_2dcats.yml`) uses ONLY the 11 one-hot cols; raw PNet scores are dropped.

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

