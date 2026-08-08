---
tags:
  - reference
status: active
date: 2026-06-17
source: lxplus
pinned: true
---

# Quickstart — H+c (H→WW) analysis on `migration-v2`

This branch runs the **H+c → WW** analysis end-to-end: NanoAOD → parquet
ntuples (with JES/JER/lepton systematics) → 6-class MVA scoring → Combine
datacard → r₉₅ limit. It is built on the **`uacms/MVA`** systematics line, with
content cherry-picked from Thomas's 53-variable line.

```
git checkout migration-v2
```

---

## What's different vs upstream `uacms/MVA`

| Area                         | Change                                                                                                                                                                                        |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Parquet output**           | Self-normalising shards — `sumw`/`xsec`/`era` stored in the parquet schema metadata, plus an `event` id column. No external bookkeeping needed.                                               |
| **Object-shift systematics** | One Condor job per dataset emits the nominal **plus every** JES/JER/lepton scale+resolution shift in a single NanoAOD read (`object_shifts: true`). Shifts land in `<dataset>/base/<shift>/`. |
| **Shift merge**              | `merge_shifted_parquets_by_sample` collapses them to `<year>/<shift>/<sample>.parquet`.                                                                                                       |
| **MVA**                      | Train/test split + inference extracted into `scripts/mva/{prep_training_inputs,run_inference}.py`; 6-class model, order `[hplusc, higgsbkg, tt, st, diboson, vjets]`.                         |
| **Combine**                  | New `scripts/combine/` pipeline + a `combine:` block in the workflow yaml (6 argmax channels, 12 shape systs, 9 lnNs).                                                                        |
| **Variables**                | 53 MVA/histogram variables (mirrored into `hww.yaml` + `hww_MVA.yaml`).                                                                                                                       |
| **Selection**                | Single category `base`, now requiring **`atleast_one_cjet`** (SR category dropped).                                                                                                           |
| **Fixes**                    | muon `pt_resol` clamp; empty-parquet failsafes; **2022postEE JEC tags bumped V3→V4 / JRV1→JRV2** (cvmfs `latest` drift — see Gotcha).                                                         |

Two workflow files, identical except one knob:
`hww_MVA.yaml` (`object_shifts: false`, nominal) and `hww_combine.yaml`
(`object_shifts: true`, nominal + all shifts).

---

## Run it end-to-end

### Pre-flight (once per session)
```bash
voms-proxy-init --voms cms --valid 192:00
cd .../higgscharm
ln -sfn /eos/user/c/cgupta/higgscharm/outputs outputs   # if not already linked
```

### Nominal → r₉₅ (the working path)

Current production workflow is **`hww_combine_2dcat`** (native 2D c-tag SF + negrw).
Env: `micromamba run -n b_hive` with
`MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba`.

```bash
# 1. Produce parquets on Condor. Use --memory 6000 (default 3 GB OOMs heavy samples).
python runner.py -w hww_combine_2dcat -y 2022postEE --output_format parquet --eos --submit --memory 6000

# 2. *** CHECK COMPLETION -- DO NOT SKIP ***  (see the gotcha below)
python jobs_status.py -w hww_combine_2dcat -y 2022postEE --eos
#    -> prints expected / finished / missing; answer y to resubmit the missing ones.
#    RE-RUN UNTIL missing == 0 BEFORE DOING ANYTHING ELSE.

# 3. Merge shards  (NOTE: there is no --mva flag)
python run_postprocess.py -w hww_combine_2dcat -y 2022postEE --postprocess --output_format parquet

# 4. MVA inference -> adds mva_score_* columns
python scripts/mva/run_inference.py -w hww_combine_2dcat -y 2022postEE

# 5. Build ROOT templates + datacard
python scripts/combine/make_combine_inputs.py -w hww_combine_2dcat -y 2022postEE

# 6. Fits (inside CMSSW — the wrapper sources it)
bash scripts/combine/run_combine.sh hww_combine_2dcat

# 7. Plots
python scripts/combine/make_combine_plots.py -w hww_combine_2dcat
python scripts/combine/make_impact_plot.py   -w hww_combine_2dcat
```

Only **step 6** runs inside CMSSW; steps 3–5 run in the `b_hive` env.

### Retrain the MVA (in the b-hive repo)

**Training and the fit read DIFFERENT trees.** This is the single most confusing thing
about the setup:

| purpose | tree | why |
|---|---|---|
| **training** | `hww_combine_fixed/<year>/mva_labeled/` | has the group-level merges (`ggH.parquet`, `VBF.parquet`, …) that `make_mva_labeled.py` needs |
| **fit / limit** | `hww_combine_2dcat/<year>/` | has native `ctagging_2d: true` → `weight_CMS_ctag2d_2022` |

The "2dcats" in `hwwcom_multiclass_v11_2dcats` refers to the **feature set** (the 11
one-hot `cjet_cand_ctag2d_*` columns appended post-hoc), **not** to the
`hww_combine_2dcat` workflow. The model trains on `hww_combine_fixed` parquets.

```bash
cd /eos/home-c/cgupta/HToWW/b-hive

# a. labels + 80/20 split (produces mva_labeled/{train,test}/ + filelists/base.txt)
python make_mva_labeled.py --input-dir <outputs>/hww_combine_fixed/2022postEE --groups-key process_groups
python split_train_test.py --input-dir <outputs>/hww_combine_fixed/2022postEE/mva_labeled

# b. append the 11 ctag2d one-hots (REQUIRED by the HPlusCHToWW_2dcats config;
#    the processor does NOT write them)
python scripts/append_onehot.py --mva-dir <...>/mva_labeled/train
python scripts/append_onehot.py --mva-dir <...>/mva_labeled/test

# c. train (DatasetConstructor -> Training -> Inference -> ROC)
./train_v11_2dcats.sh
# then point inference.model_path in the workflow yaml at the new best_model.pt
```

`train_v11_2dcats.sh` uses `filelists/v11_{train,test}_allEras.txt` — **3 eras**
(2022postEE + preEE H+c/H+b + 2023preBPix H+c). For a single-era study, write a filelist
with only that era's lines and pass `--train-filelist` / `--test-filelist`.

---

## Gotchas

- **JEC version drift.** cvmfs `latest` `jet_jerc.json.gz` moves versions; the tags
  in `analysis/corrections/jec_params_correctionlib.yaml` must match or jobs die
  with `KeyError: ..._V3_MC_L1L2L3Res_AK4PFPuppi`. **2022postEE is fixed (V4/JRV2);
  2022preEE and 2023* are still on V3/JRV1** — bump before running those years.
  Verify a key exists:
  ```python
  correctionlib.CorrectionSet.from_file(<json>).compound.keys()
  ```
- **Memory.** Runner Condor jobs need `--memory 6000`.
- **`jobs_status.py` output format.** Pass `--output_format parquet`; the default
  `coffea` counts stale `.coffea` stubs and reports wrong numbers.

### Completeness — the trap that invalidated a whole study (2026-08-08)

- **`jobs_status.py` is the ONLY valid completeness check.** Do not infer completeness
  from output directories on EOS: partition dirs (`<sample>_1`, `_2`, …) are created
  **early**, so "7/7 dirs exist" is true long before the jobs finish. A study was run to
  completion on trees that were 335/496, 3/6 and 2/6 finished, and every number had to be
  withdrawn. Run `jobs_status.py` and require `missing == 0` before reading any yield.
- **A partial tree reads LOWER than the baseline.** If a strictly looser selection gives
  *fewer* events than a tighter one, the tree is incomplete — that is the cheapest sanity
  gate available.

### Silent failures — a fast "success" is the failure mode

- **`run_postprocess.py` has no `--mva` flag** (some older notes show one). The call dies
  with `unrecognized arguments: --mva`.
- **`law` lives inside the `b_hive` env.** `b-hive/setup.sh` calls `law completion`, so
  sourcing it from a plain shell gives `law: command not found`, leaves
  `LAW_CONFIG_FILE` unset, and every task dies with
  `task family 'DatasetConstructorTask' not found in index` — **while `law` still exits
  0**. Source it *inside* micromamba:
  ```bash
  micromamba run -n b_hive bash -c "cd $B_HIVE_DIR && source setup.sh && law run <task> ..."
  ```
  and grep the log for `not found in index`, since the exit code will not tell you.
- **Piping a step into `tee` masks its exit code** (`tee`'s rc is ~always 0). Use
  `${PIPESTATUS[0]}`, or redirect to a file and `tail` it.
- **Rule of thumb:** on this stack, a step that "succeeds" implausibly fast has failed.
  Always sanity-check elapsed time against the work the step should be doing.

### Grid proxy and long-running submissions

- **The proxy is node-local.** `voms-proxy-init` writes `/tmp/x509up_u<uid>` on *one*
  lxplus node; reconnecting elsewhere makes `submit_condor.py` report
  "VOMS proxy expired or non-existing" on a perfectly valid proxy. Export the AFS copy,
  which `submit_condor.py` itself writes and which is shared across nodes:
  ```bash
  export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
  ```
- **`nohup … & disown` does not survive an ssh control-master reset.** Use `tmux` for
  anything long-running.
- **Waiting on a workflow's jobs needs the CLUSTER ID.** `condor_q -nobatch | grep <wf>`
  matches nothing (the listing shows the executable, not the workflow). Parse
  `submitted to cluster <N>` from the submit log and poll `condor_q <N> -af ProcId`.
- **The private H+c postEE NanoAOD (`maite.iihe.ac.be`) times out under load**
  (`XRootD error: Operation expired`). Transient — resubmit; it clears once the queue
  drains. `--nfiles <small>` reduces per-job concurrency if it persists.

---

## Status (updated 2026-08-08)

**Done since the June snapshot:**

- **Object-shift (JES/JER) shape templates: folded into the datacard.** No longer a
  pending wiring step.
- **c-tagging SF implemented** — native `CTag2DCorrector` (`ctagging_2d: true`) →
  `CMS_ctag2d_2022`, replacing the post-hoc patch. [[2026-07-19-ctag2d-full-documentation]]
- **Negative-weight reweighting** of V+jets (arXiv:2510.16217) in the processor.
- **sumw normalisation fixed** — `read_scale` now uses the self-normalising
  `sumw_records`, not the shard metadata (which undercounts WtoLNu 5.4×).
  [[2026-07-31-sumw-normalization-trap]]
- **LOWESS shape smoothing off everywhere** (it double-treated the negrw'd vjets).

**Current limits** (2022postEE, Asimov, `sumw_records`, no smoothing):

| variant | full | stat-only | freeze-aMCS |
|---|---:|---:|---:|
| baseline, no ctag SF | 1150 | 668 | 905 |
| **baseline + SF** ← canonical | **1164** | 676 | 930 |
| 2D-cat + SF | 1676 | 637 | 1393 |

**Open items, by measured impact** ([[2026-07-24-systematics-master-list]]):

1. **Signal theory 29.7%** — `xsec_hplusc_4FS_5FS` needs re-derivation (~20k gen-level
   events each of 3FS and 4FS non-FXFX at 13.6 TeV).
2. **MC-stat 24.5%** — more signal MC is the direct lever.
3. Trigger SFs — coded already, a config flip; expect ~0% impact.
4. `flavor_composition_ggH` still a 1.40 placeholder.
5. Decorrelation (JES Total → RegroupedV2, ctag Total → per-source) may *improve* the limit.

**In flight (2026-08-08):** c-jet acceptance study
([[2026-08-08-cjet-acceptance-study]]) — three selection variants testing whether the
charm tag can be loosened. **All results withdrawn**; trees were incomplete and are being
reprocessed. See that note for the full account.

## Reference numbers

- **Signal sample production (NanoAOD inputs):** [[2026-07-08-hplusc-hplusb-crab-status]] —
  hplusc/hplusb CRAB status across all 4 campaigns: 5/8 NanoAOD published (event counts
  + DAS links); the other 3 (2023 postBPix c+b, preBPix b) are mid-chain — step1+step2 done
  (step2 needed 5 GB/job, 67–96% published), **step3 RECO submitted 2026-07-15**.
- **Cutflow (2022postEE):** [[2026-07-07-cutflow-2022postEE]] — weighted events per
  selection step, all samples (`base` workflow).
- **Trigger efficiency (2022postEE):** [[2026-07-07-trigger-efficiency]] — per-sample ε
  from the `base` cutflow (signal H+c ≈ 37.5%). No trigger SF applied yet.

# Links
![[links]]