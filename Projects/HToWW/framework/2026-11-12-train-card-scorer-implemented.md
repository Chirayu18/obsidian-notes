---
tags: [reference, framework, production]
status: active
date: 2026-11-12
source: laptop
evidence: executed-focused-checks
---

# TRAIN-to-card scorer implemented; production models still pending

Chirayu explicitly approved installation/testing after the read-only approval rejection: **“yes continue”**. This supersedes the installation-blocked state in [[2026-11-12-train-card-scorer-local-draft]] and implements the offline nominal path designed in [[2026-11-12-train-stat-only-limit]]. No delegates used; no change to live training, corrections, workflows, seeds or input files.

## Implementation

Analysis local commit **5b25295** (`combine: add validated nominal TRAIN scoring and iteration cards`) adds only `scripts/combine/build_cards_from_train.py` and `tests/test_train_cards.py` under `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`. Neither analysis nor vault commits were pushed.

The scorer consumes the full MC `inputs.json` inventory already frozen by preparation and a strict production FoldModels manifest. It scores original TRAIN shards with the model holding out event%5. It checks marker modes/year/hashes, complete entry counts, exact partition LFNs, duplicate input/chunk/file identities, current workflow/fileset coverage, per-shard metadata/source/fold identities, and real selected-row totals. It reuses existing template normalization, Route B stitching, signed sumw2 handling, final bin policy, ROOT writer and card writer.

Historical TRAIN negrw weights are ignored: current v2 is rescored from generator columns using BaseProcessor's existing hashed-byte loader/predictor. Signed raw and reweighted sums are accumulated over all shards of each era/sample before yield-preserving renormalization. No fit-bin closure PASS is implied; G3 remains open.

Modes: `--stat_only` removes shape/lnN terms, retains autoMCStats and configured rateParams (including rate_tt). `--rate_systematics` retains configured lnN rates with the same nominal/statistical model, no shapes. `--stat_only --also_rate_systematics` writes both variants from a **single scoring pass**. Today's schema requires explicit `--merge_channel_splits`; absent split columns otherwise fail. These results would have one merged SR, distinct from intended two-SR full-systematics production. The command never submits jobs or runs Combine.

## Evidence

| Check | Saved source | Observed boundary |
|---|---|---|
| Initial focused regressions | `~/htoww_submit_logs/train_cards_tests_20261112_2025.log` |6/6PASS; superseded by changed-code7-test run below |
| Final focused regressions in existing coffea apptainer environment | `~/htoww_submit_logs/train_cards_tests_20261112_2030.log` |**7/7PASS**,0.142s test runtime, rc0; imports/startup excluded from that timing |
| Hand-calculated signed yields/variances, uint64 event fold assignment | test_signed_nominal_counts_variances_and_uint64_folds |PASS on controlled inputs |
| Current negrw rescoring; normalization after shard merge | test_negrw_rescored_and_renormalized_after_all_shards |PASS; stale stored weight_negrw intentionally unusable in fixture |
| Missing/duplicate rows, wrong fold/source, missing channel split | focused rejection tests |PASS; missing split requires explicit merge flag |
| ROOT readback, identical nominal templates in both card modes, background-only Asimov and rate_tt/autoMCStats retention | actual writer integration test |PASS on synthetic controlled templates; not a production fit |
| Real A/B TRAIN generator schema and current model/hash compatibility | `~/htoww_submit_logs/train_cards_real_schema_20261112.json` |One real selected DY event from each arm, same source chunk; current negrw shaaf53567c… and frozen feature/selection hashes match; g=−0.375169439323052. Bounded schema check, not full production scoring |
| Source hygiene and commit scope | git staged check, local5b25295 |Only434added lines in two new files; tracked pre-existing code unchanged |

The7-test run followed the change that added shared nominal scoring for both card modes. Existing unrelated unit/GPU tests were not rerun. No diagnostic model was registered or used as a production substitute.

## Next execution, once each arm's five folds finish

1. Read the real training status/provenance and best checkpoints for all five held-out models. Stop on failures; preserve successful dataset caches/checkpoints.
2. Run existing `scripts/mva/export_fold_onnx.py` in the established b-hive environment on the real held-out inputs; require its PyTorch/ONNX agreement and completed training-provenance records.
3. Register with `scripts/mva/register_folds.py`, supplying the split manifest, exact b-hive config, all four eras and export record. Its production guards remain intact.
4. From the analysis root, in the established coffea environment, for each era invoke the new script with `-w <arm_workflow> -y <era> --input_manifest ~/bhive_prod_20261112_sol/<A_or_B>/inputs.json --model_manifest <registered_meta.yaml> --output <new_directory> --stat_only --also_rate_systematics --merge_channel_splits`.
5. Check template_policy/yields/floored bins, combine era cards and execute blind Asimov expected limits in the established CMSSW/Combine environment. Preserve full source/card/model/command provenance. Produce comparison/performance material for the keeper-owned slides only from those checked outputs.

## Current compute boundary

At20:29CET A9706926–9706928 run,9706929–9706930 idle; B9706954 idle; DAGs running. A fold0 live stdout subsequently reached split source index021647, still DatasetConstructorTask. No production fold completion, epoch result, export or new A/B limit has been observed. The wrapper's earlier startup defect is operationally bypassed: it now reaches real dataset construction. B's five folds remain one sequential Condor job by explicit request. No repeat submission, release/removal, new watcher, credentials/services action, deletion or push.

The existing A yields artifact `~/htoww_submit_logs/yields_A_train_20261112.json` sums signed normalized weights from60123split shards. Its quoted statistical errors precede current negrw reshaping and must not be labelled final v2 template-bin uncertainties. Do not use it as proof of an MVA-category result.
