---
tags: [reference]
status: active
date: 2026-07-15
source: lxplus
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
