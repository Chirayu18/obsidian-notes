---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# Runbook: b-hive JetClass → ParT training on lxplus

Exact commands, start to finish. Background and the bugs behind some of these
steps are in [[2026-08-28-bhive-jetclass-part-setup]].

Everything below runs on lxplus. Paths are literal.

---

## 0. One-time setup

### 0.1 Clone

The repo is **private** on gitlab.cern.ch. Anonymous HTTPS returns 401 and git then
hangs on a credential prompt (silently, in non-interactive shells). Clone
interactively so you can answer the prompt:

```bash
cd /eos/user/c/cgupta/flashjet
git clone https://gitlab.cern.ch/cms-btv/b-hive.git
```

Do **not** clone into AFS home — it is near quota. Verify:

```bash
cd /eos/user/c/cgupta/flashjet/b-hive && git log --oneline -1
# 448bb65 Merge branch 'parquet_format' into 'master'
```

### 0.2 Environment

Reuse the existing `b_hive` env; do not build a new one.

```bash
export MAMBA_EXE="/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba"
export MAMBA_ROOT_PREFIX="/eos/user/c/cgupta/EPR_task/b-hive/micromamba"
$MAMBA_EXE run -n b_hive pip install \
    "mlflow-skinny==2.22.0" "pynvml==12.0.0" "mlflow-token==1.1.0"
```

Those three are new on master. **Without `mlflow`, `law index` silently drops
`tasks.training` and `tasks.inference`** — you get 3 indexed tasks instead of 11 and
`TrainingTask` simply does not exist. pip will warn that it upgraded protobuf past
TensorFlow 2.15's pin; TF still imports fine.

### 0.3 `local_setup.sh`

Gitignored, so it does not come with the clone. Create it:

```bash
echo 'export DATA_PATH=/eos/user/c/cgupta/flashjet/b-hive/output' \
    > /eos/user/c/cgupta/flashjet/b-hive/local_setup.sh
mkdir -p /eos/user/c/cgupta/flashjet/b-hive/output
```

### 0.4 The `processes:` key

`config/jet_class.yml` ships without it, but `tasks/dataset.py:63` does
`config["processes"]` — a direct index, so it is a hard `KeyError`. Prepend:

```yaml
processes:
- "TTBarLep"
- "TTBar"
- "HToWW2Q1L"
- "HToWW4Q"
- "HToBB"
- "HToCC"
- "HToGG"
- "ZJetsToNuNu"
- "ZToQQ"
- "WToQQ"
```

**Order matters.** Processes are matched as substrings of the file path and the
first match wins, so `TTBarLep` must precede `TTBar` or every TTBarLep file is
misfiled as TTBar. Longest-first is the safe rule.

### 0.5 Activate (every session)

```bash
cd /eos/user/c/cgupta/flashjet/b-hive
export MAMBA_EXE="/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba"
export MAMBA_ROOT_PREFIX="/eos/user/c/cgupta/EPR_task/b-hive/micromamba"
eval "$($MAMBA_EXE shell hook -s posix)"
micromamba activate b_hive
source setup.sh
law index          # expect: written 11 task(s)
```

---

## 1. Datasets

### Option A — reuse the prebuilt ones (recommended)

They already exist in the group area and cost nothing:

| version | size |
|---|---|
| `JetClass_train_100_mod` | 239 GB |
| `JetClass_val_mod` | 12 GB |
| `JetClass_test_mod` | 48 GB |

The area is **read-only**, so symlink them into `DATA_PATH` rather than pointing
`DATA_PATH` at it (law needs to write training output):

```bash
G=/eos/cms/store/group/phys_btag/b_hive_HLT/b-hive/output/DatasetConstructorTask/jet_class
D=/eos/user/c/cgupta/flashjet/b-hive/output/DatasetConstructorTask/jet_class
mkdir -p $D
ln -sfn $G/JetClass_train_100_mod $D/JetClass_train_100_mod_fine
ln -sfn $G/JetClass_val_mod       $D/JetClass_val_mod
ln -sfn $G/JetClass_test_mod      $D/JetClass_test_mod
```

Note the rename: the command everyone passes around says
`JetClass_train_100_mod_fine`, but upstream only has `JetClass_train_100_mod`.
The symlink reconciles them.

`processed_files.txt` inside those datasets holds absolute paths into the group
area, which resolve fine — nothing needs rewriting. Confirm law sees them:

```bash
law run TrainingTask --config jet_class \
    --model-name ParticleTransformer2_JetClass \
    --dataset-version JetClass_train_100_mod_fine \
    --training-version v_fg_1 --epochs 0 --print-status 1
# DatasetConstructorTask targets should read "existent"
```

### Option B — build them yourself

Only if you need a different selection. **~300 GB for all three**; check quota first:

```bash
eos root://eoshome-c.cern.ch quota /eos/user/c/cgupta | tail -2
# logical used vs 1.00 TB limit — need ~299 GB free for all three
```

Build the filelists. **Use plain `/eos/...` paths, never `root://` URLs** —
`utils/coffea_processors/base.py:129` truncates the output filename at the first
dot, so an XRootD hostname collapses every input file onto one output name,
silently discarding most of your data (see [[2026-08-28-bhive-jetclass-part-setup]]):

```bash
cd /eos/user/c/cgupta/flashjet/b-hive
J=/eos/cms/store/group/phys_btag/b_hive_HLT/jetclass

for d in $(ls $J/jetclass_data); do ls $J/jetclass_data/$d/*.root; done \
    > filelists/jetclass_train_local.txt      # 1000 files
ls $J/jetclass_val/*.root  > filelists/jetclass_val_local.txt    # 50
ls $J/jetclass_test/*.root > filelists/jetclass_test_local.txt   # 200
```

Sanity check — every path must yield a *distinct* name:

```bash
python3 -c "
def mk(p): return '_'.join(p.split('/')[1:]).split('.')[0]
ls=[l.strip() for l in open('filelists/jetclass_val_local.txt') if l.strip()]
print(len(ls), 'files ->', len({mk(p) for p in ls}), 'unique names')"
# must print: 50 files -> 50 unique names   (1 unique name = broken)
```

Then build. **Always `rm -rf` the target dir first** — the merge deletes each `.npy`
as it consumes it, so re-running into a partial directory fails on a *different*
missing file every time and tells you nothing:

```bash
rm -rf output/DatasetConstructorTask/jet_class/JetClass_val_mod
law run DatasetConstructorTask --config jet_class \
    --dataset-version JetClass_val_mod \
    --filelist filelists/jetclass_val_local.txt \
    --coffea-worker 12
```

Same for `JetClass_test_mod` / `jetclass_test_local.txt` and
`JetClass_train_100_mod_fine` / `jetclass_train_local.txt`. Val takes ~15 min;
train is 20× the files. Run long builds under `tmux`, not `nohup`.

Done when: `n .lz4` files equal the input count, zero `.npy` left over, and
`weights.json` + `histogram.npy` are present.

---

## 2. Condor submission

Training needs a GPU; lxplus login nodes have none
(`torch.cuda.is_available() == False`). Submit from **AFS** — EOS submit paths are
rejected by the schedd.

### 2.1 Executable — `~/flashjet_condor/run_jetclass_part.sh`

```bash
#!/bin/bash
cd /eos/user/c/cgupta/flashjet/b-hive
source /afs/cern.ch/user/c/cgupta/.bashrc
micromamba activate b_hive
source setup.sh
law index

nvidia-smi

COMMON="--config jet_class \
    --model-name ParticleTransformer2_JetClass \
    --dataset-version JetClass_train_100_mod_fine \
    --training-version v_fg_1 \
    --lr-scheduler batch_exp_decay \
    --n-threads 4 \
    --batch-size 512 \
    --learning-rate 0.001 \
    --epochs 0"

# 1) training (validation set binds here)
law run TrainingTask $COMMON \
    --val-dataset-version JetClass_val_mod \
    --loss-weighting True \
    --use-iterations True \
    --total-iterations 1000000 \
    --n-iters-per-save 20000

# 2) ROC curve on the test set, reusing the training above
law run ROCCurveTask $COMMON \
    --test-dataset-version JetClass_test_mod \
    --TrainingTask-val-dataset-version JetClass_val_mod \
    --TrainingTask-loss-weighting True \
    --TrainingTask-use-iterations True \
    --TrainingTask-total-iterations 1000000 \
    --TrainingTask-n-iters-per-save 20000
```

**Why two steps instead of one `ROCCurveTask`:** `ROCCurveTask` inherits
`TestDatasetDependency` but **not** `ValDatasetDependency`
(`tasks/plotting.py:30-32`), so `--TrainingTask-val-dataset-version` passed to it is
silently dropped by luigi — training then runs with `val_dataset_version=None` and
falls back to a `train_val_split` of the training data. Running `TrainingTask`
directly makes the flag bind. Verify before submitting:

```bash
law run TrainingTask ... --print-status 1 | grep -o "val_dataset_version=[^,]*"
# must show JetClass_val_mod, not None
```

The last four flags are the paper-reproduction settings: iteration-based training
(1M iterations, `--epochs 0`) with loss weighting.

### 2.2 Submit file — `~/flashjet_condor/jetclass_part.sub`

```
executable = run_jetclass_part.sh

arguments = $(ClusterId)$(ProcId)

output = output/jetclass_part.$(ClusterId).$(ProcId).out
error  = output/jetclass_part.$(ClusterId).$(ProcId).err
log    = output/jetclass_part.$(ClusterId).log

should_transfer_files = YES
when_to_transfer_output = ON_EXIT

getenv = True

request_GPUs = 1
request_CPUs = 4
request_memory = 32 GB

requirements = (TARGET.GPUs_DeviceName == "NVIDIA H100 NVL" || \
                TARGET.GPUs_DeviceName == "NVIDIA A100-PCIE-40GB" || \
                TARGET.GPUs_DeviceName == "NVIDIA H200") && \
               (TARGET.OpSysAndVer =?= "AlmaLinux9")

+JobFlavour = "nextweek"
queue
```

Two things to keep right:

- **Pin exact full-card device names.** `regexp("H100", ...)` also matches the MIG
  partitions `H100L-2-24C` / `H100L-1-12C`, which are a fraction of a card.
- **Keep `request_CPUs` low.** 16 CPUs narrowed the eligible pool to 6 slots and the
  job sat idle for two hours; 4 CPUs across A100/H100/H200 gives 21, and the job
  started within minutes. Keep `--n-threads` equal to `request_CPUs` so the
  dataloader does not oversubscribe.

Current pool (`condor_status -af GPUs_DeviceName | sort | uniq -c`): 42 H100 NVL,
35 A100-PCIE-40GB, 9 H200 full cards.

### 2.3 Submit and watch

```bash
cd ~/flashjet_condor
mkdir -p output
condor_submit jetclass_part.sub          # -> "1 job(s) submitted to cluster NNNNNNN"

condor_q NNNNNNN -nobatch                # I = idle, R = running, H = held
condor_q NNNNNNN -better-analyze | grep -E "slots match|would match"
tail -f output/jetclass_part.NNNNNNN.0.out
```

`condor_q` returning empty does **not** mean the job finished — a busy schedd times
out and prints nothing. Confirm with `condor_history NNNNNNN` before concluding
anything.

To change resources, remove and resubmit; nothing is lost if it never started:

```bash
condor_rm NNNNNNN
```

---

## Gotchas, condensed

| Symptom | Cause |
|---|---|
| `KeyError: 'processes'` | `jet_class.yml` needs the `processes:` key (§0.4) |
| `law index` writes only 3 tasks | `mlflow` missing → training/inference modules dropped (§0.2) |
| `FileNotFoundError: ..._eoscms_0_5000.npy` | XRootD paths in the filelist (§1B) |
| Same, on a re-run, different file | Stale output dir; `rm -rf` it first (§1B) |
| `val_dataset_version=None` | Flag passed to `ROCCurveTask` instead of `TrainingTask` (§2.1) |
| Job idle for hours | Too many CPUs / too narrow a GPU match (§2.2) |
| AFS `Permission denied` mid-session | Kerberos ticket alive but AFS token gone → run `aklog` |

## Open

- `ParticleTransformer2_JetClass_orig` (in the command as circulated) **does not
  exist** in b-hive — no branch, no history. Substituted
  `ParticleTransformer2_JetClass`, which is the paper architecture but with RMSNorm
  and SwiGLU. Confirm with the author before treating a result as a reproduction.

## Run log

- **9246292** — 16 CPUs, H100-only. Idle 2 h, never started (6 eligible slots). Removed.
- **9246305** — 4 CPUs, A100/H100/H200. 21 eligible slots; started within minutes.
  Submitted 2026-08-28 15:39.

Related: [[2026-08-28-bhive-jetclass-part-setup]], [[2026-08-28-bhive-maintainer-message]], [[flashjet-workflow]]
