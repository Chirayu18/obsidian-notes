---
tags: [reference]
status: active
date: 2026-07-15
source: lxplus
---

# NEGRW RETRAIN — RESUME STATE (Condor, 2026-07-15)

## Goal (two things)
1. **Retrain the 20-model neg-weight ensemble INSIDE the Condor worker image**
   (`coffea-base-almalinux9:0.7.30-py3.10`, sklearn **1.7.2**) so the joblib pickle
   loads on the SR-processing workers. The existing model
   `/eos/user/c/cgupta/HToWW/b-hive/negrw_out/negrw_models.joblib` was trained under
   sklearn **1.4.2** (b_hive env) and FAILS to load on workers
   (`AttributeError __pyx_unpickle_CyHalfBinomialLoss`). This is the ONLY Phase-3 blocker.
2. **Make training plots + a Marp markdown deck** (user renders with Marp himself).

## WHY Condor (not host)
Retraining on the shared lxplus login node kept getting **OOM-killed after model 1/20**
(node lxplus975 was at 4 GB free / 43 GB used / 9 GB swap). The container also can't see
`/eos` directly. Condor gives a dedicated 8 GB slot + the exact worker image. The earlier
SUCCESSFUL run (Jul 12) was host+b_hive → sklearn 1.4.2 → wrong version. So: Condor.

## SUBMITTED JOB
- **Cluster `9086952`** on schedd bigbird28. Submit dir: `/afs/cern.ch/user/c/cgupta/negrw_condor`.
- Check: `ssh lxplus 'condor_q 9086952 -totals; condor_history 9086952 -af JobStatus ExitCode -limit 1'`
- As of last check: **JobStatus=2 (RUNNING)** for ~10 min.

### Submit dir contents (`/afs/cern.ch/user/c/cgupta/negrw_condor/`)
- `negrw_retrain.sub` — submit file (+SingularityImage = coffea-base 0.7.30-py3.10;
  request 4 cpus / 8 GB / 4 GB disk; longlunch; transfer_output_files = out)
- `negrw_condor_exec.sh` — executable: prints env versions, untars data, runs
  `negrw_diag.py` then `make_negrw_plots.py`, both writing into `out/` and `out/img/`.
- `negrw_diag.py` — the training+diagnostics script (see below).
- `make_negrw_plots.py` — the plot generator (see below).
- `negrw_train.tar.gz` — 664 MB tarball of the 502 training parquets
  (`2022postEE/<dataset>/train/*.parquet`, from
  `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train/2022postEE/`).

### Expected outputs (transferred back to submit dir as `out/`)
- `out/negrw_models.joblib` — the **version-matched (1.7.2) ensemble** ← the deliverable
- `out/negrw_diagnostics.npz` — all plot data
- `out/sklearn_version.txt` — should read `1.7.2`
- `out/img/*.png` — 8 plots (01_loss_curves … 08_input_features)
- `out/summary.json` — headline numbers

## SCRIPTS I WROTE (local copies in $CLAUDE_JOB_DIR/tmp AND on lxplus)
Local: `/home/cgupta/.claude/jobs/af76ec6a/tmp/{negweight_reweight_train_diag.py,make_negrw_plots.py,negrw_condor_exec.sh,negrw_retrain.sub}`

**`negrw_diag.py` (= negweight_reweight_train_diag.py):** SAME training as the proven
production `scripts/negweight_reweight_train.py` — identical 20 FEATURES, 20×
HistGradientBoostingClassifier(loss=log_loss, max_iter=200, lr=0.05, max_depth=4,
l2=1.0, early_stopping, val_frac=0.15), SUBSAMPLE_FRAC=0.6, seeded. Label =
`weight_nominal > 0`. **Changes vs production:** (a) reads only the 21 needed columns
(memory fix); (b) ALSO dumps `negrw_diagnostics.npz` with per-model train/val loss
curves, n_iter, ensemble log-loss+AUC+ROC, permutation feature importance, P+ dist by
sign, g(x)/δg dists, lhe_vpt closure+N_eff, per-feature histograms split by weight sign;
(c) writes sklearn_version.txt. Model bundle schema UNCHANGED
({models, features, n_models, frac_pos}).

**`make_negrw_plots.py`:** reads the npz → 8 PNGs + summary.json. Plots: 01 loss curves
(20 members), 02 n_iter hist, 03 ROC, 04 permutation importance, 05 P+ by true sign,
06 g and δg, 07 closure+N_eff on lhe_vpt, 08 input-feature panels (blue w>0 / red w<0).

## EXPECTED NUMBERS (from the Jul-12 host run, 1.4.2 — should reproduce ~exactly)
- 9.72M events, frac positive 0.836
- g(x) mean 0.672, range [-0.991, 0.992]; δg mean 0.006, max 0.424
- CLOSURE ratio (Σ|w|g / Σw) = **0.994**
- N_eff **2.91M → 4.67M (+60%)**, 3–4× lift in hard-Vpt tail bins
(the Condor run loaded 9,832,308 events — same sample; tiny count diff = column-load path)

## NEXT STEPS (in order) when the job finishes
1. `ssh lxplus 'condor_history 9086952 -af JobStatus ExitCode -limit 1'` — expect JobStatus=4, ExitCode=0.
2. Copy outputs to EOS:
   `cp -r /afs/cern.ch/user/c/cgupta/negrw_condor/out /eos/user/c/cgupta/HToWW/b-hive/negrw_out_img`
   Verify `out/sklearn_version.txt` == 1.7.2 and closure ≈ 0.994 in the .out log.
3. **Point the workflow at the new model:** edit
   `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_fixed.yaml`
   → `negrw.model:` → `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/negrw_models.joblib`.
4. **Re-smoke in the image** (load the new joblib inside the container, score one vjets SR
   file) to prove the version blocker is gone on the worker env.
5. **Build the Marp deck** in `Projects/HToWW/negrw-training/`: pull `out/img/*.png` into
   `img/`, write `slides.md` (Marp frontmatter `marp: true`) referencing them + the
   summary.json numbers. Commit+push vault.
6. **Submit the vjets SR re-run** on `hww_combine_fixed` — **vjets datasets ONLY**
   (`DYto2L`, `WtoLNu`; gate is enforced both by which datasets you submit AND the
   `negrw.datasets: [DYto2L, WtoLNu]` block). Full file count (not the 35-file Phase-1 cap).
   Restore fileset from `.bak_presiteredir`/`.bak_pre_genrw` if truncated.
7. Merge SR parquets, sanity-check the new `weight_negrw`/`weight_negrw_std` columns.
8. Wire into combine (`make_combine_histograms_v11_v32.py` + `dy_template_smooth.py`):
   fill vjets template with `|weight_nominal|·weight_negrw` + PCA shape nuisance from
   ±weight_negrw_std. Re-run limit; check autoMCStats collapses, r₉₅ drops from 1742.

## KEY FACTS / GOTCHAS
- SR-processing runner `submit_condor.py` DEFAULT image = coffea-base 0.7.30-py3.10
  (confirmed) → retrain image matches. (Note: the old hww_*.sub files use coffea-dask
  py3.9 — NOT what the SR jobs use; ignore those.)
- Container CANNOT read /eos arbitrary paths → that's why data is tar'd + transferred.
- Grid proxy `/tmp/x509up_u151861` valid (~100h left as of 14:09).
- Processor injection code (base.py `_score_negrw`+`_dataset_matches`, workflow_config
  passthrough, hww_combine_fixed.yaml negrw block) is DONE + smoke-validated, DURABLE on
  the AFS mount but NOT git-committed (repo tree had unrelated dirty files). See
  `Projects/HToWW/2026-07-12-negweight-phase3-SR-inference-handoff.md`.

See [[hww-negweight-reweight-fix]] memory.
