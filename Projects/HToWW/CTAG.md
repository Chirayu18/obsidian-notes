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
- [x] Second submit **9071502** was HELD ~3 min in (02:20): *"Job has gone over cgroup memory
      limit of 3000 MB. Last measured usage: 4227 MB."* (Code 34.102). The submitter had no
      `request_memory`, so it defaulted to 3000 MB; DatasetConstructor peaks higher reading the
      big parquets (tt = 3.2M rows). **Fix:** added `request_memory = 16384` (16 GB) to
      `submitter_mva_2dcats.sub`, removed the held job, resubmitted.
- [x] Third submit **9071503** (16 GB) sat IDLE ~2h — never matched. `condor_q -analyze`:
      *"0 slots match … Job did not match any machines' constraints"* (RequestMemory rounded to
      **18000**). H100 slots advertise memory in tiers (12000/18000/24000/…); requiring
      ≥18000 **and** a free H100 GPU **and** AlmaLinux9 over-constrained it — only the large tiers
      qualified, and free H100 GPUs are scarce. **Over-corrected on memory.**
- [x] **Retrain re-submitted with 8 GB** — cluster **9071507.0**, 2026-07-12 05:41; matched in
      ~8 s, ran on b9pgpun102, **finished 06:04:10 (return value 0, no failed tasks).**
      8 GB safely covers the 4.2 GB DatasetConstructor peak while fitting far more H100 slots.
      `submitter_mva_2dcats.sub` sets `request_memory = 8000`. Full 5-step law chain completed.
      **Lesson:** on the H100 pool, request memory ≤ the smallest useful slot tier (≈8–12 GB);
      don't inflate it — it silently blocks matching against the (scarce) GPU slots.

---

## ✅ RESULT — 2D-cat MVA retrain vs baseline (2026-07-12)

Training `hwwcom_multiclass_v11_2dcats` (features = **11 one-hot** `cjet_cand_ctag2d_*`, raw PNet
cvsl/cvsb **removed**) vs baseline `hwwcom_multiclass_v11` (same inputs, raw PNet scores). Both
6-class SimpleMLP_MultiClass, 30 epochs, same cross-era train/test filelists. **Test-set AUC:**

| Discriminant        | 2D-cats (one-hot) | Baseline (raw PNet) | Δ (2D − base) |
|---------------------|-------------------|---------------------|---------------|
| **hplusc_vs_all**   | **0.9322**        | 0.9284              | **+0.0038**   |
| hplusc_vs_higgsbkg  | 0.8302            | 0.8506              | −0.0204       |
| hplusc_vs_tt        | 0.9438            | 0.9375              | +0.0063       |
| hplusc_vs_st        | 0.9334            | 0.9287              | +0.0047       |
| hplusc_vs_diboson   | 0.8855            | 0.8840              | +0.0015       |
| hplusc_vs_vjets     | 0.9425            | 0.9348              | +0.0077       |

**Takeaway:** replacing the two continuous PNet scores with the 11 one-hot 2D-categories is
**≈ equivalent to baseline** — overall hplusc-vs-all AUC is marginally *better* (+0.004), and 4 of
5 background-specific ROCs improve. The one regression is **vs higgs-background (−0.020)**:
separating H+c from other Higgs processes leans on fine charm-tag gradients that the coarse
11-bin scheme discards. Matches the note's hypothesis ("hopefully not much difference"). No
catastrophic loss from discarding the continuous scores.

**AUC source:** `AUC_default_all.npy` in each ROCCurveTask dir (loaded directly).

### Output locations (EOS)
- 2D-cats ROCs (6 PNG+PDF+npy): `…/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/`
- Baseline ROCs: same tree under `HPlusCHToWW_multiclass/hwwcom_v11_train/hwwcom_v11_test/hwwcom_multiclass_v11/…`
- Trained model: `output/TrainingTask/HPlusCHToWW_2dcats/hwwcom_multiclass_v11_2dcats/`
- Full job log: `~/job_2dcats.9071507.0.out` (14188 lines, all 5 law steps).

### Open follow-ups
- If the higgsbkg regression matters, consider the *additive* variant (keep cvsl/cvsb AND the
  one-hot) rather than pure replacement — would recover the fine-gradient info.
- Append one-hot cols + retrain for `2023preBPix` era once ready.
- 2D categories are also SF-ready (official SFbc-2D edges) if/when calibrated SFs are wanted.
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

