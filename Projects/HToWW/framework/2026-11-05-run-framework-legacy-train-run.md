---
tags: [reference]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# How to run the higgscharm HWW framework (legacy, TRAIN, RUN): state on 2026-11-05

**Status: agent-reported, not reviewed by Chirayu.** The TRAIN/RUN modes and the HZZ safety ports are implemented in the higgscharm working tree but are **uncommitted**. Neither mode has been run as a production, and no production model exists yet. Run A has not been submitted. This note replaces [[Projects/HToWW/framework/2026-07-24-run-analysis-steps]] as the current how-to. The legacy chain in that note still works, but its workflow (`hww_combine_2dcat`), v11 model and expected limits are from before the full fix.

Written by the keeper from a read-only inspection of the live tree (lxplus, 2026-11-05 ~09:50 CET: `git status`, `git diff`, and the argument parsers of the files below) and from the implementing thread: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:63909997-e3a4-4f8d-a68e-53b5c2c8bbc3>. The test counts are as reported there, not rerun by the keeper.

## Where the code is

- **Repo:** `/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`.
- **Committed:** HEAD `40d0e3e` (speed-ups and WH alignment) on top of `0850e51` (the full-fix baseline). Both are unpushed.
- **Uncommitted on top of that:** 11 modified files, +248/−20 lines:
  - the two Sol review fixes (`object_selections.py`, `lhepdf.py`);
  - the TRAIN/RUN wiring (`base.py`, `runner.py`, `submit.py`, `submit_condor.py`, `condor/submit.sh`);
  - the HZZ ports (`eos_io.py`, `postprocess/utils.py`, `make_combine_inputs.py`);
  - tests.
- **New untracked files:** `analysis/processing_modes.py`, `analysis/processing_checks.py`, `analysis/features/hww.py`, `analysis/models/registry.py`, `analysis/sinks/hww.py`, `scripts/mva/split_folds.py`, `scripts/mva/register_folds.py`, `scripts/check_train_outputs.py`, `scripts/combine/build_cards_from_templates.py`, `tests/test_processing_modes.py`, `tests/test_hzz_safety_ports.py`, and diagnostic `tests/data/mode_models/fold_{0..4}.onnx`.
- **Backups and change logs:** `/eos/user/c/cgupta/HToWW/backups/higgscharm_pre_fullfix_20261104/sol_trainrun_20261105/` and `.../sol_review_20261105/`. `*.pre_sol_review` files sit next to each edited file. Do not stage them.
- **Run A workflow:** `hww_allfix_4fs`.

## Modes (`--mode`, on `runner.py` and `submit.py`)

| mode | what it writes | when to use |
|---|---|---|
| `legacy` (default) | as before: nominal and every object-shift parquet tree | current production chain; unchanged behaviour |
| `train` | slim **nominal** feature ntuples (parquet), one row per selected event, plus the event fold | build MVA training inputs |
| `run` | **coffea** accumulators holding inline-scored templates for nominal and all shifts. Each event is scored by the model of its held-out fold. `--slim_ntuple` also keeps per-shift features and weights as insurance | production templates for cards, without the parquet → inference → template steps |

Common flags:
- `--folds k` (default 5; minimum 2, and `split_folds.py` needs k ≥ 3). The fold is `event mod k`.
- `--model_manifest <meta.yaml>`: RUN only, and required. There is **no fallback to the old v11 model**.
- `--allow_diagnostic_model`: local tests only. Combined with `--submit`, it is refused.

Guards (`processing_modes.validate`):
- TRAIN and RUN need a workflow with `mva` and `combine` blocks and exactly **one** exclusive preselection category.
- RUN refuses a manifest whose features hash, selection/correction hash, class order or fold scheme differs from the workflow.
- RUN refuses a model without training provenance (workflow, eras, git commit, file-list SHA256), and a fold model whose SHA256 does not match.

## Steps

0. **Proxy** (you, on lxplus): `voms-proxy-init --voms cms --valid 192:00`. If an agent on another node needs it, add `--out ~/private/x509up_cms`.
1. **EOS space first.** At the last count there was about 81 GB free against about 266 GB for a legacy full production with shifts (full-fix state note). Chirayu, 2026-11-05: "Dont remove anything from eos also". Space must therefore come from a new output location, not from deletion.
2. **Legacy chain** (Run A as it stands): the same steps as the 07-24 note with `--workflow hww_allfix_4fs`, i.e. `runner.py … --submit --eos --output_format parquet` → `jobs_status.py` → `run_postprocess.py --postprocess --mva` → `scripts/mva/run_inference.py` → `scripts/combine/make_combine_inputs.py` → `run_limit.sh`. **Caveat:** the v11 event model was trained on the old leptons, so it must be retrained before a limit is trusted.
3. **TRAIN:**
   ```bash
   python3 runner.py --workflow hww_allfix_4fs --year <era> --submit --eos --mode train --folds 5
   python3 scripts/check_train_outputs.py --coffea <TRAIN .coffea files> --parquets <TRAIN parquet shards>
   python3 scripts/mva/split_folds.py --inputs <TRAIN parquet shards> --coffea <all TRAIN .coffea, incl. zero-selection chunks> --output <dir> --folds 5
   ```
   `split_folds.py` writes, for each model i, the test fold i, the validation fold (i+1) mod k and the remaining training folds. No data or unlabelled process enters a supervised file list.
4. **Train the k fold models** externally in b-hive, one per held-out fold. Export them to ONNX and check the ONNX against torch (max |Δ| ≤ 1e-5). This step is not automated here.
5. **Freeze the models:**
   ```bash
   python3 scripts/mva/register_folds.py -w hww_allfix_4fs --split_manifest <split manifest> \
     --models fold_0.onnx … fold_4.onnx --eras <eras> --validation <onnx-vs-torch.json> --output <meta.yaml>
   ```
6. **RUN:**
   ```bash
   python3 runner.py --workflow hww_allfix_4fs --year <era> --submit --eos --mode run --folds 5 --model_manifest <meta.yaml>
   ```
   In TRAIN and RUN, `submit.py` adds an `execution_checks` record (HZZ port). Every input file's entries must equal the events read, and a duplicate NanoAOD file (same file UUID) raises an error.
7. **Cards from RUN templates:**
   ```bash
   python3 scripts/combine/build_cards_from_templates.py -w hww_allfix_4fs -y <era> --inputs <RUN .coffea> --output <new dir> [--not_applicable na.yaml]
   ```
   Normalisation happens after all chunks are merged, including zero-selection chunks. A missing shape needs an explicit per-sample "not applicable" entry. The script does not run Combine.
8. **Limit:** as before (`run_limit.sh`/`run_combine.sh`) on the new card.

## HZZ ports (from Saranya's HZZ branch, commit `7962523`; only the useful parts)

Chirayu, 2026-11-05: "dont adopt anything useless from hzz btw.. Only things useful for us". Two things were ported:
- **Output completeness:** `processing_checks.py` and `check_train_outputs.py`. Incomplete or duplicated inputs now fail instead of producing partial rows.
- **EOS read fallback:** `eos_io.read_parquet` and `eos_io.isdir`, used in postprocess and in `make_combine_inputs.read_scale`. They read correctly when the FUSE mount serves stale listings.

The ZZ-specific selections, the c-tag changes and the wider production machinery were not ported.

## What has been checked (agent-reported, thread 2026-11-05)

- **Tests:** 49 pass, covering TRAIN/RUN and the HZZ ports.
- **Seeded checks:** legacy, TRAIN and RUN give identical nominal features and weights. The inline RUN templates match independent histograms built from the slim ntuples. Only diagnostic fold models were used.
- **Not done:**
  - a full TRAIN production;
  - real fold models;
  - a RUN production or card;
  - an independent review of TRAIN/RUN and the HZZ ports. Sol reviewed Route B, but the reverse review, a second Claude reviewer, was not started: Chirayu said "Actually let that agent only continue";
  - committing these changes.
