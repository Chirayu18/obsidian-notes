---
tags: [reference]
status: active
date: 2026-11-12
source: lxplus
evidence: agent-reported
---

# negrw v2 follow-up: G1 inputs frozen, G2 RUN model identity guard, corrected closure/shape statistics

**What this is.** The bounded G1/G2/reporting scope in [[Projects/HToWW/negative-weights/2026-11-12-negrw-review-followup-proposal]], approved by Chirayu ("Yes do all that, I need things done soon", [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-afternoon-approved-followups]]). It addresses findings F1, F3 and F4 of [[Projects/HToWW/negative-weights/2026-11-12-negrw-v2-acceptance-review]] and reports F2 with corrected statistics. It was run by a Claude 2 worker after the c1 worker `e9268642…` hit the API rate limit. **Agent-reported.** The tests below were run by this worker. Nothing here has been validated by Chirayu or an independent reviewer.

**Not changed:**
- No `negrw.model` or config switch. Both `hww_allfix_4fs.yaml:74` and `hww_routeb_3fs4fs.yaml:100` still point to the July model `negrw_models.joblib` (`05567a8c…`).
- No change to features, recipe or nuisances.
- No training, no jobs submitted, nothing deleted.
- `scripts/mva/*`, b-hive files and filesets were not touched.

**The switch stays on hold.** G3 (closure in the scored SR fit bins) is still open, and neither the July model nor v2 is shape-validated.

## State found before starting

The previous c1 worker left no partial files:
- the tracked tree was clean at `8535275` (b-hive commit);
- `~/negrw_review_20261112/` held only reviewer files;
- `negrw_out_img/v2_20261112/` held only the author outputs.

`analysis/filesets/2023preBPix_nanov12.yaml` was dirty. It belongs to the sample-replacement worker, who committed it as `045af4a` during this session. I left it alone.

Condor jobs run from the live AFS repo (`condor/submit.sh`: `cd $BASEDIR`). For that reason the edits are RUN-only, each file was swapped in atomically (`os.replace`), and the TRAIN/legacy code paths are unchanged. At the time, cgupta had 3 jobs running and 2 held.

## G1: training-input provenance frozen next to the EOS v2 model

Script: `~/negrw_g1g2_20261112/g1_freeze.py`. It refuses to overwrite anything, checks the sha256 of every copy against its source, then sets the files read-only (`chmod 444`). That is not an immutable ACL: the owner can still change it.

Checks before copying:
- `train_v2.parquet`: 7,595,624 rows, 27 columns, 174,764,220 B.
- Manifest: `n_chunks` 377, 40 partitions, `rows_total_eos` = `rows_total_slim` = 7,595,624, `chunks_newer_than_slim` 0.
- Model `af53567c…` is identical in all three copies: AFS, EOS and condor `out/`.

| artifact | sha256 | location |
|---|---|---|
| sidecar `negrw_models_v2_20261112.provenance.json` | `068068f1b1d38e8cec8fb51a1075a935478fa8ad166cbf522fb470edd895c237` | `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/` (next to the model) |
| `train_v2.parquet` (frozen copy) | `f603ef6de8f30dc873615eddadba63684ebd64fc0e0b7c830a8e19213e7cc412` | `…/negrw_out_img/v2_20261112/frozen_inputs/` |
| `resume_input_manifest.json` (377 chunks) | `a76a5e2fb7141d35bb47a1182cf41bb071feb10cdaac5a4954225eff680a3ca0` | same |
| `sr_allfix_v1_20261110.parquet` | `4e34a0fffada2b7ee3953b8606bd41c591c0b0a167ce096ad920b29f3692ff98` | same |
| `negrw_train_v2.py` (as trained, recipe `7c1738b`) / `negrw_slim_v2.py` | `759023fb…` / `978c3382…` | same |
| training log `negrw_train_v2.9701673.out` | `aac26dee…` | same; also `SHA256SUMS` |

- The originals are untouched: `condor/hww_genrw_train_v2_model/train_v2.parquet` re-hashed to `f603ef6d…` afterwards, and the reviewer manifest is still in `~/negrw_review_20261112/`.
- The model binary was not rewritten. The sidecar is a separate file.
- No large binaries went into git.
- `train_v2.parquet` on AFS should **not** be cleaned up without Chirayu's OK, even though a frozen copy now exists.

## G2: RUN records the negrw model it actually consumed

Analysis commit **`ccdc8f9`** (local, not pushed) on branch `hww-analysis`, repo `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`.

**`analysis/processors/base.py`** (`b932556e7042`):
- In RUN mode, each chunk now writes `provenance["negrw_model_sha256"]`, for V+jets and non-V+jets chunks alike. The slim-ntuple parquet metadata gets the same field.
- The value is the sha256 of the bytes that `joblib.load` deserialises. The file is read once and the same bytes are both hashed and loaded, so replacing the file mid-job cannot make the record disagree with the scores.
- A workflow with no `negrw` block records the explicit value `"disabled"`.
- TRAIN and legacy modes still load the model by path and record nothing.
- `features/hww.py` and the TRAIN hashes are not touched, so the weight-only negrw input did not go back into TRAIN.

**`scripts/combine/build_cards_from_templates.py`** (`411ad3850173`):
- `merge_outputs` rejects, file by file, a RUN output that is missing `negrw_model_sha256`. It has to check each file because `accumulate()` unions the sets, so a file without the key would otherwise merge silently. It also rejects malformed values.
- Mixed identities across files, including "disabled" mixed with a sha, are rejected by the existing single-value provenance check.
- `main()` refuses to build cards if the identity differs from `negrw_identity(cfg)`, the sha256 of the current `negrw.model` file, or "disabled".
- `template_policy.json` records the identity.
- Consequence: RUN outputs written before this change (no key) can no longer be merged. Only test RUN outputs exist today.

**Tests** (container `coffea-base-almalinux9:0.7.30-py3.10`, at HEAD `ccdc8f9`):
- `tests/test_negrw_identity.py` (`899c860130d8`) and `tests/test_negrw_stats.py` (`eace74bbd368`): **14/14 OK** (about 14 s). They cover:
  - the identity equals the consumed bytes and stays the same after the file is replaced mid-job;
  - "disabled" is explicit;
  - TRAIN keeps loading by path and records no sha;
  - production-model scores are bit-identical whether loaded from bytes or by path;
  - merge cases: matching sha merges, matching "disabled" merges; mixed sha/sha and sha/disabled are rejected; missing (in one file or all files) and malformed values are rejected; non-RUN outputs keep the "Only RUN outputs" refusal;
  - `main()` refuses a different model;
  - the A/B TRAIN hashes are **unchanged**: A `36f655f4/80e75bca` and B `36f655f4/24b63ba3`, and they stay the same when `negrw.model` is swapped to v2.
- Existing suites `test_trainrun_blockers`, `test_external_inputs`, `test_processing_modes`, `test_routeb_integration` and `test_channel_split`: **50/50 OK** after the patch. The rest of the 118-test suite was not rerun because its code is unchanged.
- **End-to-end local one-file RUN smoke**, not submitted:
  - same input and diagnostic fold-0 manifest as the b-hive smoke; ran 15:19–15:20 at `8535275` plus the patch, rc 0;
  - script and log: `~/negrw_g1g2_20261112/run_smoke/run.sh`, `run.log`;
  - output `out/HplusCharm_4FS_HToWWTo2L2Nu.coffea`, `f4549aed…`;
  - provenance `negrw_model_sha256 = {05567a8c…f707417}` (the July model), with features/selection `36f655f4…/80e75bca…`. The slim parquet metadata carries the same sha;
  - `merge_outputs` accepts it and matches `negrw_identity(cfg)`. Merging it with the earlier pre-G2 b-hive smoke output is **refused** ("no negrw_model_sha256");
  - check script: `run_smoke/check_smoke.py`.
  - The smoke sample is signal (not a negrw dataset), so V+jets scoring through the bytes path is covered only by the unit tests above.

## Corrected validation statistics (F1, F2)

These fix the reported statistics only. They do not validate either model.

**Code changes:**
- `scripts/negrw/negrw_train_v2.py::closure` (`fe809f3bb1c6`): `ratio_staterr` is now the delta-method σ of R = Σ|w|g/Σw, i.e. Var(R) = Σ(|w|g − R·w)²/(Σw)², and the result is tagged `ratio_staterr_def: "delta"`.
- `binned` adds a per-bin `<k>_ratio_var`. It includes an out-of-range/NaN fix found during this work.
- `scripts/negrw/negrw_stats.py` (`82ca60d5e644`) ports the reviewer's `resume_shape_cov.py` fitted-normalization, shared-event covariance:
  - per-(era, dataset) k;
  - c_ib = (k·a_i − w_i)(1[i∈b] − f_b);
  - pseudo-inverse χ² with ndf = rank;
  - a `CMS_negrw_vjets` ΔΔᵀ term.
- `make_negrw_v2_plots.py` (`20cd4e6aea0a`):
  - takes a JSON path as input;
  - draws no error bars from the old denominator-only σ;
  - uses the per-bin delta σ;
  - adds plots 09 (shape after renormalization).

**Toy tests:**
- closure σ: toy spread / formula = 1 ± 0.06 over 2000 toys; the old formula overstates by >15%;
- per-bin σ, including out-of-range rows;
- shape χ² under the null: ⟨χ²⟩ = rank ± 0.4 over 1000 toys with two eras, and the empirical/formula covariance diagonal is 1 ± 0.15;
- a biased model is detected, and adding the nuisance lowers χ².

**Versioned report**, new directory. The original `negrw_v2_validation.json` (`e6918b6c…`) and `img/` are untouched:
- `/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/corrected_report_20261112/negrw_v2_validation_corrected_20261112.json`, sha256 `c52edc930f618c58332e4514b982e3ddbb1c4d010d041e263d129039790bcfbf`.
- Script: `scripts/negrw/negrw_v2_corrected_report.py` (`b9f04de0808f`); log `~/negrw_g1g2_20261112/corrected_report.log`.
- Inputs are pinned to the G1 frozen copies.
- Held-out scores come from the reviewer cache `resume_holdout_scores.npz` (`5fbae7a0…`). A spot re-score of 20,000 rows with both models agrees to max |Δg| 6e-8.
- Recomputed ratios equal the author JSON to 1.5e-8.
- Shape χ² reproduce the reviewer `resume_shape_cov_out.json` to 1.7e-6 relative. That is floating-point noise in the eigensolver; the tolerance is set to 1e-4.

**Held-out closure (1,516,987 rows).** σ_old is √Σw²/|Σw|, now superseded. These numbers reproduce review F1.

| sample | v2 R | σ_old → σ corrected | (R−1)/σ | July R | July (R−1)/σ |
|---|---|---|---|---|---|
| total | 0.9984 | 0.0016 → 0.0012 | −1.4 | 1.0031 | +2.7 |
| DY 10–50 | 0.8980 | 0.0139 → 0.0091 | −11.2 | 0.9048 | −10.4 |
| DY 50 | 1.0080 | 0.0019 → 0.0012 | +6.5 | 1.0127 | +10.3 |
| W 0J | 0.9855 | 0.0022 → 0.0011 | −13.2 | 0.9886 | −10.4 |
| W 1J | 1.0086 | 0.0036 → 0.0028 | +3.1 | 1.0133 | +4.8 |
| W 2J | 1.0004 | 0.0059 → 0.0051 | +0.1 | 1.0096 | +1.8 |

**SR closure** (allfix v1 reference, 17,627 events):
- v2: 1.0110 ± 0.0207 (σ was quoted as 0.0248 before);
- July: 1.0185 ± 0.0208;
- DY 50: v2 1.0073 ± 0.0194.

**Shape after per-(era, dataset) renormalization** (v2 / July). These are the χ² values from review F2, unchanged:

| variable, sample | v2 χ² / ndf | v2 with nuisance | July χ² / ndf | July with nuisance |
|---|---|---|---|---|
| `lhe_vpt`, DY 50, njets ≥ 1 | 47.2/20 | 35.0 | 47.9/20 | 37.1 |
| `lhe_ht`, DY 50, njets ≥ 1 | 110.0/10 | 26.5 | 92.9/10 | 25.8 |
| `lhe_vpt`, W 1J | 139.4/20 | 120.1 | 185.5/20 | 155.6 |

The full set is in `shape_after_renorm` (4 variables × 3 subsets × 5 datasets × 2 models).

**The author note's shape pulls are superseded.** It quoted DY‑50 `lhe_vpt` "χ² 42/20, max pull 4.9". That was the raw, un-renormalized ratio with the denominator-only σ. With the per-bin delta σ the same raw ratio gives 118/20, max 9.4. That raw ratio is not a shape test. The shape statistic to use is `shape_after_renorm`.

## Vault corrections

[[Projects/HToWW/negative-weights/2026-11-12-negrw-retraining]] now has a dated correction block:
- 397 → **377** chunk files;
- N1 is "disjoint at nominal objects";
- its closure σ, pulls and χ² are superseded by this note.

The rest of the author note (model identity, recipe, AUC, coverage) is still current, so it is not marked superseded as a whole.

## Remaining

- **G3 (open):** closure on the scored SR V+jets fit bins in each final channel. It needs a RUN `--slim_ntuple` output or a legacy `mva/` parquet with `weight_nominal`, `weight_negrw` and `weight_negrw_std`, then `negrw_stats.shape_cov` on the fit observable, compared with `CMS_negrw_vjets` and the template MC stat. If the bias is not covered, Chirayu decides the prescription.
- If v2 is adopted later:
  - run every V+jets RUN chunk of every era after the switch;
  - `build_cards_from_templates` will now refuse mixed or stale identities;
  - the identity to expect is `af53567c…`.
- Not done:
  - TRAIN outputs still record no negrw identity (by design: weight-only, b-hive does not read it);
  - the legacy `make_combine_inputs.py` path has no identity guard (out of the approved scope);
  - V+jets scoring through the bytes path has no end-to-end RUN run.

## Plots

- tags: [plot]
- Date: 2026-11-12
- Description: corrected negrw v2 validation plots from the versioned report.
  - 04: closure per (era, dataset) with delta-method σ.
  - 05/06/07: raw ratio panels with per-bin delta σ.
  - 09: shape residual after per-(era, dataset) renormalization with the fitted-k covariance, v2 vs July, against the |`CMS_negrw_vjets`| band.
  - 02/03/08 copied unchanged from the original JSON.
  - Agent-reported; not a shape validation.
- Path: /eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/corrected_report_20261112/img
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/negrw_out_img/v2_20261112/corrected_report_20261112/img
