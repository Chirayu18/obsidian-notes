---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# negrw retraining v2 (2026-11-12): current DY / jet-binned W+jets, 4 Run-3 eras

**Status: agent-reported, IN PROGRESS.** Input (parquet) jobs submitted and queued; no training yet.
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
_Pending: training job cluster 9701673 (submitted 2026-11-12 01:14 CET from `condor/hww_genrw_train_v2_model/`)._

## Model
New model will be written to `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models_v2_20261112.joblib` (+ copy in `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/`). The old `negrw_models.joblib` and `negrw.model` in `hww_allfix_4fs.yaml` stay unchanged.
