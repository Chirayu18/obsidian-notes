---
tags: [reference, review]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# negrw v2 acceptance review (resumed): hold the switch until two operational gates are met; no defect found in the model

**Reviewer:** c1 Claude Opus, fresh bounded review resumed on 12 Nov 13:04 after the interrupted run ([[Projects/HToWW/negative-weights/2026-11-12-negrw-acceptance-review-handoff|handoff]]). Uses the `htoww-review` skill and [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|protocol]]. Read-only for analysis/config/models: no retraining, no model switch, no job submission, no analysis-code edit. Reviewed claims: [[Projects/HToWW/negative-weights/2026-11-12-negrw-retraining|negrw retraining v2]] (author note, agent-reported). This review is itself agent-reported.

## Recommendation

**HOLD the production switch for now. Do not reject v2.** Adopting v2 as the replacement for the July model is supported once gates G1 and G2 (below) are met. Neither gate is a physics change.

- **No software or training defect found in v2.** On the current samples it closes as well as or better than the July model. On independent held-out events its shape residuals are comparable in DY‑50 and smaller in W 0J/1J/2J (F2). Its training uses the allfix lepton definitions, so N1 holds by construction for nominal objects.
- **G1: freeze the training-input provenance.** The model bundle records no input hash or manifest, and the slim was built by globbing live EOS directories. The author note also lists `train_v2.parquet` as a cleanup candidate. Before adoption, store the manifest and the parquet hash with the model (this review produced both; see below). Keep `train_v2.parquet` until that is done.
- **G2: one negrw model per production.** RUN-output provenance does not record which negrw model scored each chunk, so a merge cannot detect chunks scored by different models. After the switch, either (a) add the model SHA-256 to RUN provenance (needs separate code authorization), or (b) rerun all V+jets RUN chunks of every era with the new model and check that the stored `weight_negrw` matches the new bundle on a sample.
- **Not resolved, and it applies to both models:** after the approved per-(era, dataset) renormalization, the held-out data show statistically significant shape residuals. They are about 1–2.5% in SR-like DY‑50 and up to 17% in W bins, more than the `CMS_negrw_vjets` ensemble nuisance covers (F2). So **neither the old nor the new model is shape-validated.** This does not favour keeping the July model, which has the same or larger residuals. Whether the bias matters at the precision of the fit observable is a separate open item (G3, next steps). It needs Chirayu's decision on a prescription, not a reviewer-invented fix.
- This note does not accept either model and does not approve any feature addition.

## Review manifest

| item | value |
|---|---|
| Analysis repo | `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `0995853c0a5aa45fda4ff3ee21129e993a6c1c5f` (snapshot 2026-11-12 13:13 CET) |
| Dirty tracked files | `scripts/mva/bhive_fold_commands.py`, `scripts/mva/register_folds.py`: owned by the b-hive agent and not touched here. The `register_folds.py` diff adds `--diagnostic_only` and does not change `external_inputs` or negrw. Untracked backups: unchanged. |
| Files in scope (sha256, first 12) | `scripts/negrw/negrw_train_v2.py` 759023fbd21c (identical to the copy in the condor dir); `negrw_slim_v2.py` 978c33825cb2; `negrw_n1_check.py` 2f193238e123; `make_negrw_v2_plots.py` b6820e7dd66a; `analysis/workflows/hww_genrw_train_v2.yaml` e735ebef000f; `hww_allfix_4fs.yaml` 582316b2629a; `analysis/processors/base.py` 57c49705d080; `analysis/sinks/hww.py` a9fdf93df937; `analysis/features/hww.py` c524acfe85f0; `scripts/combine/make_combine_inputs.py` a95cfd9ed3ea; `scripts/combine/build_cards_from_templates.py` d9b5e43c470b |
| New model | `/afs/cern.ch/user/c/cgupta/negrw_model/negrw_models_v2_20261112.joblib`, sha256 `af53567c…19155cb`. Re-hashed: AFS copy and condor `out/` copy are identical. |
| July model (production, unchanged) | `/afs/…/negrw_model/negrw_models.joblib` sha256 `05567a8c…f707417`; `negrw.model` in `hww_allfix_4fs.yaml` still points to it |
| Training input | `condor/hww_genrw_train_v2_model/train_v2.parquet` sha256 `f603ef6de8f30dc873615eddadba63684ebd64fc0e0b7c830a8e19213e7cc412` (174,764,220 B, mtime 01:13:51; training submitted 01:14) |
| SR reference | `…/sr_allfix_v1_20261110.parquet` sha256 `4e34a0fffada…` (from v1 TRAIN SR parquets written 2026-11-10 18:22–18:48, after `f1e2016`) |
| Author outputs | `out/negrw_v2_validation.json` sha256 `e6918b6c4e84…`, training log `negrw_train_v2.9701673.out` (cluster 9701673, b9g34p8811, sklearn 1.7.2, numpy 1.26.4, pandas 2.3.3, seed 0, member seeds 0–19) |
| Reviewer environment | `coffea-base-almalinux9:0.7.30-py3.10` via apptainer on lxplus (`OMP_NUM_THREADS=4`, `-B /afs -B /cvmfs`); host `python3` + pyarrow for EOS listings (the container cannot read `/eos/user`) |
| Reviewer scratch | `~/negrw_review_20261112/` on lxplus AFS (scripts, JSON outputs and sha256 listed under "Checks") |

## Findings

### F1. Author closure uncertainties and pulls use the wrong variance (reported statistic, not analysis code)
- **Trigger:** `negrw_train_v2.py::closure` quotes `ratio_staterr = sqrt(Σw²)/|Σw|`, the uncertainty of the denominator only. The pulls and χ² in the author note (DY‑50 "χ² 42/20, max pull 4.9") use the same nominal-only variance. The reviewer reproduced them exactly from the saved JSON (42.1/20, 4.92; interrupted thread, activity 30).
- **Expected:** for R = Σ|w|g / Σw on the same events with g fixed, the delta-method variance is Σ(|w|g − R·w)² / (Σw)². This accounts for both numerator and denominator and for their correlation.
- **Observed** (held-out rows, `check_negrw_v2_out.json`, reviewer-run): the correct errors are smaller and the offsets are significant. Columns: R ± quoted error / correct error, significance (R − 1)/σ, and the spread of R across the 20 ensemble members.

| sample | v2: R, σ quoted / σ correct | (R−1)/σ | member s.d. of R | July: R, (R−1)/σ |
|---|---|---|---|---|
| total | 0.9984, 0.0016 / 0.0012 | −1.4 | 0.0006 | 1.0031, +2.7 |
| DY 10–50 | 0.8980, 0.0139 / 0.0091 | −11.2 | 0.0012 | 0.9048, −10.4 |
| DY 50 | 1.0080, 0.0019 / 0.0012 | +6.5 | 0.0005 | 1.0127, +10.3 |
| W 0J | 0.9855, 0.0022 / 0.0011 | −13.2 | 0.0006 | 0.9886, −10.4 |
| W 1J | 1.0086, 0.0036 / 0.0028 | +3.1 | 0.0014 | 1.0133, +4.8 |
| W 2J | 1.0004, 0.0059 / 0.0051 | +0.1 | 0.0027 | 1.0096, +1.8 |

- **Meaning:** the per-sample offsets are real held-out biases of the realised model, 3–13σ. They are 5–20× the member-to-member spread, so they come from systematic model or pooling bias, not training statistics. The author's statement "all within stat errors" applies only to the SR (17,627 events, σ ≈ 0.021). The approved per-sample renormalization removes these offsets from template yields; it does not remove shape bias (F2).
- **Classification:** validation-statistic error in the author script and note. No analysis/production code is affected.

### F2. Shape residuals after the approved renormalization exceed the ensemble nuisance (both models)
- **Method** (`resume_shape_cov.py`, this session, both models on the same 1,516,987 held-out rows):
  - Each (era, dataset), or (era, dataset, subset), is renormalized with k = Σw/Σ|w|g over **all** its events, as the analysis does per sample. All events are binned, including underflow, overflow and a NaN bin.
  - Covariance: c_ib = (k·a_i − w_i)(1[i∈b] − A_b/A), with a_i = |w_i|g_i. This includes the shared events between the signed and reweighted histograms and the fitted normalization. It is summed over independent eras, and χ² = rᵀC⁺r is taken on the non-null eigenspace (ndf = rank = populated bins − 1). The model is held fixed, which is correct for testing the realised model on independent events.
  - "With nuisance" adds ΔΔᵀ, where Δ is the per-era-renormalized `CMS_negrw_vjets` Up − nominal shift. That is one Gaussian-constrained shape parameter, as in the cards.
  - Toy check of the formula under the null: ⟨χ²⟩ = 5.006 at rank 5 (`resume_toy_cov_check.out`).
  - The interrupted run's `shape_after_renorm_out.json` (normalized in-range, k fixed) overstated some χ² values; for example W 0J `lhe_vpt` was 692/6 there and is 95/5 here. It is superseded.
- **DY‑50** (91.5% of SR V+jets events). Columns: χ²/ndf (p), the same with the nuisance added, mean |relative residual| vs mean |relative nuisance|, and the largest bin.

| variable / subset | v2 | v2 + nuisance | July | mean \|resid\| vs \|nuis\| (v2) | largest bin (v2) |
|---|---|---|---|---|---|
| lhe_vpt / all | 29.5/20 (p 0.08) | 25.5 (p 0.18) | 26.0/20 | 0.42% vs 0.54% | 60–80 GeV −2.6% (−2.6σ) |
| lhe_vpt / lhe_njets ≥ 1 (SR-like; SR is 99.6% ≥1) | 47.2/20 (p 5e-4) | 35.0 (p 0.02) | 47.9/20 | 1.2% vs 0.50% | <20 GeV −2.4% (−4.9σ, 18% of events; nuis 1.0%) |
| lhe_ht / lhe_njets ≥ 1 | 110/10 (p 5e-19) | 26.5 (p 0.003) | 92.9/10 | 0.92% vs 0.57% | 60–100 GeV −2.2% (−3.2σ; nuis 0.3%) |
| genparton1_pt / lhe_njets ≥ 1 | 22.8/9 (p 0.007) | 22.3 (p 0.008) | 34.0/9 | 1.0% vs 0.45% | 100–150 GeV +3.8% (+2.8σ; nuis 0.6%) |
| SF-pair subset: vpt / ht / g1pt / njets | 20.7/20, 6.9/10, 16.7/10, 4.6/3 | — | 22.3, 7.4, 22.1, 15.2 | consistent | — |

- **W+jets and DY 10–50** (8.5% of SR V+jets), v2 model: W 1J `lhe_vpt` 139/20 → 120 with the nuisance; residuals −9.2% (<20 GeV), +2.1%, −2.2%, against a mean nuisance of 0.3%. W 1J `lhe_ht` 114/8 → 106 (+5.7%, −4.4%). W 2J `genparton1_pt` 59.8/9 → 59.7 (+6.9% at 150–200 GeV, +17% at 300–500 GeV). W 0J `lhe_ht` 159/4 → 52 (≈1% residuals). DY 10–50 `lhe_njets` 71/3 → 34 (+7.3% at njets 0, −17% at njets 2).
- **New vs July:** the χ² values are comparable for DY‑50 (better for `genparton1_pt` and `lhe_njets`, slightly worse for `lhe_ht`, equal after the nuisance) and smaller for W 0J/1J/2J (for example W 1J `lhe_vpt` 139 vs 186, W 0J `lhe_ht` 159 vs 291). **On this evidence v2 is not worse than the production model anywhere material.**
- **Interpretation:**
  - After per-sample renormalization, both models leave held-out generator-level shape residuals that are statistically significant. They are about 1–2.5% in DY‑50 within the SR-like `lhe_njets ≥ 1` phase space and 2–17% in W 1J/2J. `CMS_negrw_vjets` covers them partly in DY‑50 (p 0.003–0.02 after the nuisance) and essentially not at all in W. As expected, the ensemble spread measures member-to-member variance, not common bias.
  - Per-sample normalization restores totals, not arbitrary shapes.
  - Whether these generator-level residuals matter for the fit is not established. They have to be propagated to the eμ + c-jet SR discriminant, where V+jets has N_eff ≈ 5,300 (author SR numbers) and per-bin MC-stat is larger. That is gate G3. Under the realised-model hypothesis, these are significance statements about the training-region distribution, not SR significances.
- **Status:** checked (reviewer-run). The pulls and χ² in the author note are superseded.

### F3. negrw model identity is not part of RUN-output provenance (guard gap; source-established, no mixed production found) → gate G2
- **Trace:** `analysis/features/hww.py:126-139` `external_inputs(cfg)['weights']` records `negrw:<path>` → sha256. Its only non-test consumer is `scripts/mva/register_folds.py:116`, which writes it into the fold `meta.yaml` **at registration time**. RUN provenance (`analysis/processors/base.py:139-146`) records mode, year, `features_hash`, `selection_hash`, folds, `model_manifest_hash` and Route B stitching. It records **no negrw identity**. Since `f84d311`, the negrw path is excluded from `selection_signature` (`features.hww:46-58`, covered by `test_external_inputs.py::test_selection_change_changes_hash_weight_change_does_not`). `build_cards_from_templates.py::merge_outputs` refuses mixed provenance values and `normalize_record` refuses mixed negrw on/off flags, but neither can see which model was used. `_score_negrw` (`base.py:366-398`) loads `negrw_cfg["model"]` by path with no hash check. Nothing in `analysis/models/registry.py` or `analysis/processing_modes.py` references negrw.
- **Consequence:** if `negrw.model` changes between RUN submissions or resubmissions of one production, chunks scored by the July and v2 models merge without error. The fold `meta.yaml` then records whichever model existed at registration, which can disagree with what RUN used. Overwriting the file at the same path would also go undetected.
- **Status:** this is a gap established from the source, not a reproduced numerical defect. The production configuration has never changed models, so no current output is known to be mixed. It becomes a real hazard at the switch. The reviewer did not edit shared code. `register_folds.py` belongs to the b-hive agent.

### F4. Training-sample provenance: reproducible today only through the frozen parquet; manifest now recorded → gate G1
- `negrw_slim_v2.py` globs the **live** EOS tree `hww_genrw_train_v2/<era>/<ds>_<n>/train/*.parquet`, and the bundle `meta` records no input hash or file list. Rerunning the slim after any resubmission of partitions 99/316 would give a different training set without any warning. The analysis also cannot reproduce the partition→file mapping, because filesets are regenerated (`f84d311`) and `jobnum.txt` was trimmed by hand.
- **Reviewer manifest** (`resume_input_manifest.json`, sha256 `a76a5e2f…`): 377 chunk files across 40/40 partitions, with name (NanoAOD uuid + entry range), size, mtime and row count. The total is **7,595,624 rows, identical to the slim both in total and per (era, partition). No chunk is newer than the slim.** Every partition contributed all 4 of its NanoAOD files. The only interior entry-range gaps are in the two failed partitions: preEE DY‑50_99 is missing `[0, 85716)` of one file, and postEE DY‑50_316 is missing `[0, 87506)` and `[93646, 187292)` of two files. Missing trailing chunks cannot be detected without per-file entry counts.
- **Discrepancy:** the author note says the slim read "397 parquet files". EOS holds 377 chunk files and the reviewer could not reproduce 397. The row counts match exactly, so this looks like a reporting slip, not a data difference. No slim log is saved.
- **Duplicates:** no overlapping entry ranges within any uuid, and no uuid in two partitions (`overlap_files_out.json`, interrupted run). The 191 rows that share (era, dataset, event, five gen features) are all `lhe_njets = 0` events, whose LHE kinematics are all zero. None of them is identical across all columns (`dup_rows_all_columns = 0`), so they are distinct events with colliding event numbers, not duplicated chunks.
- **Representativeness of the partial jobs:** held-out closure for the failed partitions vs the rest of the same era/dataset: preEE 1.0027 vs 1.0102 (Δ = −0.0075 ± 0.0076), postEE 1.0062 vs 1.0083 (Δ = −0.0021 ± 0.0059). Row yields match the complete partner partitions (160,240 vs 172,617; 282,692 vs 263,686). MC files within a dataset are exchangeable at generator level, and the missing chunks are entry ranges, not kinematic selections. **The sample is intentionally file-sampled and needs no completion. Excluding or recovering the partial jobs is not needed.**
- **Hold-out:** `event % 5 == 0` per row. The held-out fraction is 0.193–0.203 in all 20 (era, dataset) cells, and frac(w>0) is 0.7996 train vs 0.7993 held-out. Event numbers repeat across files, so the split is deterministic per physical event but is not a per-file split. That is acceptable for an i.i.d. generator sample.

### F5. N1 (training region vs eμ SR): logically guaranteed for nominal objects at the same code version; empirically confirmed on shared chunks
- **Logical:** `hww_genrw_train_v2.yaml` `object_selection` and `corrections.object` are equal to `hww_allfix_4fs.yaml` (YAML dict equality, interrupted run, activity 22). `veto_emu_sr = ~fill_none((num(ll_pair)==1) & firsts(eμ), False)`. The allfix `base` category requires `one_ll_pair & one_muon_one_electron`, so a nominal SR event cannot pass the veto. Lepton smearing uses the per-object deterministic RNG from `f1e2016`. Between `f1e2016` (11-10 18:00) and HEAD, no commit touches `analysis/{corrections,selections,working_points,leptonmva,data}` (per-commit `git show --stat`). `base.py` changes are the channel split (`9802054`) and Route B (`eaab247`, inactive without a `stitching:` block; inspected via the commit stat and the gate in `base.py:62-73`, not line-reviewed). The `hww_allfix_4fs.yaml` diff `f1e2016..HEAD` adds only `channel_splits` and `xsec_hplusc_PDF`. The v1 SR parquets were written 18:22–18:48 on 11-10, after `f1e2016`. The v2 training jobs ran 12 Nov 00:16–01:10 on the same object code. **So the guarantee carries over to the v1 SR and to a live RUN at HEAD.**
- **Empirical:** 86 (uuid, entry-range) chunks were processed by both v2 training and the v1 SR. They hold 196 SR V+jets events and 2,801,092 training rows, with **0 event-number matches within those chunks** (`n1_shared_chunks.py`, interrupted run). The same physical event must share its event number within a chunk, so this test is conclusive for those 196 events (1.1% of SR V+jets). The author's (era, dataset, event) + `lhe_vpt`/`lhe_ht` key is weaker: 36% of training rows have all-zero LHE kinematics. It is adequate for the SR, where `lhe_njets ≥ 1` for 99.6% of events.
- **Scope limit:** the training region uses nominal objects only (`object_shifts: false`). In RUN, muon/electron scale-smearing shifts can move a nominally vetoed event into a shifted SR template, so disjointness is guaranteed for the nominal and JES/JER/MET shifts only (the veto uses leptons only). The impact is negligible: held-out vs train log-loss is 0.3806 vs 0.3800, and the 6.1M training rows make single-event leverage tiny. The claim should still read "disjoint at nominal", not unconditionally "by construction". The July model has no event overlap, because it was trained on different MC samples.

### F6. Sign target, unweighted fit, |genWeight| and pooling
- **|w| is one constant per (era, dataset)** in all 20 cells (`n_unique_absw = 1`, `check_negrw_v2_out.json` A). So the unweighted classifier on `w > 0` estimates the same P₊(x) as a |w|-weighted fit within a sample, and E[|w|·g | x] = E[w | x] holds per sample **if** P₊ is correct.
- **Pooling** of 5 datasets × 4 eras in one unweighted fit estimates the count-weighted mixture P̄₊(x) = Σ_s π_s(x) P₊,s(x). That is exact for sample s only if P₊,s(x) = P̄₊(x). Era pooling is supported: frac(w>0) per dataset agrees across eras to within 0.005 (DY‑50 0.8317–0.8328, W 0J 0.9160–0.9183). Dataset pooling is where it fails measurably. The per-sample offsets in F1 have the sign pattern expected from mixing: DY 10–50 cannot be separated from DY‑50 with gen features that carry no dilepton mass. They are not explained by ensemble variance.
- This is a **limitation of the approved July recipe** (pooled, unweighted, generator-only, `g = 2P₊ − 1`, arXiv:2510.16217 Eqs. 2–6). It is not a v2 implementation bug. The approved remedy is per-sample renormalization ([[Projects/HToWW/negative-weights/training/2026-07-17-closure-renormalization-decision|2026-07-17 decision]]). It restores per-sample totals only. The reviewer did not invent a sample-conditioned recipe.

### F7. Feature support and conditional transfer
- **Marginal:** no SR event lies outside the training min/max (author). That is necessary but not sufficient.
- **Coarse joint check** (interrupted run, `check_negrw_v2_out.json` C): SR events were binned in 7-dimensional cells (lhe_njets, lhe_npnlo, lhe_nc, lhe_nb, and training deciles of lhe_vpt, lhe_ht, genparton1_pt). No SR event sits in an empty training cell. 0.12% sit in cells with fewer than 10 training rows and 1.3% (1.5% of SR |w|) in cells with fewer than 100. The open-ended top deciles and the omitted features (η, second parton, incoming flavours) make this a coarse screen, not a proof of joint support.
- **Missing-value conventions** agree between the training parquet (legacy `dump_parquet`) and SR scoring (TRAIN sink). The NaN fraction of `genparton1_pt` equals the zero fraction of `lhe_njets` (0.3609/0.3609 train, 0.0044/0.0044 SR). The July model re-evaluated on SR parquet features reproduces the stored `weight_negrw` to within 6e-8 (author).
- **Transfer to the reconstructed eμ selection** is assumed: given x, P₊ should not depend on the reco selection. It is tested only weakly. Held-out DY‑50 SF-pair events close at 0.9962 ± 0.0052 vs 1.0095 ± 0.0012 for pairless events (Δ = −0.013 ± 0.005, 2.5σ). The SR closure is 1.011 ± 0.021 (correct σ). This is suggestive, not established. Per-sample SR renormalization absorbs any such normalization dependence, but not a shape dependence.

### F8. Downstream per-sample renormalization: implemented as approved in RUN and legacy paths, including variations
- **RUN:** `analysis/sinks/hww.py:87-134` `make_templates` stores additive `norm_raw = Σ nominal` and `norm_rw = Σ|nominal|·g` per variation record. For weight variations it uses `(w_var, g)` with the **nominal** normalization sums, which keeps the relative effect of the variation. For `CMS_negrw_vjetsUp/Down` it uses `(nominal, clip(g ± δg))` with its own `norm_rw`, which makes it shape-only. Object shifts get `weight_map = {shift: nominal_shift}`, normalized to the shifted pass's own yield, which keeps the shift's rate effect. `build_cards_from_templates.py:47-58` `normalize_record` applies `norm_raw/norm_rw` once per accumulated record after summing all chunks. Records are keyed per sample (`dataset_info` strips the `_<n>` partition suffix) and per era output, and they sum over all argmax channels and splits. So the normalization is **per (era, dataset) over the SR category**, as decided on 2026-07-17.
- **Legacy:** `scripts/combine/make_combine_inputs.py:292-299` computes the renorm from the whole per-(sample, year) parquet across channels. Line 315 applies it to every weight variation. Lines 329-344 renormalize the negrw Up/Down to the nominal yield. Lines 571-590 recompute it within each object-shift parquet.
- **Status:** checked against the source by the reviewer. Unit coverage: author-run test log, not re-executed by the reviewer. That log is the 118/118 suite run after all commits (`test_trainrun_blockers`, `test_channel_split`, `test_external_inputs`, …; [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train]]). The tested code is unchanged since (`features/hww.py`, `sinks/hww.py` and the card builders were last changed at or before `3a03245`; HEAD adds only the plot script).
- **Switch consistency:** `negrw.model` is in neither `features_hash` nor `selection_hash`, so switching does not invalidate TRAIN outputs or fold models. This is intended (`f84d311`). It changes only RUN `weight_negrw`, and gate G2 covers the resulting provenance gap.

### F9. Proposed dilepton-mass or sample-flag feature: not appropriate as stated; no follow-up needed for adoption
93.5% of training rows are pairless (7,099,213 / 7,595,624). A reconstructed m_ll is undefined for them, and as a reco-level, selection-dependent feature it would break the generator-only recipe. A generator-level V mass or a per-sample flag would be a new prescription and needs Chirayu's decision. Per-sample renormalization already handles the DY 10–50 normalization offset. DY 10–50 contributes 112 of the 17,627 SR V+jets events. No feature change is approved or needed for this decision.

## Evidence table

| Item | Approved prescription and source | Implementation and revision | Independent check / command | Observed result and saved output | Status |
|---|---|---|---|---|---|
| Recipe | July recipe: 20 features, 20× HGB, 60% subsamples, `w>0` label, unweighted (author note; `RESUME-condor-retrain`) | `scripts/negrw/negrw_train_v2.py` 759023fbd21c @`7c1738b`, same file in condor dir | source read; train log | recipe identical; only the event%5 hold-out is new; all members ran to 200 iterations | checked (source + author log) |
| \|w\| per sample | assumption of the unweighted fit | — | `check_negrw_v2.py` A | 1 unique \|w\| in 20/20 cells | checked |
| Pooling | approved pooled fit + per-sample renorm (2026-07-17) | — | F1 table | per-sample offsets 3–13σ, both models | limitation of the approved recipe |
| Training sample | file-sampled, representative | `negrw_slim_v2.py` 978c33825cb2 (live EOS glob, no manifest) | `resume_input_manifest.py` (host) | 377 chunks, 7,595,624 rows = slim; 3 interior gaps, all in the failed partitions; author's "397 files" not reproduced | checked; G1 open |
| Partial jobs | — | — | partial vs rest closure | Δ within 1σ | checked: no recovery needed |
| Hold-out closure σ | — | `closure()` uses √Σw²/\|Σw\| | delta-method σ (`check_negrw_v2_out.json` B) | quoted σ ≈ 1.3–2× too large; offsets significant | author statistic wrong (F1) |
| Shape after renorm | 2026-07-17: per-dataset yield renorm; `CMS_negrw_vjets` = ensemble spread | sinks/hww.py, card builders | `resume_shape_cov.py` (fitted-k covariance, toy-validated) | see F2 | significant residuals, not covered by the nuisance (both models); G3 open |
| N1 | disjoint training/SR (audit N1) | v2 yaml objects equal allfix; `veto_emu_sr` | YAML equality; git history; 86 shared chunks | 0 shared events among 196 SR events; nominal-only guarantee | checked; scope: nominal |
| Support | no extrapolation | — | coarse 7-D joint cells | 0% of SR in empty cells; 1.3% in cells with <100 rows | coarse screen only |
| Downstream renorm | 2026-07-17 decision | sinks/hww.py:87-134; build_cards:47-58; make_combine_inputs:292-344, 571-590 | source trace | per (era, dataset), all variations as intended | checked; unit tests: author-run log (118/118), not re-executed |
| negrw identity in RUN | (none written) | features/hww.py:126-139 → register_folds only; base.py:139-146 | source trace | identity not in RUN provenance | guard gap (source); G2 |
| Old vs new | — | — | paired difference on the same held-out events | new − old closure −0.003 to −0.009 per sample (paired σ ≤ 0.0003); SR −0.0075 ± 0.0006 | checked |

## Checks actually run

Executed by the reviewer. The interrupted run (activities 30–75 of the failed review thread) is cited where marked. Nothing was submitted to Condor.
- `~/negrw_review_20261112/check_negrw_v2.py` (sha256 ccf228bf…) → `check_negrw_v2_out.json` (efdc502c…). Container, 4.5 min, interrupted run. Covers |w| structure, duplicates, held-out closure with correct σ, member spread, pairless/SF subsets, partial partitions, binned pulls, SR closure, feature conventions and joint cells. Its part D (EOS listing) returned nothing because the container cannot read EOS; it was superseded by the next item.
- `overlap_files.py` (de3e2551…) → `overlap_files_out.json` (b474ac50…); `n1_shared_chunks.py` (3383206b…). Host, interrupted run.
- `shape_after_renorm.py` (86676d54…) → `shape_after_renorm_out.json` (d3e22374…). Interrupted run. **Not used as an acceptance statistic:** it normalized within the displayed x-range (dropping overflow and NaN) and treated k as fixed in the variance. It is superseded by the next item. Its raw pulls and χ² are not final significances.
- **This session:** `resume_toy_cov_check.py` (e0349a5e…) → `.out` (41d200cb…). 3000 toys under the null: ⟨χ²⟩ = 5.006 at rank 5 with the fitted-k covariance vs 5.74 with fixed-k diagonal; empirical/formula variance ratio 0.97–1.05.
- **This session:** `resume_shape_cov.py` (4dcea11e…) → `resume_shape_cov_out.json` (704760c4…); summary `resume_shape_summary.py` (793e6f12…) → `.out` (5eaaaaf6…), log `resume_shape_cov.log`. Held-out scores are cached in `resume_holdout_scores.npz` (~24 MB, regenerable reviewer scratch; deletion needs Chirayu's OK like any other).
- **This session:** `resume_input_manifest.py` (c339bd03…) → `resume_input_manifest.json` (a76a5e2f…). Host.
- Source and git inspection as cited in F3, F5 and F8. sha256 of models and inputs re-taken (manifest table).

Not re-executed: author unit tests (cited log), the author's training, slim and N1 scripts, and the plots.

## Limits
- All held-out checks are in the generator-level training region, which is 93.5% pairless. Transfer to the eμ + c-jet SR is tested only to about ±2% in normalization (SR closure) and through one 2.5σ hint (SF-pair vs pairless DY‑50). No check was done on the b-hive discriminant or fit observable: the training region has no event-MVA scores, and the slim SR file has none either.
- The joint-support check is coarse. Event identity in N1 relies on chunk identity plus event number.
- The fixed-model variance tests the realised model. It does not include retraining variance, which is small (member spread, F1).
- This review does not validate either model for physics use.

## Next steps (targeted; no retraining needed)
1. **G1 (owner: parent/author, no physics change):** copy `resume_input_manifest.json` and the `train_v2.parquet` sha256 next to the model on EOS (`negrw_out_img/`) and add them to the bundle metadata or a sidecar. Keep `train_v2.parquet` until then; do not delete it as "cleanup". Correct the "397 files" statement.
2. **G2 (owner: Chirayu to choose):** (a) authorize a small code change adding `negrw_model_sha256` to RUN provenance, so `merge_outputs` refuses mixed models, plus a test; or (b) if switching, rerun all V+jets RUN chunks of every era after the switch and verify the stored `weight_negrw` against the v2 bundle on one chunk per (era, dataset).
3. **G3 (shape-bias decision, both models):** run a closure check on the fit observable using scored SR V+jets events with `weight_nominal`, `weight_negrw` and `weight_negrw_std` (a RUN `--slim_ntuple` output or a legacy `mva/` parquet). In each final channel and bin, compare the signed nominal template with the renormalized |w|g template, using the fitted-k covariance from `resume_shape_cov.py`. Compare the residual against `CMS_negrw_vjets` and the template MC-stat. If the bias is not covered, Chirayu decides the prescription (for example, an additional closure-derived shape nuisance). The reviewer proposes none here.
4. Fix the uncertainty formula in `negrw_train_v2.py::closure` and the plot script before any re-validation. This is author-owned and needs separate authorization.
5. In the author note, reword N1 as "disjoint at nominal objects; lepton-scale shifted templates are not covered (negligible impact)".
