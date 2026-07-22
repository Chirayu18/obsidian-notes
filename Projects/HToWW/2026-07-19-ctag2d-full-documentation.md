---
tags: [reference]
status: active
date: 2026-07-19
source: lxplus
---

# 2D c-tagging (CTAG) — full documentation

Complete write-up of the 2D flavour-tagging categories: derivation, the binning plane,
pipeline integration, MVA retrain results, feature importance, and how to proceed to v32.

Companion notes: [[CTAG]] (running log / task list), [[plots]] (plot links).

---

## 1. What this is

The BTV **SFbc-2D** calibration (AN-25-222) replaces single-cut working points with a
**2D plane** partitioned into 11 categories — `L0, C0–C4, B0–B4` — with *frozen* bin edges,
each carrying its own scale factor. We adopt the same scheme for H+c (H→WW).

**Reference:** `References/HToWW/2D-SFbc-calibration-AN-25-222.pdf`
(snapshot of https://etsai.web.cern.ch/2DCalibration/SFbc-2D/docs.html, CERN SSO).

### The two axes

| axis | definition |
|---|---|
| **BvC** (y) | `1 − CvB` |
| **HFvLF** (x) | `P_b + P_c = 1 − P_L` |

### Frozen bin edges (official, 2026.06.29)

```
HFvLF (x): [0.000, 0.250, 0.452, 0.808, 1.000]
BvC   (y): [0.000, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.000]
```

### Category layout

```
HFvLF < 0.808                 ->  L0 | C0 | C1     (split at 0.250, 0.452; full BvC height)
HFvLF >= 0.808, BvC < 0.055   ->  C4 (BvC<0.006) | C3 (…<0.017) | C2 (…<0.055)
HFvLF >= 0.808, BvC >= 0.055  ->  B0 | B1 | B2 | B3 | B4   (rising BvC, B4 = purest b)
```

Integer ids used everywhere: `L0=0, C0=1, C1=2, C2=3, C3=4, C4=5, B0=6, B1=7, B2=8, B3=9, B4=10`.

---

## 2. Key result: the axes need only CvsL and CvsB

The 2D method as originally sketched needs the raw b-score, which **our parquets never stored**.
It turns out not to matter — `B` is *exactly recoverable*, so no reprocessing was ever needed.

CMS PNet AK4 discriminants share one 3-simplex `(b, c, L≡uds+g)`:

```
CvsL = P_c/(P_c+P_L),   CvsB = P_c/(P_c+P_b),   P_b+P_c+P_L = 1
```

Three equations, three unknowns → unique solution:

```
B = P_b   = CvL·(CvB−1) / (CvB·CvL − CvB − CvL)
HFvLF     = CvL / (CvL + CvB·(1−CvL))          # = P_b + P_c  (equals B + (1−B)·CvL)
BvC       = 1 − CvB
```

**Verified three independent ways:**

| check | result |
|---|---|
| Symbolic (sympy) | unique closed form exists |
| 2M random valid probability triplets | max \|B_rec − B\| = **4×10⁻¹⁶** (machine precision) |
| 30k real jets, `Jet_btagPNetB` from a Run3Summer22 **NanoAODv12** file | median **2.8×10⁻⁵**, 95pct 1.4×10⁻⁴ |

The ~10⁻⁵ residual on real data is NanoAOD float-storage rounding, **not** a modelling gap — a
gluon-class mismatch would show O(0.1–1) errors. So "L" in CvsL lumps `uds+g`, and the recovery
is exact up to storage precision.

---

## 3. The plane, plotted

![[ctag2d_plane_bins.png]]

Plot: `/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.{png,pdf}`
(CERNBox: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/plots/)
Generator: `Projects/HToWW/lxplus-2026-07-12/plot_2dplane_v2.py`

Density = 2022postEE MC (tt + H+c + DY + Single Top + WW), **candidate c-jet**, 845k jets.
Insets zoom the two thin bands (they are invisible at full scale).

### Flavour composition per bin

| cat | N | %b | %c | %l |
|-----|---:|---:|---:|---:|
| L0 | 130,694 | 13.5 | 4.7 | **81.8** |
| C0 | 188,702 | 28.2 | 6.2 | 65.7 |
| C1 | 170,043 | 58.0 | 7.9 | 34.1 |
| C2 | 17,823 | 58.6 | 33.4 | 8.0 |
| C3 | 1,082 | 30.6 | **57.9** | 11.5 |
| C4 | 39 | 15.4 | **74.4** | 10.3 |
| B0 | 336,372 | **89.6** | 7.3 | 3.0 |
| B1–B4 | 0 | — | — | — |

### ⚠️ Important caveat: only 7 of 11 bins are populated

**B1–B4 are always empty for the candidate c-jet**, and C4 is nearly so (39 jets).
Reason: the c-jet *candidate* is already charm-selected, so it sits at high `CvB`, i.e. **low
BvC** — the B1–B4 band (`BvC > 0.761`, i.e. `CvB < 0.239`) is cut away by construction.

Consequences:
- 4 of the 11 one-hot MVA inputs are **identically zero** → dead inputs, no information.
- Charm purity rises correctly C2→C3→C4 (33% → 58% → 74%), so the *ordering* is physical, but
  the high-purity charm bins hold very few jets.
- On the **leading jet** (not charm-selected) the full ladder does populate, and b-purity rises
  monotonically B0→B4: 24 → 75 → 93 → 98 → 100%. So the scheme itself is sound; it is the
  candidate-c-jet selection that truncates it.

**Implication:** for the MVA, the effective information is ~6 non-trivial bins. Consider either
applying the categories to a jet collection that spans the plane, or collapsing B1–B4.

---

## 4. Pipeline integration (new runs get these automatically)

Previously the columns were only *appended after the fact* by a script. They are now produced by
the processor itself, so **any new processing run has them without extra steps**.

### What changed in `higgscharm` (branch `NewWorkflows`, AFS `~/higgscharm`)

| file | change |
|---|---|
| `analysis/utils/ctag2d.py` | **new** — `ctag2d_category`, `ctag2d_onehot`, `ctag2d_axes`, edges + category list |
| `analysis/utils/__init__.py` | export the above |
| `analysis/processors/base.py` | import them so they are in the `eval()` scope for axis expressions |
| `analysis/workflows/hww.yaml` | **+12 axes** (1 `IntCategory` 0–10 and 11 one-hot) + `layout.candidate_cjet` entries |

The yaml expressions are evaluated by `base.py:189` (`eval(axis.expression)`), e.g.

```yaml
cjet_cand_ctag_2d_cat:
  type: IntCategory
  categories: [0,1,2,3,4,5,6,7,8,9,10]
  expression: ctag2d_category(ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvL,
                              ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvB)
cjet_cand_ctag2d_L0:
  type: IntCategory
  categories: [0, 1]
  expression: ctag2d_onehot(…CvL, …CvB, 'L0')      # ×11, one per category
```

### Running it

```bash
cd ~/higgscharm
python3 runner.py --workflow hww --year 2022postEE --submit --eos --output_format parquet
```

Output parquets now contain `cjet_cand_ctag_2d_cat` plus `cjet_cand_ctag2d_{L0…B4}`.

### Validation status

- ✅ YAML parses; 12 new axes registered; `layout.candidate_cjet` updated.
- ✅ The exact expressions, run through the real awkward path (`ak.pad_none(...)` → helper), on
  genuine PNet scores, reproduce the **already-verified stored column exactly**
  (20k tt events: one-hot rowsum ≡ 1, argmax ≡ category, 0 unassigned, matches stored column).
- ⚠️ **A full end-to-end `runner.py` job has NOT been run.** Two attempts were blocked by the
  environment, not by the code: the repo fileset points at a Purdue xrootd endpoint that needs a
  **grid proxy** (none active — needs your password), and the local EOS NanoAODs lack
  `Jet_btagPNetCvL/CvB` branches. **Please run one real job to confirm** before trusting a full
  production. Everything the code does downstream of reading those two branches is verified.

### Backfilling existing parquets

For files produced *before* this change, `scripts/append_ctag2d.py` adds the same columns
in place (idempotent, atomic writes):

```bash
python3 /eos/user/c/cgupta/HToWW/b-hive/scripts/append_ctag2d.py <dir-with-process-parquets>
```

Already applied to: `hww_combine_fixed/2022postEE` (57 files, 8.1M rows) and all six
`mva_labeled/{train,test}` dirs for 2022postEE / 2022preEE / 2023preBPix (38 files, 4.08M rows).

---

## 5. MVA retrain results (v11, 6-class)

Setup: `SimpleMLP_MultiClass`, 128→64→32→6 with BatchNorm+Dropout(0.2), 30 epochs, batch 1024,
lr 1e-3, class loss-weighting. Identical cross-era train/test filelists for both variants.

| | baseline | 2D-cats |
|---|---|---|
| config | `HPlusCHToWW_multiclass` | `HPlusCHToWW_2dcats` |
| training version | `hwwcom_multiclass_v11` | `hwwcom_multiclass_v11_2dcats` |
| charm-tag inputs | `cvsl_pnet`, `cvsb_pnet` | **11 one-hot** `ctag2d_*` (scores removed) |
| input dim | 17 | 26 |
| best epoch | 22 | 17 |
| val loss / acc | 0.01072 / 0.4150 | 0.01260 / 0.4077 |

### Test-set AUC

| Discriminant | 2D-cats | Baseline | Δ |
|---|---|---|---|
| **hplusc_vs_all** | **0.9322** | 0.9284 | **+0.0038** |
| hplusc_vs_higgsbkg | 0.8302 | 0.8506 | **−0.0204** |
| hplusc_vs_tt | 0.9438 | 0.9375 | +0.0063 |
| hplusc_vs_st | 0.9334 | 0.9287 | +0.0047 |
| hplusc_vs_diboson | 0.8855 | 0.8840 | +0.0015 |
| hplusc_vs_vjets | 0.9425 | 0.9348 | +0.0077 |

**Takeaway.** Replacing the two continuous scores with 11 one-hot categories is **≈ equivalent**:
overall AUC is marginally better and 4 of 5 background ROCs improve. The one loss is **vs
higgs-background (−0.020)** — separating H+c from other Higgs modes needs the fine charm-tag
gradient that a coarse 11-bin (effectively ~6-bin) scheme throws away. Note val loss/acc are
slightly *worse* for 2D-cats even though AUC is better, i.e. the gain is in ranking, not
calibration.

ROC plots (6 PNG+PDF+npy):
`…/ROCCurveTask/HPlusCHToWW_2dcats/hwwcom_v11_2dcats_train/hwwcom_v11_2dcats_test/hwwcom_multiclass_v11_2dcats/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/`

---

## 6. Feature importance

Method: gradient-based, `mean |∂P_hplusc/∂z_f − ∂P_k/∂z_f|` with `z` the **standardized** feature
(so raw-unit features don't win trivially), summed over background classes weighted by
`α_k = sigmoid(cos_sim(W_sig, W_k)/τ)`, τ=0.3. 75,000 test events each, identical for both.

Script: `Projects/HToWW/lxplus-2026-07-12/feature_importance_2dcats.py`
(deployed at `b-hive/scripts/feature_importance_2dcats.py`; `--variant 2dcats|base`)

### 2D-cats model (26 features)

| # | feature | importance | rel% |
|---|---|---|---|
| 1 | dilepton_mass | 0.27879 | 25.4% |
| 2 | mtl1 | 0.19257 | 17.6% |
| 3 | met_pt | 0.13025 | 11.9% |
| 4 | mtl2 | 0.11625 | 10.6% |
| 5 | dilepton_pt | 0.09031 | 8.2% |
| 6 | lepton1_pt | 0.08855 | 8.1% |
| 7 | lepton2_pt | 0.04965 | 4.5% |
| 8 | nSV | 0.04822 | 4.4% |
| 9 | cjet_cand_pt | 0.04669 | 4.3% |
| 10 | delta_R_ll_c | 0.01359 | 1.2% |
| 11 | **cjet_cand_ctag2d_B0** | 0.01281 | 1.2% |
| 12 | **cjet_cand_ctag2d_L0** | 0.00666 | 0.6% |
| 13 | **cjet_cand_ctag2d_C0** | 0.00580 | 0.5% |
| 14 | delta_R_ll_l2 | 0.00405 | 0.4% |
| 15 | **cjet_cand_ctag2d_C2** | 0.00207 | 0.2% |
| 16 | delta_phi_l1PlusMET_c | 0.00194 | 0.2% |
| 17 | delta_phi_l2_MET | 0.00193 | 0.2% |
| 18 | delta_phi_l1_MET | 0.00179 | 0.2% |
| 19 | **cjet_cand_ctag2d_C1** | 0.00097 | 0.1% |
| 20 | **cjet_cand_ctag2d_B3** | 0.00061 | 0.1% |
| 21 | **cjet_cand_ctag2d_B1** | 0.00058 | 0.1% |
| 22 | delta_R_ll_l1 | 0.00056 | 0.1% |
| 23 | **cjet_cand_ctag2d_B2** | 0.00051 | 0.0% |
| 24 | **cjet_cand_ctag2d_B4** | 0.00047 | 0.0% |
| 25 | **cjet_cand_ctag2d_C3** | 0.00017 | 0.0% |
| 26 | **cjet_cand_ctag2d_C4** | 0.00000 | 0.0% |

### Baseline model (17 features)

| # | feature | importance | rel% |
|---|---|---|---|
| 1 | dilepton_mass | 0.31533 | 25.3% |
| 2 | mtl1 | 0.23808 | 19.1% |
| 3 | met_pt | 0.14406 | 11.6% |
| 4 | mtl2 | 0.13297 | 10.7% |
| 5 | dilepton_pt | 0.10378 | 8.3% |
| 6 | lepton1_pt | 0.10176 | 8.2% |
| 7 | cjet_cand_pt | 0.06184 | 5.0% |
| 8 | lepton2_pt | 0.05107 | 4.1% |
| 9 | nSV | 0.04140 | 3.3% |
| 10 | delta_R_ll_c | 0.01482 | 1.2% |
| 11 | **cjet_cand_cvsl_pnet** | 0.01290 | 1.0% |
| 12 | **cjet_cand_cvsb_pnet** | 0.01050 | 0.8% |
| 13 | delta_R_ll_l2 | 0.00699 | 0.6% |
| 14 | delta_phi_l1_MET | 0.00376 | 0.3% |
| 15 | delta_phi_l2_MET | 0.00260 | 0.2% |
| 16 | delta_phi_l1PlusMET_c | 0.00223 | 0.2% |
| 17 | delta_R_ll_l1 | 0.00167 | 0.1% |

### Grouped: the charm-tag block

| model | charm-tag total | share |
|---|---|---|
| 2D-cats (11 one-hot) | 0.03064 | **2.8%** |
| baseline (2 scores) | 0.02340 | **1.9%** |

**Reading it.**
1. **Kinematics dominate both models** — `dilepton_mass` + `mtl1` alone are ~43%. The charm tag
   is a small fraction of what the MVA uses; this is the headline caveat on *any* c-tag change.
2. The 2D block carries **more** aggregate importance (2.8% vs 1.9%) — the categorization is not
   throwing information away in the mean; it redistributes it.
3. Within the block, importance concentrates in **B0, L0, C0** — the *populated, high-statistics*
   bins. `C4` is exactly 0.00000 (it has 39 jets), and B1–B4 are ~0 (empty). This is direct
   confirmation of the §3 caveat: **~4–5 of the 11 inputs are dead weight.**
4. The near-identical kinematic rankings across both models are a good sanity check that the two
   trainings are otherwise comparable.

---

## 7. How to proceed with v32

v32 is the finer-grained class scheme (`process_groups_v32` in `hww_combine_fixed.yaml`), driven
by `train_v32.sh` / `train_v32_sub.sh` with config `HPlusCHToWW_multiclass`. To repeat this study
on v32, mirror exactly what was done for v11:

**1 — Make sure the inputs carry the columns.** The v32 training reads the same
`hww_combine_fixed/<year>/mva_labeled/{train,test}` files, which **already have** the 12 columns
(backfilled). If you regenerate them via `make_mva_labeled.py` + `split_train_test.py` from the
top-level parquets, re-run the appender afterwards, or re-produce from the patched processor:

```bash
python3 /eos/user/c/cgupta/HToWW/b-hive/scripts/append_ctag2d.py \
    /eos/home-c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva_labeled/train \
    /eos/home-c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva_labeled/test
```

> This was the failure that killed the first job: training reads `mva_labeled/`, **not** the
> top-level parquets. Check the columns are there before submitting.

**2 — Create the v32 2D-cats config.** Copy whatever config `train_v32.sh` uses, strip the two
PNet score lines from `global_features`, add the 11 one-hot lines:

```bash
cd /eos/user/c/cgupta/HToWW/b-hive
grep -E "^CONFIG=" train_v32.sh          # find the config it points at
cp config/<that>.yml config/<that>_2dcats.yml
# then in the copy: delete cjet_cand_cvsl_pnet + cjet_cand_cvsb_pnet,
# add cjet_cand_ctag2d_L0 … _B4  (11 lines) under global_features
```

**3 — Create the driver.** Copy `train_v32.sh` → `train_v32_2dcats.sh` and suffix *every* version
so it cannot clobber baseline outputs:

```
CONFIG="<that>_2dcats"
DATASET_VERSION="…_2dcats_train"
TEST_DATASET_VERSION="…_2dcats_test"
TRAINING_VERSION="…_v32_2dcats"
```

**4 — Submit to the H100 pool.** Copy `job_mva_2dcats.sh` → point it at `train_v32_2dcats.sh`,
and reuse `submitter_mva_2dcats.sub`:

```bash
condor_submit ~/submitter_mva_2dcats.sub
condor_q <cluster>;  tail -f ~/job_2dcats.<cluster>.0.out
```

**Two batch gotchas learned the hard way (both cost hours):**
- `request_memory` **must be set** — the 3000 MB default OOMs in DatasetConstructorTask (peaks
  ~4.2 GB) and the job is *held*, not failed.
- But do **not** inflate it. 16 GB rounds to 18000 and then matches **zero** H100 slots
  (`condor_q -analyze` → "0 slots match"), because free H100 GPUs are scarce and only large
  memory tiers qualify. **8000 is the sweet spot** — matched in ~8 s.

**5 — Compare.** AUCs live in `AUC_default_all.npy` in each ROCCurveTask dir; feature importance
via `feature_importance_2dcats.py` (add a v32 entry to its `VARIANTS` dict — it currently only
knows the two v11 models, and v32 has a different class count, so `CLASSES`/`NUM_TRUTHS` need
updating too).

### Recommendation before investing in v32

Given the v11 outcome, I'd **not** run v32 as a straight replacement first. Two things are worth
settling with cheap v11 runs:

1. **Additive variant** — keep `cvsl`/`cvsb` **and** the one-hot categories. v11 showed the only
   regression is vs higgsbkg (−0.020), precisely where fine gradient matters; the additive model
   should recover it while keeping the +0.004 overall gain. This is the single most informative
   next run.
2. **Drop the dead bins** — B1–B4 (and probably C4) are identically zero for the candidate c-jet.
   Feeding 4–5 constant-zero inputs is pure noise-surface. Either collapse them into a single
   "B" bin or apply the scheme to a jet collection that populates the full plane.

Only once the feature set is settled is it worth spending v32 GPU time.

---

## 9. Scale factors (per-campaign PNet 2D SFs) — added 2026-07-22

The official **per-category** 2D flavour-tagging SFs for PNet AK4 (the H→γγ /
`cmshgg` "2D_HF_Tagging" ingredients, correctionlib v2). These are the correct SFs
for our 11-category scheme — one SF per (flavour, category, pt), applied to the
**candidate c-jet**. Provided by the analysis group on EOS:

| campaign | file |
|---|---|
| 2022 preEE  | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022preEE.json.gz` |
| 2022 postEE | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022postEE.json.gz` |
| 2023 preBPix  | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2023/2D_HF_Tagging/flavTaggingSF_2023preBPix.json.gz` |
| 2023 postBPix | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2023/2D_HF_Tagging/flavTaggingSF_2023postBPix.json.gz` |

**Correction:** `ParticleNetAK4_pseudocontinuous`
**Signature:** `evaluate(systematic, flavor, wp, abseta, pt)`
- `systematic` (string): `central`; uncertainties `up_Total`/`down_Total` (combined —
  use this for a single nuisance), `up_Stat`/`down_Stat`, plus a large per-source
  decomposition (`up_JES`, `up_XSec_*`, `up_LHEScaleWeight_*`, per-bin `up_Stat_flav*_*`, …).
  **There is no bare `up`/`down`.**
- `flavor` (int): `0`=udsg, `4`=c, `5`=b — the jet's **hadron flavour**
  (`cjet_cand_flavour` in the parquets).
- `wp` (int): the 2D category id — **`L0=0, C0..C4 = 40..44, B0..B4 = 50..54`**.
  (Map our stored `cjet_cand_ctag_2d_cat` 0..10 → these ids.)
- `abseta` (real): **inclusive** (single `eta_0p00toinf` bin — value irrelevant, pass any).
- `pt` (real): pt-binned `[20,35,50,70,90,120,10000]` (flat below 20 / above 120).

**Central SF matrix** (2022postEE, pt=60, verified by evaluation):

| flavour | L0 | C0 | C1 | C2 | C3 | C4 | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| udsg | 0.953 | 1.122 | 1.193 | 0.300 | 1.062 | 1.000 | 0.822 | 1.000 | 1.000 | 1.000 | 1.000 |
| c    | 1.149 | 1.000 | 0.885 | 1.091 | 0.781 | 0.749 | 1.148 | 1.000 | 1.000 | 1.000 | 1.000 |
| b    | 0.730 | 1.450 | 1.232 | 1.167 | 1.274 | 1.142 | 1.042 | 1.064 | 0.938 | 0.953 | 0.921 |

**B1–B4 SFs are 1.0 for every flavour** — uncalibrated / empty, consistent with §3's
finding that B1–B4 are empty for the candidate c-jet. Across the whole 2022postEE MC,
**every event lands in L0 / C0–C4 / B0; B1–B4 receive zero events** (verified in the
applier dry-run), so those SFs are exact no-ops.

### How it enters the fit
The SF is a genuine correction on the candidate c-jet, so it multiplies the
**nominal** weight, with a single combined shape+norm nuisance `CMS_ctag2d_<year>`
carrying `up_Total`/`down_Total`:

- applier `b-hive/scripts/apply_ctag2d_sf.py` adds three columns to each
  `mva/<sample>.parquet` (MC only, data untouched), idempotent with a
  `.bak_pre_ctag2dsf` backup:
  - `weight_nominal` ← `weight_nominal × SF_central` (and every existing
    `weight_*` variation is scaled by the same central SF, so the correction is
    everywhere);
  - `weight_CMS_ctag2d_<year>Up`   = `weight_nominal_corrected × SF_upTotal/SF_central`;
  - `weight_CMS_ctag2d_<year>Down` = `weight_nominal_corrected × SF_downTotal/SF_central`.
- category per row = recomputed from `cvsl_pnet`/`cvsb_pnet` (the `mva/` parquets carry
  the raw scores but not the int cat column); flavour = `cjet_cand_flavour`; rows with
  no candidate c-jet (`cjet_cand_pt` NaN) → SF 1.
- add `CMS_ctag2d_<year>` to `shape_systematics` in `hww_combine_fixed.yaml`; the
  existing `build_variations`/`process_sample` machinery then reads the two new
  weight columns automatically — no builder code change.

**Only 2022postEE is populated** in the combine tree today, so the rerun uses
`flavTaggingSF_2022postEE.json.gz` and the nuisance `CMS_ctag2d_2022`. The other
three files are wired in and ready for when 2022preEE / 2023 are processed.

**Object-shift consistency:** the JES/JER/lepton-scale templates read `weight_nominal`
from their own `<year>/<shift>/mva/` dirs. The SF is applied there too (recomputed from
each dir's *shifted* scores/pt), so the shift is measured against the same SF-corrected
baseline — otherwise every object-shift nuisance would pick up a spurious ~6% offset.
All 12 shift dirs corrected.

### Limit result (2022postEE, blind Asimov, `run_limit.sh … ctag2dsf`)

| variant | full (all syst) | stat-only | freeze-autoMCStats |
|---|---|---|---|
| baseline (`negrwF`, pre-SF) | 1343 | 788 | 1100 |
| **+ `CMS_ctag2d_2022`** | **1371** | 797 | 1144 |
| Δ | +28 (+2.1%) | +9 (+1.1%) | +44 (+4.0%) |

The SF **weakens the expected limit by ~2%** — the expected sign/size. The stat-only
shift (+1.1%) is just the yield rescaling (mean central SF ~1.06 changes SR S/√B); the
extra degradation in the full limit is the one new nuisance's wide (+44%/−16%) band. A
real c-tag SF *should* cost a little; this is the systematic doing its job, not a
regression. The stat-only→full gap is still autoMCStats-dominated (freeze → 1144), i.e.
low-stat SR templates remain the driver, not the SF.

**Backfill / undo:** `apply_ctag2d_sf.py` is idempotent (guards on the `Up` column) and
leaves `.bak_pre_ctag2dsf` next to every parquet; the yaml has
`hww_combine_fixed.yaml.bak_pre_ctag2dsf`. To revert, restore the backups and rebuild.

### Limit with the 2D-cat MVA *and* the SF (the physically-matched combination)

The SFs calibrate the 2D-category tagging, so they belong with the **2D-cat MVA scores**,
not the baseline scores. Built as a separate workflow `hww_combine_2dcat` (copy of
`hww_combine_fixed` with `inference:` → the 2D-cat model
`.../HPlusCHToWW_2dcats/.../best_model.pt`, config `HPlusCHToWW_2dcats`, output
`v11_hplusc_2dcat.*`). The SF-corrected `mva/` trees (nominal + 12 shift dirs) were copied
into `outputs/hww_combine_2dcat/2022postEE/`, the 11 one-hot cols appended
(`append_onehot.py`, deterministic from cvsl/cvsb), and the `mva_score_*` cols re-scored
in place with the 2D-cat model (`rescore_2dcat.py`, softmax, `.bak_pre_2dcatscore` backups).

**Full three-way comparison (2022postEE, blind Asimov):**

| variant | full (all syst) | stat-only | freeze-autoMCStats |
|---|---|---|---|
| baseline (no SF) | 1343 | 788 | 1100 |
| baseline scores + SF (`ctag2dsf`) | 1371 | 797 | 1144 |
| **2D-cat scores + SF (`2dcatsf`)** | **1422** | **749** | 1168 |

**Reading it:**
- **Stat-only *improves*: 749 vs 788 (−5%).** With statistics-only uncertainties the
  2D-cat MVA is the sharper discriminant — signal (H+c) `<P_hplusc>` rises to 0.514
  (baseline 0.377) and **91.1%** of signal lands in the SR (baseline 70.8%). Consistent
  with the +0.004 AUC.
- **Full limit is *worse*: 1422 vs 1343 (+6%).** The 2D-cat argmax also pulls **2.3× more
  tt** into the SR (tt→SR fraction 18.9% vs 8.3%), so SR yields ~double (SR total 20563 vs
  ~9142). tt is the dominant background, so the enlarged SR is more systematics-exposed;
  the wide `CMS_ctag2d_2022` band + autoMCStats on the bigger SR eat the stat gain. The
  stat→full inflation grows (749→1422 = 1.9× vs 788→1343 = 1.7×).

**Verdict:** the 2D-cat model genuinely separates better (stat-only wins), but with the
current conservative systematics its more-inclusive SR boundary lets in enough tt that the
*full* expected limit regresses ~6%. Levers to recover it: tighten the SR (raise the
P(hplusc) cut / rebin), split ggH out of higgsbkg, or narrow the SF nuisance once a less
conservative decomposition (e.g. Stat-only, or the per-source split) is used instead of
`Total`. Not a bug — an honest separation-vs-systematics trade.

**Baseline tree untouched:** all 2D-cat work lives under `outputs/hww_combine_2dcat/`;
`hww_combine_fixed` (baseline+SF) is unchanged. Limit roots:
`outputs/combine/higgsCombine2dcatsf{F,S,M}.AsymptoticLimits.mH120.root`.

---

## 8. File map

| what | where |
|---|---|
| helper (processor) | `~/higgscharm/analysis/utils/ctag2d.py` (AFS, branch `NewWorkflows`) |
| 2D SF applier | `b-hive/scripts/apply_ctag2d_sf.py` (+ vault copy in `lxplus-2026-07-12/`) |
| 2D SF files | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/{2022,2023}/2D_HF_Tagging/flavTaggingSF_<campaign>.json.gz` |
| 2D-cat combine workflow | `~/higgscharm/analysis/workflows/hww_combine_2dcat.yaml` (inference→2D-cat model, out `v11_hplusc_2dcat.*`) |
| one-hot appender | `b-hive/scripts/append_onehot.py` (+ vault copy) |
| 2D-cat re-scorer | `b-hive/scripts/rescore_2dcat.py` (+ vault copy) |
| 2D-cat combine tree | `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE/` |
| workflow axes | `~/higgscharm/analysis/workflows/hww.yaml` |
| backfill script | `b-hive/scripts/append_ctag2d.py` |
| 2dcats train config | `b-hive/config/HPlusCHToWW_2dcats.yml` |
| 2dcats driver | `b-hive/train_v11_2dcats.sh` |
| condor job / submitter | `~/job_mva_2dcats.sh`, `~/submitter_mva_2dcats.sub` (AFS) |
| feature importance | `b-hive/scripts/feature_importance_2dcats.py` |
| plane plot generator | vault `Projects/HToWW/lxplus-2026-07-12/plot_2dplane_v2.py` |
| plane plot | `/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.{png,pdf}` |
| vault copies of all scripts | `Projects/HToWW/lxplus-2026-07-12/` |
