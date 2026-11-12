---
tags: [reference, production, decision]
status: active
date: 2026-11-12
source: laptop
evidence: in-progress
---

# Event-MVA training relaunch after the batch preparation failure (2026-11-12)

Follows [[2026-11-12-direct-continuation-training-launch]].

## Chirayu's wording (2026-11-12)
- "Can you launch the training on lxplus-gpu?"
- "You may start claude subagents now , launch 1 for the hdamp stuff... And 1 for making slides"
- Then: "Stop, I need to ask the keeper to make the slides actually". **No slide worker was started.** The keeper owns the slides.
- I gave him the GPU facts below and asked where to run. His choice: **"Batch GPU (Recommended)"**. After the interactive preparation passes, the 10 fold jobs are submitted to Condor batch GPUs.

## Why the first DAGs stopped
- A DAG 9706466 (PREP 9706468) and B DAG 9706467 (PREP 9706469) exited at the PREP node.
- `A/prep.9706468.err` shows `PermissionError: [Errno 13] Permission denied: '/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_split'`. It came from `prepare.py:20`, which runs inside the coffea apptainer container on a batch node.
- No fold node started. Nothing was written to the split or cmds directories.
- Batch GPU jobs **without** a container did read EOS earlier: the fold-0 test job 9701591 finished with rc 0 ([[Projects/HToWW/framework/2026-11-12-bhive-pipeline-c1-resume]]). `fold_job.sh` uses no container.

## Why batch GPUs rather than lxplus-gpu
Checked at about 16:37 CET:
- The lxplus-gpu alias resolves to lxplus901, lxplus905 and lxplus908. Each has one shared **Tesla T4** (15 GB), already in use by other users:

  | node | GPU utilisation | GPU memory used |
  |---|---|---|
  | lxplus901 | 95% | 3993 MiB |
  | lxplus905 | 35% | 922 MiB |
  | lxplus908 | 99% | 4763 MiB |

- lxplus901 has `KillUserProcesses = yes` in `/etc/systemd/logind.conf` and `Linger=no`, so training there would die when the session ends.
- The fold-0 test gives about 10–20 min per fold on batch GPUs, plus dataset construction.

## What is running
- **Interactive preparation** (same `prepare.sh`/`prepare.py`, all checks unchanged), started 16:38 CET from laptop-held SSH sessions:
  - A on lxplus932;
  - B on lxplus901 (CPU only).
  - Logs: `~/bhive_prod_20261112_sol/{A,B}/prep.interactive.{out,err}`. Laptop-side logs: `~/htoww_runs/prep_{A,B}.local.log`.
  - Success writes `{A,B}/ready.json`.
- **Fold-only DAGs.** `{A,B}/folds.dag` is `train.dag` without the PREP node and its PARENT line. Both pass `condor_submit_dag -no_submit`. Each fold job still asserts `ready.json` `ready: true` before training.
- The training recipe is unchanged from the earlier note:
  - 30 epochs, batch 1024, lr 1e-3;
  - class weights only;
  - event%5 outer folds, b-hive 85/15 internal validation;
  - seeds 20261112.

## hDamp
A separate worker (Claude 2) implements tt hDamp as an alternative-sample systematic for both arms: [HToWW · hDamp systematic implementation](t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3A46cfa6bd-8e40-479d-8e0d-43f2822f9027%3Adelegate-task%3Aec148be8-df90-4343-94be-827fa7bfc04a). It may not submit jobs without Chirayu's OK.

## Next
After each `ready.json`: submit `folds.dag` for that arm, then monitor. Then export, check and register the folds, then RUN, cards and Combine. **No production model or limit exists yet.**

## RUN approval (Chirayu, 2026-11-12 ~16:55 CET)
- Chirayu: "Launch the RUN mode once you are done with training..."
- Scope as stated to him: RUN goes ahead for A and B only after all 10 folds per arm are checked, exported and registered (the model manifest). If any fold fails or looks wrong, stop and report rather than submit RUN.
- RUN reprocesses all NanoAOD (data + MC, nominal + every shift) with inline scoring, so it is a production-sized Condor submission per era. hDamp is not in RUN unless the hDamp worker's code is merged before submission.
