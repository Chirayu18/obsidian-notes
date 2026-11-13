---
tags: [reference, production, decision]
status: active
date: 2026-11-13
source: laptop
evidence: executed-launch
---

# B folds 3 and 2 moved to SSH-owned interactive GPU runs; fold 4 stays in Condor

Chirayu asked for B folds 2, 3 and 4 to run **interactively**, later folds first, aiming for 2–3 h. This updates the ownership table in [[2026-11-13-b-later-folds-parallel]]. Training recipe, wrapper, inputs, versions and guards are unchanged.

## Ownership after this change (06:27 CET)

| Fold | Owner | State |
|---|---|---|
|0| serial 9706954.0 | completed train/inference earlier |
|1| serial 9706954.0, b9pgpun201 | running; test-dataset construction at 06:16 (file_152) |
|4| **Condor 9708299.0**, slot1_1@b9pgpun205 | **started ~06:17 CET before I could switch it**; the guard saw JobStatus 2 and aborted the removal, so it is kept as the single owner |
|3| **interactive lxplus909**, run_interactive PID 514021, wrapper 514128 | started 06:26:17, law began 06:27:11 on T4 GPU-beedd88b |
|2| **interactive lxplus902**, run_interactive PID 43173, wrapper 43317 | started 06:26:38 |

Records are under `~/bhive_prod_20261112_sol/B/parallel_later_20261113/`: `ownership.json` (updated; previous copy `ownership.before_interactive_20261113.json`), and `interactive_20261113/` with `preflight.sh`, `lxplus90{2,9}.preflight.log`, `fold{2,3,4}.removal.log`, `run_interactive.sh`, and per-run `fold<i>.<tag>.{out,err,pid,rc}`. Laptop SSH client logs are in `~/bfold_ssh_20261113/`.

## What was done

1. **Capacity (06:14 CET).** Checked the four GPU hosts I could reach with `nvidia-smi`. lxplus901: T4 at 98 % use by another process. lxplus908: another user's process on its GPU. lxplus905: idle GPU but load 28 on 28 cores. **lxplus902 and lxplus909: idle T4s and low load**, so they are the only two clean slots. lxplus903, 904, 907 and 912 failed SSH host-key verification. I did not bypass that.
2. **Preflight on 902 and 909**, without running any fold. Kerberos ticket and AFS token were present, expiring 11/14 07:10. `ready.json` ready=True. torch 2.5.1 with CUDA True on the T4. `law` resolved from the b_hive env. Parallel wrapper SHA256 `03d53030…5b0b`, matching the original recorded in ownership.json.
3. **Duplicate prevention, one fold at a time.** The script checked idle status, then ran `condor_rm`, then checked again. Fold 4 (9708299) was already running, so nothing was removed. **9708300 (fold 3) was removed at 06:23:29 and 9708301 (fold 2) at 06:24:02.** Both were idle with NumJobStarts 0, and their user logs show only submit/abort with no execute event. All four dataset, training and inference paths for f2 and f3 were absent before launch. No other job was touched, and serial 9706954 is unchanged.
4. **Failed first launch method.** I first started fold 3 inside `tmux` on lxplus909 (tag `lxplus909_20261113T062351`). The tmux server was killed when the SSH session closed (lxplus Linger=no). It produced no output and no EOS outputs; an empty scratch dir `/tmp/cgupta/bfold3_lxplus909_20261113T062351` remains. **On these nodes, tmux does not survive logout.** For a short time folds 3 and 2 had no owner, and I asked Chirayu. He chose **SSH-owned interactive**.
5. **Launch.** Each fold runs as a laptop `setsid nohup ssh lxplus "ssh -K lxplus90x 'run_interactive.sh <fold> <tag>'"`: laptop client PID 21200 for fold 3, 21418 for fold 2. `run_interactive.sh` creates a fresh node-local scratch dir (refusing one that already exists) and sets `_CONDOR_SCRATCH_DIR` and `TMPDIR` to it, so the generated fold script lives in scratch and not in the checkout. It then runs the **unchanged** `parallel_later_20261113/fold_job.sh B <fold>`, which handles the canonical DATA_PATH/B_HIVE_DIR, the ready check and the guarded commands. Exit code and time go to `.rc`.

## Caveats

- **The runs depend on SSH.** They stop if the laptop sleeps or the lxplus connection drops. An interrupted fold leaves a partial `DatasetConstructorTask/.../hwwBv2sol_46deafa8_f<i>_*` directory, and the guards will then refuse a rerun until Chirayu approves removing it. Nothing has been verified to survive a disconnect.
- **Timing (estimate, not a promise).** Fold 0 took about 3 h end to end in Condor. Fold 1 reached test construction in about 1.6 h. I expect **about 2–3.5 h per fold** on an unloaded node. B then finishes when the slowest of folds 1–4 does.
- AFS log content written on the node is only visible from other lxplus hosts once the file is closed. While a fold runs, read its log on that node.

## Completion criteria (not yet met)

For each fold, all of the following are required: `.rc` = 0; a `completed route B fold <i>` line; `DatasetConstructorTask` f<i>_train and f<i>_test; `TrainingTask/.../hwwBv2sol_46deafa8_f<i>_train/SimpleMLP_MultiClass` with a completed training_provenance whose best-checkpoint hash matches; and `InferenceTask/.../f<i>_train/f<i>_test/hwwBv2sol_46deafa8_f<i>/SimpleMLP_MultiClass/epochs_30`. Fold 4 must also exit successfully in Condor. Serial 9706954's "all folds completed" line is not evidence for folds 2–4.

## Results

_Pending; filled in when the processes exit._

## Next steps

- Keep the laptop awake and connected until folds 3 and 2 exit.
- Once all five folds pass the completion criteria, B export and registration can start through the unchanged route. No full RUN or Combine is part of this task.
