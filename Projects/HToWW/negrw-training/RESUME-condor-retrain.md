---
tags: [reference]
status: active
date: 2026-07-15
source: lxplus
---

# NEGRW — ✅✅ LIMIT IMPROVED: r95 1742 → 1343 (−23%)

## 🎯 RESULT (2026-07-17) — BOTH v11 AND v32, central value only

| builder | metric | baseline | negrw | Δ |
|---|---|---|---|---|
| **v11** (make_combine_inputs.py) | full | 1742 | **1343** | −23% |
| | stat-only | 771 | 788 | +2% |
| | freeze-autoMCStats | 1032 | 1100 | |
| **v32** (make_combine_histograms_v11_v32.py, v32_v9 model) | full | 1935 | **1491** | −23% |
| | stat-only | 600 | 599 | flat |
| | freeze-autoMCStats | 1068 | 1083 | |

Both: autoMCStats inflation collapsed (~-60%), stat-only ~flat (template undistorted).
v32 baseline datacard backed up `combine_inputs/v11_hplusc_v32_v9.{txt,root}.bak_pre_negrw`;
builder `.bak2_pre_negrw`.

## ⚠️ OPEN: METHOD UNCERTAINTY NOT YET IN THE LIMIT
Both numbers above are **central-value only**. The reweighting's OWN systematic —
`weight_negrw_std` = 2·std(P+) (ensemble spread, mean ~0.012, already in the parquets,
validated) — is NOT yet added as a datacard shape nuisance. arXiv:2510.16217 §IV B–D
prescribes it (event-level ±g_std → vjets template Up/Down shape, or PCA over the ensemble
per-bin covariance). This WILL pull the limit back up somewhat from 1343/1491 — the honest
cost of the method. **TODO before quoting a final number.** The `weight_negrw_std` column is
currently unused.

## 🎯 FINAL RESULT (2026-07-17)
Neg-weight reweighting wired into the canonical combine builder
(`scripts/combine/make_combine_inputs.py`, `is_vjets` path: fill = |w|·weight_negrw·renorm,
REPLACES smoothing). Limit on `outputs/combine/v11_hplusc_v4.txt`:

| | baseline (pre-negrw) | **negrw** | Δ |
|---|---|---|---|
| full (all syst) | **1742** | **1343** | **−23%** |
| stat-only floor | 771 | 788 | ~flat |
| freeze autoMCStats | 1032 | 1100 | +7% |

**autoMCStats inflation (full − freeze) collapsed 710 → 243 (−66%)** — the reweighting
raised SR N_eff at the source, exactly as designed. Per-sample renorm: DYto2L_50 ×0.986,
WtoLNu ×0.900, DYto2L_10to50 ×0.446 (74-evt sample). Baseline datacard backed up
`v11_hplusc_v4.{txt,root}.bak_pre_negrw`.

**THE SMOKING GUN (SR_hplusc_vjets bin-6):** baseline `0.000 ± 4.1e9 %` (the ±79k
cancellation → 0±∞, the bin that drove 1742) → negrw **`91.5 ± 24.7 %`** (real, finite).
SR mean rel MC-stat err/bin: ~∞ → **0.203**; CR_vjets: 0.193 → 0.126. Every bin's error
shrank, contents stayed physical, yield preserved by renorm.
**Why stat-only floor moved 771→788 (not flat):** the "stat-only" limit freezes
allConstrainedNuisances but KEEPS autoMCStats `prop_bin*` floating — so it INCLUDES per-bin
MC-stat error. The reweighting changes those errors (bin6 0±∞ → 91±25%), so stat-only SHOULD
move; +2% is the net rebalance = expected, not a distortion. ("freeze autoMCStats" is the
separate line that removes prop_bin*.)

---

# NEGRW RETRAIN — ✅ DONE (Condor, 2026-07-15)

## ✅ RESULT: sklearn blocker RESOLVED, model + plots + deck delivered

**Cluster `9086952` finished clean (JobStatus=4, ExitCode=0).** The ensemble is retrained
inside the worker image → the pickle now loads on workers.

**VERIFIED in-image load:**
```
sklearn in image: 1.7.2
LOADED OK -> n_models 20 | n_features 20 | frac_pos 0.8359
predict_proba OK; g sample: [ 0.984 -0.974  0.967 -0.981  0.985]
```
The old `AttributeError __pyx_unpickle_CyHalfBinomialLoss` is gone.

### Artifacts
- **Model (USE THIS):** `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/negrw_models.joblib` (sklearn 1.7.2)
- Diagnostics: `.../negrw_out_img/negrw_diagnostics.npz`, `sklearn_version.txt` (=1.7.2), `train.log`, `img/*.png`
- Submit dir (raw): `/afs/cern.ch/user/c/cgupta/negrw_condor/` (out/, .sub, .out logs)
- **Deck:** `Projects/HToWW/negrw-training/slides.md` (Marp) + `img/*.png` — user renders with Marp
- `hww_combine_fixed.yaml` **repointed** to `negrw_out_img/negrw_models.joblib`
  (backup of prior: `hww_combine_fixed.yaml.bak_pre_imgmodel`)

### Results (reproduce the Jul-12 reference run almost exactly)
| metric | Jul-12 (sklearn 1.4.2) | Condor (sklearn 1.7.2) |
|---|---|---|
| events | 9.72M | 9,832,308 |
| frac positive | 0.836 | 0.836 |
| g mean | 0.672 | 0.672 |
| δg mean / max | 0.006 / 0.424 | 0.006 / 0.467 |
| **closure ratio** | **0.994** | **0.994** |
| **N_eff** | 2.91M → 4.67M (+60%) | **2.92M → 4.68M (+60.1%)** |
| ensemble log-loss / AUC | — | **0.331 / 0.829** |

**Per-bin N_eff gain (the headline):** ~**3× sustained across the whole hard-Vpt tail**
(1.39× in bin 0 which was never starved; 2.84× @40-60; 3.07× @80-100; 3.15× @160-180;
3.21× @200-220; 3.54× @260-280; 3.84× @360-380). Gain grows exactly where autoMCStats hurts.

**Notable:** median n_iter = 200 → **early stopping never fired, all members hit the
max_iter ceiling**; loss still descending. There is headroom (more iters / deeper trees).
Top features by permutation importance: `lhe_npnlo` (dominant), `lhe_njets`, `lhe_nglu`,
`genparton1_pt`, `lhe_alphas` — physically sensible (amc@NLO merging/subtraction regions).

## 🐞 TWO REAL BUGS FOUND + FIXED BEFORE THE SR SUBMIT (2026-07-15)

**1. The dataset gate was substring-matching and would have reweighted SIGNAL.**
`_dataset_matches` did `any(p in dataset for p in patterns)` with `datasets: [DYto2L, WtoLNu]`.
`"WtoLNu" in "WplusH_WtoLNu_Hto2Wto2L2Nu"` → **True** → the WH **signal** sample would have
been reweighted with a V+jets generator model, silently corrupting a signal template.
**Fix:** `_dataset_matches` now does **exact** matching (`dataset in set(names)`), and the
yaml lists exact names: `DYto2L_2Jets_10to50`, `DYto2L_2Jets_50`, `WtoLNu_2Jets`.
Verified: the 3 vjets samples → REWEIGHT; `WplusH_WtoLNu_Hto2Wto2L2Nu`, `TTto2L2Nu`,
`HplusCharm_HtoWW`, `GluGluHto2Wto2L2Nu` → untouched.

**2. The model path was on EOS, which the worker container CANNOT read.**
`joblib.load("/eos/user/c/cgupta/...")` inside the singularity image →
`PermissionError [Errno 13]`. Every Condor job would have died.
**Fix:** model staged to **AFS** `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models.joblib`
and yaml repointed there (workers read AFS fine — `submit.sh` cds into the AFS repo).
Master copy still on EOS in `negrw_out_img/`.

**Also note:** `b_hive` (sklearn 1.4.2) can **no longer load this model** (it's 1.7.2) —
`TypeError: __generator_ctor()`. Local processor tests must now run **inside the image**:
`singularity exec -B /afs -B /cvmfs -B /tmp -B /eos --env X509_USER_PROXY=/tmp/x509up_u151861 $IMG python3 ...`

**Smoke test PASSED (in-image, real processor → parquet, DYto2L_2Jets_50, 200k events):**
13 event shards (nominal + 12 JEC/JER/scale shifts) + 1 `sumw_records/` file → **143 SR rows**,
`weight_negrw` **0 NaN**, all g∈[−1,1], range [−0.336, 0.709], mean 0.333, 12 distinct;
`weight_negrw_std` mean 0.009 max 0.024; frac w>0 in SR = **0.545** (vs 0.836 inclusive —
the SR concentrates the negative-weight region, which is exactly why this fix matters).
⚠️ **Gotcha when validating parquets:** a recursive `**/*.parquet` glob also picks up
`sumw_records/*.parquet` (single `sumw` column); concatenating it with event shards
manufactures an all-NaN row. Filter to files that have `weight_nominal`.

## 📦 FILESET REGENERATED (2026-07-15)
Live `fileset_2022postEE_nanov12_lxplus.json` was the **truncated Phase-1** one (4 datasets,
vjets capped at 35 files each = 105). Re-ran:
`python3 fetch.py --year 2022postEE --samples DYto2L_2Jets_50 DYto2L_2Jets_10to50 WtoLNu_2Jets`
→ now **3 datasets, 989 files**: DYto2L_2Jets_50 **286**, DYto2L_2Jets_10to50 **322**,
WtoLNu_2Jets **381** (matches the full `.bak_presiteredir` counts).
NOTE `make_filesets.py` **overwrites** (open "w"), it does not merge — the fileset now holds
only these 3 vjets samples. Backups: `.bak_pre_srererun_20260715`, `.bak_presiteredir` (53 datasets).

## 🐞 BUG #3 (found on first submit) + a data-safety lesson (2026-07-15)

**The exact-match gate was TOO strict and silently produced NO reweighting.**
condor/submit.sh runs `--dataset <name>_$JOBID`, so the processor sees
`DYto2L_2Jets_50_7`, not `DYto2L_2Jets_50`. The exact `dataset in set(names)` gate
rejected every partitioned name → first submit (clusters 9087046/47/48, REMOVED) wrote
121-col parquets with NO weight_negrw. **Fix:** `_dataset_matches` now strips a trailing
`_\d+` partition suffix before matching (`re.sub(r"_\d+$","",dataset)`), still anchored so
`WplusH_WtoLNu_Hto2Wto2L2Nu` stays untouched. Verified against 14 cases incl. suffixed vjets
(match) and suffixed WH signal (untouched). `import re` added to base.py.

**⚠️ DATA-SAFETY LESSON:** Condor jobs write straight into `<dataset>_<N>/base/` on EOS,
**overwriting** whatever is there. Submitting the (buggy) run overwrote the pre-existing
vjets SR production; then I `rm -rf`'d those partition dirs. No permanent loss (vjets SR is
regenerable = this very re-run), and only the 3 vjets sample names were touched — the other
435 dirs / 125k parquets (base/, CMS_* shifts, all non-vjets samples) are intact. But the
destructive act was the SUBMIT (overwrite-on-write), not the delete. **Rule going forward:
run ONE canary job and verify columns before a full submit over live data.**

## ✅ RE-RUN SUBMITTED + VALIDATED (clusters 9087051/9087052/9087053)
20/22/26 jobs (DYto2L_2Jets_50 / _10to50 / WtoLNu_2Jets), parquet→EOS, nfiles 15, 989 files.
**Verified in fresh output:** weight_negrw present, 0 NaN, all g∈[−1,1], per-event varying;
weight_negrw_std mean ~0.012; sample closure Σ|w|g/Σw ≈ 0.98 (tightens with more shards).
Output: `/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/{DYto2L_2Jets_50,
_10to50,WtoLNu_2Jets}_<N>/`. Check: `condor_q 9087051 9087052 9087053 -totals`.

## ✅ RE-RUN COMPLETE + FULL VALIDATION (2026-07-15)
All 68 jobs (9087051/52/53) done. weight_negrw/std in all 3 datasets, **0 NaN / 10,205 SR rows**,
all g∈[−1,1]. 0-SR-event partitions (esp. low-mass DYto2L_10to50) still wrote sumw_records =
jobs ran fine, just few events pass the eμ SR (physical).
**SR N_eff gain = 3.44× (455 → 1563)** — bigger than the +60% on the training region because
the SR is exactly the starved regime the method targets.

**⚠️ OPEN PHYSICS QUESTION — SR closure offset:** per-dataset Σ|w|g/Σw:
DYto2L_50 **1.014**, WtoLNu **1.133**, DYto2L_10to50 2.24 (only 74 rows = noise); **TOTAL 1.058**
(6% high). Training-region closure was 0.994 on 9.8M events. The SR is a small (~10k events),
kinematically-biased corner of the training domain, so per-event g doesn't perfectly average to
the local positive fraction → normalization drifts a few %. **DECISION NEEDED before the limit:**
(a) accept as-is (small vs the 1742 problem), (b) renormalize the reweighted vjets template to the
nominal yield (reweighting is meant to fix VARIANCE, not change the central yield — a post-hoc
Σ|w|g→Σw rescale is defensible and standard), or (c) investigate the WtoLNu 13% before trusting.
Recommendation: **(b) renormalize per dataset** — preserves the N_eff gain while keeping the
central yield = nominal, which is what closure should give in the large-N limit anyway.

## ⚠️ 689 / 10325 vjets SR events (~7%) missing due to xrootd errors
(re-run vs Jul-12 production; `jobs_status.py` = 0 missing jobs since loss is intra-job;
transient `XRootD Operation expired` on ~53 input files, mostly ruhex-osgce.rutgers.edu).
Proceeding anyway per user — background template, yield renormalized to nominal.

## ✅ MERGE DONE (2026-07-17) — via repo's own merge_parquet_files
Merged the 3 vjets samples' fresh shards → the combine inputs, using
`analysis.postprocess.utils.merge_parquet_files` (the repo's tested flat-concat +
sumw-aggregation merger), scoped to vjets only (NOT the full merge). Wrote:
`SAMPLE_DIR/<sample>.parquet` (nominal) + `SAMPLE_DIR/<shift>/<sample>.parquet` (12 shifts)
= 39 files, all with `weight_negrw`, verified 0 bad. Old files backed up `.bak_pre_negrw`.
Driver: `/tmp/merge_vjets_via_repo.py` (takes sample names as argv; idempotent; 6× retry on
the EOS footer-read race that aborted the first WtoLNu run).
**ctag2d SKIPPED per user** (combine histo-maker doesn't read those cols; append_ctag2d not run).
Nominal rows: DYto2L_50=9646, DYto2L_10to50=74, WtoLNu=469 (~7% below Jul-12 due to xrootd).

## ▶️ NEXT STEPS (Phase-3 continuation)
1. **Re-smoke the SR injection with the NEW model** — run one vjets SR file through the
   processor (now that yaml points at negrw_out_img) and confirm `weight_negrw` /
   `weight_negrw_std` columns appear and vary. (The in-image load test above already
   proves the pickle side.)
2. **Submit the vjets SR re-run** on `hww_combine_fixed` — **vjets datasets ONLY**
   (`DYto2L`, `WtoLNu`; double-gated by which datasets you submit AND the
   `negrw.datasets` block). Full file count (not the 35-file Phase-1 cap). Restore
   fileset from `.bak_presiteredir`/`.bak_pre_genrw` if truncated.
3. Merge SR parquets, sanity-check the new columns.
4. Wire into combine (`make_combine_histograms_v11_v32.py` + `dy_template_smooth.py`):
   vjets template ← `|weight_nominal|·weight_negrw` + PCA shape nuisance from ±weight_negrw_std.
5. Re-run the limit; check autoMCStats collapses and r₉₅ drops from 1742.

## HOW IT WAS RUN (for reference / re-running)
Host retrain kept **OOM-dying on the shared login node** (lxplus975 at 4GB free) → moved to
Condor. Container **cannot read /eos** arbitrary paths → training data tar'd (664MB, 502
parquet from `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/`) and shipped
via `transfer_input_files`. Job: 4 cpus / 8 GB / longlunch; peaked ~7.4 GB, ran ~50 min
(train ~35 min + diagnostics/plots).

**Scripts (in submit dir + `$CLAUDE_JOB_DIR/tmp`):**
- `negrw_diag.py` — SAME training as production `scripts/negweight_reweight_train.py`
  (identical 20 FEATURES, 20× HistGBDT, log_loss/max_iter 200/lr 0.05/max_depth 4/l2 1.0/
  early_stopping val 0.15, SUBSAMPLE_FRAC 0.6, seeded; label `weight_nominal>0`).
  **Changes:** reads only the 21 needed columns (memory fix); dumps `negrw_diagnostics.npz`
  (loss curves, n_iter, ROC/AUC, permutation importance, P+ by sign, g/δg, closure+N_eff,
  per-feature hists); writes `sklearn_version.txt`. Bundle schema UNCHANGED.
- `make_negrw_plots.py` — npz → 8 PNGs + summary.json.
- `negrw_condor_exec.sh` — untar → train → plot.
- `negrw_retrain.sub` — +SingularityImage = coffea-base-almalinux9:0.7.30-py3.10.
- `fix_closure_plot.py` (local) — regenerated 07_closure / 07b_neff_gain with log-y + ratio
  panels (the linear-scale original hid the tail).

**Key fact:** `submit_condor.py` (the SR-processing runner) DEFAULTS to
coffea-base-almalinux9:0.7.30-py3.10 → retrain image matches the workers. (The old
`condor/hww/*.sub` files reference coffea-dask py3.9 — NOT what SR jobs use; ignore.)

Processor injection code (base.py `_score_negrw` + `_dataset_matches`, workflow_config
passthrough, hww_combine_fixed.yaml negrw block) is DONE + smoke-validated, durable on the
AFS mount but NOT git-committed (repo tree has unrelated dirty files). See
`Projects/HToWW/2026-07-12-negweight-phase3-SR-inference-handoff.md`.

See [[hww-negweight-reweight-fix]] memory.
