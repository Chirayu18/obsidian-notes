---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# Route B (H+c 3FS/4FS stitching) integrated, tested, TRAIN submitted (12 Nov 2026)

**Status: agent-reported.** Code is committed locally on lxplus (branch `hww-analysis`, not pushed, not reviewed by Chirayu). Route B TRAIN is submitted for all 4 eras. Completeness is tracked in the table below. No training, RUN or Combine has run on Route B yet.

Repo: `lxplus:~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`. Method and proposal: [[Projects/HToWW/2026-11-05-route-b-stitching-implementation]] (LHCHWG-2026-007 sec 4.4).

Route B combines two samples. The private 3FS re-NANO keeps events with at least one GEN c-jet (pT > 10 GeV, |eta| < 2.5, hadronFlavour 4). The central 4FS FxFx sample keeps events with no GEN c-jet. Both are normalised to sigma_NNLO x BR = 0.0016626 pb with L*X*c_s/F_s per era. The task was started by a previous agent and continued here after an account move.

## Commits (lxplus, local only)

| commit | what |
|---|---|
| `eaab247` | Route B integration (previous agent, reviewed here; details below) |
| `7b4b930` | `routeb_io.sink_scale_factors(era_samples=...)`: the card builder fails if a configured Route B sample of the era (for example the 2022postEE `_ext1`) is missing from the output. Before this, F_3FS would have been short with no error. Test added. |
| `3a03245` | `analysis/utils/parquet_writer.py`: unique local staging file per write. **This file is outside the Route B files I was given; see "Race fix" below.** |

`eaab247` contents:
- `analysis/stitching/{__init__,hplusc_routeb,routeb_io}.py` (proposal files).
- `base.py` hook, active only when the workflow has a `stitching: hplusc_routeb:` block:
  - the keep-mask is applied before object corrections;
  - sumw and the per-chunk `routeb_stitch` records use the full (pre-mask) chunk;
  - provenance `routeb_stitching` = the stitching block plus sha256 of `analysis/stitching/*.py`;
  - the 3FS PDF fix (see below).
- The workflow `hww_routeb_3fs4fs.yaml`, made from the current `hww_allfix_4fs.yaml`:
  - adds `hc_3fs`;
  - `hpluscFSShape: []`;
  - removes `xsec_hplusc_3FS_4FS`;
  - Combine outputs go to `outputs/combine/routeb/`;
  - adds the stitching block.
- Era-YAML entries `HplusCharm_3FS_HToWW` (all eras) and `HplusCharm_3FS_HToWW_ext1` (2022postEE), xsec 0.0016626.
- Fileset JSON keys added. Backups are `*.bak-20261112-routeb`. The JSONs are untracked; their file counts equal DAS: 253 / 824 + 34 / 574 / 301.
- Card builder: Route B samples are scaled by L*X*c_s/F_s.

The 3FS PDF fix: the 3FS sample uses LHA 321900, a set of 100 MC replicas. `lhe_pdf` / `lhe_pdf_alphaS` are re-added for 3FS as the replica standard deviation (ddof = 1, capped at 0.5). `lhepdf.py` is unchanged; its Hessian formula is about 10x too large for a replica set. The fix only acts in the RUN nominal pass. TRAIN carries no PDF variations.

Review notes on `eaab247`:
- Run A goes through the unchanged path (`stitch_keep is None`).
- The condor partition suffix `_<n>` is resolved through `dataset_info`.
- Fold assignment uses `event_folds(events)` (per event), so the stitch mask does not move events between folds.

Provenance sha256 carried by all Route B TRAIN jobs:

| file | sha256 (first 16) |
|---|---|
| `hplusc_routeb.py` | `5b4e256b4fdfd826` |
| `routeb_io.py` | `eb9bb58752ee3a19` |
| `__init__.py` | `b77acc70d6e8c6a9` |

## Race fix in `parquet_writer.py` (3a03245): why it was needed

`condor/submit.sh` does `cd $BASEDIR`, so every Condor job runs in the shared AFS repo directory. `dump_pa_table` / `dump_ak_array` first write `./<fileuuid>_<range>.parquet` there, copy it to EOS and then delete it.

Route B TRAIN uses the same filesets and partitioning as Run A v2 (`nfiles` 15), so job *k* of a background dataset processes the same chunks with the same temp name in both workflows. A concurrent job could delete the other's staged file, which raises `FileNotFoundError`. In the worse case it could replace that file before the copy, so a job would upload the other workflow's rows **with no error**.

This happened in a local smoke pair: `b_4fs` (Route B) and `an_4fs` (Run A) on the same 4FS file, both run from the repo directory, and `b_4fs` failed with `FileNotFoundError`. The same race applies to Run A against the genrw jobs, which also run from this repo.

The fix:
- The local staging name is now `<fname>.<pid>.<uuid>.tmp`. The destination name and content are unchanged.
- `tests/test_routeb_parquet_staging.py` checks that a foreign file at `./<fname>` survives and nothing is left behind. It fails against the old writer.
- Installed atomically. Container import tested immediately, then the full suite run.
- Run A jobs that start after 12 Nov ~01:07 import it. Single-file smokes show their output is byte-identical (below).

Chirayu: please confirm you are fine with this framework edit. It is backward compatible, and it is the one change outside the Route B files I was given.

## Tests (coffea 0.7.30 container, live repo, after all commits)

Suite: `test_routeb_parquet_staging`, `test_routeb_integration`, `test_routeb_stitching`, `test_channel_split`, `test_event_rng`, `test_external_inputs`, `test_trainrun_blockers`, `test_processing_modes`, `test_hzz_safety_ports`, `test_allfix`, `test_jobs_status_merge`. Result: **118/118 OK**.

The "known" `test_bhive_config_and_onnx_io_checks` error was the Kerberos cache not being visible in the container. Adding `-B /run/user/151861` to the apptainer binds fixes it.

## Single-file TRAIN smokes (2022postEE, `submit.py`, rerun 12 Nov ~00:35–01:10)

Route B and "new" Run A ran from the live repo. "Old" Run A ran from a copy with the pre-Route-B `base.py` (f84d311). The comparison script is `/tmp/cg_routeb/compare.py` on lxplus914; its output is `/tmp/cg_routeb/compare_out_v2.json`.

| check | result |
|---|---|
| Run A parity, 4FS file (new code, including the new writer, vs old) | parquet identical (424 rows); coffea keys, provenance and samples equal |
| Run A parity, background file (GluGluHto2Wto2L2Nu) | parquet identical (676 rows); same equality checks |
| Route B 4FS | 40 rows = exactly the Run A rows with N(GEN c-jet) = 0; no column differs on common rows; stitch full sumw 25613.4232 vs entry sumw 25613.4258 (float32); f_keep(4FS) = 0.607 |
| Route B 3FS main / ext1 | 18 / 16 rows, all with N >= 1; full sumw matches the file; f_keep = 0.453 / 0.484; negative-weight fraction 0.38 / 0.40 |
| Route B background | same rows as Run A (676); `routeb_stitching` provenance in parquet metadata; no `routeb_stitch` record for non-H+c samples |
| 3FS PDF (legacy-mode parquet) | `lhe_pdf` Up/Down: median per-event 1.94%, max 4.4%, sumw ratio 1.026 / 0.974; `lhe_alphaS` = 1; `lhe_pdf_alphaS` = `lhe_pdf` |

The second run matched the first (11 Nov 23:55) except for the expected new `routeb_io.py` sha256. All 9 smokes exited 0. The one failure, `b_4fs`, was the race above; it passed when rerun alone.

## Other repo housekeeping

- `mode_opts.bin` in the repo root (23 bytes, 12 Nov 00:28) contained `--mode train --folds 5`, NUL-separated. `condor/submit.sh` writes this format, but only to the job's `$WORKDIR`, never the repo root, so a stray manual run made it. It is not referenced from the repo root. Moved, not deleted, to `lxplus914:/tmp/cg_routeb/mode_opts.bin.moved-from-repo`.
- `analysis/processors/.base.py.swp` (0 bytes, 17 Aug): an old editor leftover, not from this task. Left in place.

## TRAIN submission (12 Nov 01:10–01:21)

- Command: `python3 runner.py --workflow hww_routeb_3fs4fs --year <era> --submit --eos --mode train --folds 5`, run by `lxplus:~/htoww_submit_logs/submit_routeb_20261112.sh`. All 4 eras returned rc = 0.
- Logs: `~/htoww_submit_logs/routeb_submit_<era>_20261112.log`.
- Output: `/eos/user/c/cgupta/higgscharm/outputs/hww_routeb_3fs4fs__train/<era>/`.
- If a runner call is cut off: `~/htoww_submit_logs/submit_missing_routeb.py --year <era>`.

| era | datasets | jobs | clusters | H+c jobs (3FS / ext1 / 4FS) |
|---|---|---|---|---|
| 2022preEE | 55 | 523 | 9701608–9701666 | 17 / – / 2 |
| 2022postEE | 57 | 1246 | 9701667–9701730 | 55 / 3 / 2 |
| 2023preBPix | 67 | 679 | 9701731–9701801 | 39 / – / 1 |
| 2023postBPix | 57 | 414 | 9701802–9701866 | 21 / – / 2 |

Each era's job count equals Run A's plus ceil(3FS files / 15).

## Completeness (`jobs_status.py -w hww_routeb_3fs4fs -y <era> --eos --mode train`)

| era | check time | finished / expected | action |
|---|---|---|---|
| (filled in as passes complete) | | | |

## Open items for cards / RUN

1. **3FS PDF under option (a).** The H+c PDF rate lnN 1.074 is the 4FS Hessian (325500) number. For Route B, the 3FS region carries its own replica-std shape. Decide whether 3FS keeps `lhe_pdf` as shape plus rate, or shape-only with the lnN; this needs the 3FS normalisation (`lhe_norm`) treatment.
2. **Scale variations.** muR/muF on the 3FS and 4FS pieces come from different generators. Check the stitched scale envelope is consistent across regions before cards (the `xsec_hplusc_3FS_4FS` shape is removed in Route B).
3. **`split_folds` normalisation.** It still uses L*X/sumw per sample for H+c. This is irrelevant for b-hive, which uses class weights only, but wrong if weighted training is ever used. Use `routeb_io.sink_scale_factors` there.
4. **Untested RUN-mode path.** In RUN mode, a chunk where every event is masked goes through `object_corrector_manager` with zero events. TRAIN skips it; RUN is untested.
5. **Selection hash.** Route B's selection hash differs from Run A's (`hpluscFSShape` change), so Route B needs its own fold split, model and RUN; Run A models cannot be reused as-is.
6. **Proxy expiry.** `x509up_u151861` is valid to about 18 Nov.
