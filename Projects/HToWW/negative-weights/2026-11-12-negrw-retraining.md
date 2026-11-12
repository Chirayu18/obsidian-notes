---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# negrw retraining v2 (2026-11-12): current DY / jet-binned W+jets, 4 Run-3 eras

**Status: agent-reported, DONE.** v2 model trained and validated by the agent; not switched into the analysis (that is Chirayu's/the parent's call). Not independently reviewed.

**Bottom line:** new model `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models_v2_20261112.joblib`, sha256 `af53567ccfeddeef94c1fa62b3a6ed3c1285937919ced3f7705c565b819155cb`. It is **fit for use**, but it is practically equivalent to the July model on the current samples (held-out AUC 0.8181 vs 0.8183, corr(g_new, g_old) = 0.9987 held-out / 0.9982 in the allfix SR). Switching is a provenance and consistency upgrade, not a physics change. N1: **pass**.
Chirayu (2026-11-12): "Do the negrw training (you might need to use the negrw workflow to get the
parquet files and subsequently find the scripts to then launch the training)". Job submission approved.
Started by one worker thread, moved to another account mid-flight (state verified on takeover, nothing
double-submitted).

## Old recipe (July 2026), reproduced exactly
Sources: [[Projects/HToWW/negative-weights/training/RESUME-condor-retrain|RESUME-condor-retrain]],
`~/negrw_condor/{negrw_retrain.sub,negrw_condor_exec.sh,negrw_diag.py}` on lxplus,
`/eos/user/c/cgupta/HToWW/b-hive/scripts/negweight_reweight_train.py`.
- 20 generator-level features: `lhe_njets lhe_nb lhe_nc lhe_nuds lhe_nglu lhe_npnlo lhe_ht lhe_htincoming lhe_vpt lhe_alphas genparton_multiplicity genparton_n_pt20 genparton_n_pt100 genparton_n_pt200 genparton_incoming1_pdgId genparton_incoming2_pdgId genparton1_pt genparton1_eta genparton2_pt genparton2_eta`.
- 20 × sklearn `HistGradientBoostingClassifier(log_loss, max_iter 200, lr 0.05, max_depth 4, l2 1.0, early_stopping, validation_fraction 0.15)`, each on a 60% subsample without replacement, seed+m; label `weight_nominal > 0`; unweighted fit. Bundle `{"models","features","n_models","frac_pos"}` (what `analysis/processors/base.py::_score_negrw` loads).
- Training data: workflow `hww_genrw_train`, 2022postEE only (old DY -v2 and inclusive WtoLNu_2Jets), region `veto_emu_sr` (events NOT having exactly one eμ pair), genWeight-only weights; ~9.8M rows from 105 files. Run in coffea-base-almalinux9:0.7.30-py3.10 (sklearn 1.7.2 = processing workers).
- July closure was evaluated on the training rows themselves (no held-out set).

## What changes in v2
- Workflow `analysis/workflows/hww_genrw_train_v2.yaml` (new file; `hww_genrw_train.yaml` untouched): the same selections, `train` category, genWeight-only weights and no object shifts, but with `object_selection` and `corrections.object` copied **verbatim from `hww_allfix_4fs.yaml`** (tight_HWW muons + promptMVA, Medium electrons + ttHMVA_Run3, `tthMVA`, `jetveto`, `events.MET`). So `veto_emu_sr` is evaluated with exactly the allfix SR's leptons, and training events are disjoint from the allfix eμ SR by construction (N1). The July yaml used the old tight/wp80iso leptons, which would no longer guarantee that.
- Samples: the five `negrw:` datasets as the era YAMLs query them now (DYto2L_2Jets_10to50, DYto2L_2Jets_50, WtoLNu_2Jets_0J/1J/2J), **all four Run-3 eras pooled** (P+(x) is a generator property of amc@NLO FxFx and is the same across campaigns; pooling covers every era the model is applied to). The filesets already contained all keys, so no fileset edits were needed.
- Fit: identical recipe. Only change: rows with `event % 5 == 0` are **held out** from every member and used for closure, calibration and the old/new comparison.
- Scripts (new, `scripts/negrw/` in the analysis repo): `negrw_slim_v2.py` (parquets → one slim parquet with features, weight, era/dataset codes), `negrw_train_v2.py` (training + validation JSON), `negrw_train_v2.sub` + `negrw_train_v2_exec.sh` (one CPU Condor job in the workers' image), `negrw_n1_check.py`.

## Inputs: parquet production (capped)
Smoke test (in container, one 20k-event chunk, 2022postEE DY-50): all 20 features present, 0 eμ-pair rows, frac(w>0) = 0.835; pairless events are written with pdgId 0.

The runner submits every partition (~6000 for the 4 eras), far more than needed. Without touching the shared filesets:
`python3 runner.py --workflow hww_genrw_train_v2 --year <era> --eos --output_format parquet --nfiles 4 --memory 6000` (no `--submit`, builds condor dirs), then each `condor/hww_genrw_train_v2/<era>/<ds>/jobnum.txt` was trimmed to **2 partitions** (at ~1/4 and ~3/4 of the list, so different sites/files), the full list kept as `jobnum_full.txt`, and each `.sub` submitted with `condor_submit`.
**40 jobs (2 × 4 files × 5 datasets × 4 eras), clusters 9701384–9701405 (except 9701389 and 9701399, which are not these jobs)**, submitted 2026-11-12 ~00:16 CET.

> ⚠️ Do **not** run `jobs_status.py` resubmission or `runner.py --submit` on `hww_genrw_train_v2`: they would treat the ~6000 untrimmed partitions as missing and submit them all. Resubmit a failed partition by writing only its number into that cell's `jobnum.txt` and running `condor_submit` on the cell's `.sub`.

Outputs: `/eos/user/c/cgupta/higgscharm/outputs/hww_genrw_train_v2/<era>/<ds>_<partition>/train/*.parquet`.

**Input outcome (2026-11-12 01:10 CET):** 38/40 jobs exited 0. Two exited 1 partway with `OSError: XRootD error: [ERROR] Operation expired` at `root://redir.t2.ucsd.edu:1095` (grid site): 2022postEE DY-50 partition 316 (cluster 9701385.1) and 2022preEE DY-50 partition 99 (9701391.1). Their completed chunks are on EOS and were **used as they are, not resubmitted**: each parquet is a complete processor chunk, and the generator-level sample needs only to be representative, not complete.
Slim (`python3 scripts/negrw/negrw_slim_v2.py train …`, host python3): **7,595,624 rows** from 397 parquet files, 175 MB → `condor/hww_genrw_train_v2_model/train_v2.parquet`. Rows per era/dataset:

| era | DY 10–50 | DY 50 | W 0J | W 1J | W 2J |
|---|---|---|---|---|---|
| 2022preEE | 17,650 | 332,857 | 172,848 | 306,208 | 76,321 |
| 2022postEE | 17,103 | 546,378 | 305,916 | 405,451 | 376,213 |
| 2023preBPix | 17,753 | 1,325,008 | 308,141 | 559,511 | 415,991 |
| 2023postBPix | 22,675 | 940,342 | 645,447 | 328,889 | 474,922 |

So ~6.1M training rows after the 20% hold-out (July: 9.8M, no hold-out). DY 10–50 is small (75k rows), as in July (the trigger/lepton cuts remove most low-mass DY).

## Validation plan
- Held-out (event%5==0) closure Σ|w|g / Σw, total and per (era, dataset), with N_eff; calibration (observed vs predicted P+); log-loss/AUC train vs held-out (overfitting); g and δg distributions; old model on the same held-out rows.
- Allfix SR reference: the 2026-11-10 allfix TRAIN v1 SR parquets (`/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train_v1_20261110/<era>/<ds>_*/base/`), slimmed to `condor/hww_genrw_train_v2_model/sr_allfix_v1_20261110.parquet` (**17,627 V+jets SR events**, ~85% DY-50) with gen features and the old model's `weight_negrw`. Checks: the old model reproduces the stored column (sanity), new vs old g in the SR, SR closure, and feature coverage (SR events outside the training range).
- v1 vs the live Run A SR: v1 outputs were written 2026-11-10 18:40 CET, after commit 6451c52 (17:52). The later commits touching `hww_allfix_4fs.yaml` (9802054 channel_splits, 0d4a035 PDF rate lnN) change no object or event selection, so the SR comparison and N1 carry over to the live SR.

## N1 (training region vs allfix SR overlap)
- By construction: v2 uses the allfix lepton definitions, and `veto_emu_sr` is the negation of "exactly one eμ pair" → disjoint.
- **Empirical: PASS** (`python3 scripts/negrw/negrw_n1_check.py condor/hww_genrw_train_v2_model/train_v2.parquet condor/hww_genrw_train_v2_model/sr_allfix_v1_20261110.parquet`, 2026-11-12 01:15 CET):
  - v2 training rows 7,595,624: **eμ-pair rows 0**, same-flavour pair rows 496,411, pairless 7,099,213.
  - (era, dataset, event) matches against the 17,627 allfix SR V+jets events: 3, of which **0** have identical lhe_vpt and lhe_ht (event-number coincidences across different files, not the same physical event).
  - July training (9,832,308 rows) vs allfix SR 2022postEE: 79 event-number matches, 0 identical.
- July model: trained on different MC samples (2022postEE DY -v2 / inclusive W) from those the allfix SR uses (-v5 DY / jet-binned W), so there is no event overlap at all.

## Results
Training job **cluster 9701673** (submitted 2026-11-12 01:14 CET from `condor/hww_genrw_train_v2_model/`, `condor_submit negrw_train_v2.sub`; ran on b9g34p8811 01:24–01:40, exit 0, sklearn 1.7.2 / numpy 1.26.4 / pandas 2.3.3). Log: `condor/hww_genrw_train_v2_model/negrw_train_v2.9701673.out` (copy `…/negrw_out_img/v2_20261112/train.log`). Full numbers: `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/negrw_v2_validation.json`.

- Rows: 7,595,624 → train 6,078,637 / held-out 1,516,987; frac(w>0) 0.7996 train, 0.7993 held-out.
- All 20 members ran to max_iter = 200 (early stopping never triggered).
- **Overfitting: none.** Log-loss train 0.3800 / held-out 0.3806; AUC 0.8191 / 0.8181.
- **New vs July model on the same held-out rows:** log-loss 0.3806 vs 0.3803, AUC 0.8181 vs 0.8183, corr(g) 0.9987, mean |Δg| 0.0124; mean g 0.599 vs 0.602; mean ensemble spread δg 0.0078 vs 0.0075 (new δg p99 0.042, max 0.26). The July model already extrapolates fine to the new DY versions and jet-binned W.
- **Calibration** (observed frac(w>0) vs predicted P+, held-out): on the diagonal for both models; max |obs − pred| in bins with > 1000 rows 0.070 (new) / 0.062 (old), at P+ ≈ 0.62–0.74.

**Held-out closure Σ|w|g / Σw** (stat error = √Σw²/|Σw|):

| sample | n | v2 model | July model |
|---|---|---|---|
| total (all pooled, genWeight-weighted) | 1,516,987 | 0.9984 ± 0.0016 | 1.0031 |
| DYto2L_2Jets_10to50 | 14,960 | **0.898 ± 0.013** | 0.905 |
| DYto2L_2Jets_50 | 626,435 | 1.0080 ± 0.0019 | 1.0127 |
| WtoLNu_2Jets_0J | 286,893 | 0.9855 ± 0.0022 | 0.9886 |
| WtoLNu_2Jets_1J | 320,358 | 1.0086 ± 0.0036 | 1.0133 |
| WtoLNu_2Jets_2J | 268,341 | 1.0004 ± 0.0059 | 1.0096 |
| 2022preEE / 2022postEE / 2023preBPix / 2023postBPix | | 1.004 / 0.997 / 1.000 / 0.996 | 1.008 / 1.002 / 1.005 / 1.000 |

Per (era, dataset), the pattern is the same in every era (plot 04): DY-50 ≈ +0.7–1.0%, W 0J ≈ −1 to −2%, W 1J/2J within ±1.5%, DY 10–50 ≈ −7 to −13%. **Both models show the same per-sample offsets** (the v2 model about 0.5% lower everywhere). The cause is structural: the 20 features cannot tell the samples apart (no m_ll; jet bin only through lhe_njets), so a pooled P+(x) is the sample-averaged P+. **The analysis already renormalises each V+jets sample's reweighted template to its nominal yield** (decision [[Projects/HToWW/negative-weights/training/2026-07-17-closure-renormalization-decision|2026-07-17]]; `scripts/combine/make_combine_inputs.py:296-315`, `scripts/combine/build_cards_from_templates.py`), so these offsets cancel in the yields and only shape matters.
- Shape (held-out, lhe_vpt per dataset, 20 bins 0–400 GeV, rw_new / nominal): DY-50 mostly within ±2% with single bins at 1.043 (100–120), 1.058 (160–180) and 0.906 (200–240) (χ² 42/20, max pull 4.9); W 1J within ±3% except 0–20 GeV (0.916) and 220–240 GeV (1.081) (χ² 66/20); W 2J within ±4% (χ² 23/20); W 0J at its offset (~0.98) where populated. Residuals reach up to ~5σ pulls in these high-statistics samples; the July model has the same shape (plots 06).
- N_eff gain on held-out rows: 389k → 861k (×2.2); W 2J ×4.2, W 1J ×2.5.

**Allfix eμ SR** (17,627 V+jets events from the 2026-11-10 allfix TRAIN v1 SR parquets):
- Sanity check: the July model re-evaluated here reproduces the stored `weight_negrw` column to max |Δg| = 6.0e-8, so the SR gen features are exactly what the processor scored.
- frac(w>0) 0.707. g_new mean 0.409, δg mean 0.013, max 0.099. corr(g_new, g_old) 0.998.
- Closure: total **1.011 ± 0.025 (v2)** vs 1.0185 (July); DY-50 (16,132 ev) 1.007 vs 1.014; W 2J (1,016) 0.984 vs 0.995; W 1J (341) 1.080 vs 1.083; DY 10–50 (112) and W 0J (26) statistically empty. All within stat errors of 1 and renormalised per sample anyway.
- **Coverage:** no SR event lies outside the training min/max for any of the 20 features. The SR fraction above the training p99.9 is ≤ 3% (lhe_vpt 3.1%, lhe_ht 1.4%, genparton1_pt 1.2%; these are inside the range, so the SR leans to harder events) and < 0.5% for all others. No extrapolation.

### Plots
- tags: [plot] · Date: 2026-11-12 · Description: negrw v2 validation plot set (loss curves, held-out calibration, g distributions held-out and allfix SR, closure per era×dataset new vs July, binned held-out closure in lhe_vpt/lhe_ht/lhe_njets/lhe_npnlo/genparton1_pt/lhe_nc, lhe_vpt per dataset, SR lhe_vpt, δg)
  - Path: `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/img/`
  - Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/img
- Key files: `02_calibration_holdout.png`, `04_closure_holdout_era_dataset.png`, `06_vpt_holdout_<dataset>.png`, `03_g_allfixSR.png`, `07_sr_vpt.png`. Script: `scripts/negrw/make_negrw_v2_plots.py <training out dir> <plot dir>`.

### Recommendation
- The v2 model is **fit for use**: trained on exactly the samples (versions, jet-binned W, 4 eras) and lepton definitions the analysis now uses, with held-out closure and calibration, no overfitting, full feature coverage of the SR, and N1 disjointness shown by construction and empirically.
- Keeping the July model would also be defensible (same performance, g correlation 0.998). The reason to switch is provenance: the July model was trained on superseded samples (2022postEE only, DY -v2, inclusive W) with the old lepton IDs, and evaluated closure only on its own training rows.
- Switching is a one-line change of `negrw.model` in `hww_allfix_4fs.yaml` (not done here, per brief). Since negrw is weight provenance only (not in the TRAIN hash, commit f84d311), it does not invalidate TRAIN outputs; it changes RUN-stage `weight_negrw` values (by ~0.012 per event on average).
- The `CMS_negrw_vjets` shape nuisance (ensemble spread) stays the same size (δg mean 0.0078 vs 0.0075).

### Open issues
- DY 10–50 closes at ≈ 0.90 for both models (the features can't separate it from DY-50). Harmless after per-sample renormalisation, and DY 10–50 has 112 events in the SR, but adding m_ll (or a sample flag) as a feature would be the fix if it ever matters. Would need a processor feature change (frozen now).
- Two of the 40 input jobs were partial (grid XRootD expiry, see above). They were used as they are; resubmission was not needed for the sample size.
- Not independently reviewed; the SR comparison uses the 2026-11-10 allfix v1 parquets (selection-identical to the live Run A, see above), not the live Run A outputs.

## Model
- **New model:** `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models_v2_20261112.joblib` (7.97 MB), sha256 `af53567ccfeddeef94c1fa62b3a6ed3c1285937919ced3f7705c565b819155cb`. Identical copies (same sha256): `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/negrw_models_v2_20261112.joblib` and the job output `condor/hww_genrw_train_v2_model/out/`.
- Bundle keys `models, features, n_models, frac_pos` (same schema `_score_negrw` loads) + `meta` (workflow, eras, datasets, hold-out rule, hyperparameters, sklearn 1.7.2). Loaded in the coffea-base-almalinux9:0.7.30-py3.10 container from AFS and scored SR rows: OK.
- Old model unchanged: `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models.joblib`, sha256 `05567a8c0762b3446e8837c7825e30406637127a6143b331a968a42bcf707417`. `negrw.model` in `hww_allfix_4fs.yaml` unchanged.
- Analysis repo commits (lxplus, local, not pushed): `7c1738b` (v2 workflow + scripts/negrw), `0995853` (plot script).
