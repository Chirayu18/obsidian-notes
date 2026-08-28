---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# b-hive + JetClass ParT training — setup, and the XRootD filename trap

Setting up ParticleTransformer training on JetClass in a fresh b-hive clone, for
the flashjet work. Most of the session went into one non-obvious bug — recorded
here so it is never re-derived.

## The bug: `root://` paths silently collapse every input file to one name

`DatasetConstructorTask` failed repeatedly in the merge step with

```
FileNotFoundError: .../JetClass_val_mod/HToWW2Q1L__eoscms_0_5000.npy
```

**Root cause** — `utils/coffea_processors/base.py:129` derives the per-chunk output
filename from the input path:

```python
filename = "_".join(events.metadata["filename"].split("/")[1:]).split(".")[0]
```

The trailing `.split(".")[0]` truncates at the **first dot**. For an XRootD URL
`root://eoscms.cern.ch//eos/cms/store/.../HToBB_000.root` this yields `_eoscms`
for *every* file, because the hostname's first dot cuts everything after it.
The code implicitly assumes a local, dot-free path.

Measured:

| filelist | files | unique output basenames |
|---|---|---|
| `jetclass_val.txt` (`root://...`) | 50 | **1** (`_eoscms`) |
| `jetclass_val_local.txt` (`/eos/...`) | 50 | **50** |
| **`filelists/shuffled_ParT_files.txt`** (shipped in the repo) | 200 | **1** (`_eoscms`) |

**The repo's own committed filelist has this defect.** It is not specific to how I
built mine, and directory structure is irrelevant — truncation happens at the first
dot of `eoscms.cern.ch`, before any path component is reached. Anyone using the
shipped XRootD filelist either crashes the same way or silently trains on a fraction
of their data.

Two consequences, the first much worse than the second:
1. **Silent data loss** — all files of a class write to the same `.npy` names and
   overwrite each other; only the last survives (4/5 of a 5-file class discarded).
2. **The crash** — `file_list` then holds each path N times. `merge_datasets`
   (`utils/dataset/merging.py:131-132`) does `np.load` then `os.remove` per entry,
   so the second occurrence of a path fails on the already-deleted file.

**Fix: use plain local paths in the filelist.** `/eos/cms/...` is mounted on lxplus,
so XRootD buys nothing here.

```bash
sed 's|^root://eoscms.cern.ch/||' jetclass_val.txt > jetclass_val_local.txt
```

### Debugging dead-ends (don't repeat these)

- **"EOS concurrent writes"** — wrong. Fails identically on local `/tmp`.
- **"ThreadPoolExecutor race on duplicate paths"** — wrong. `--coffea-worker 1`
  fails too; the duplicates are sequential, so no concurrency is needed.
- **"NaN/Inf filtering drops jets"** (`lz4_processor.py` strips non-finite rows,
  and `part_logpt = log(sqrt(px²+py²))` → `-inf` on zero-padded candidates) —
  plausible but wrong: every `.npy` had exactly 5000 rows, none empty.
- **Retrying into a dirty output dir is uninformative** — the merge deletes each
  `.npy` as it consumes it, so a failed run eats its own inputs and the *next*
  run fails earlier on a *different* file. Always `rm -rf` the dataset dir first.

Verification: after the fix, `JetClass_val_mod` built clean — 50 `.lz4`, 12 GB,
**the same shape as the prebuilt copy** in the group area (50 files, 12 GB).
Then deleted; it was only a pipeline test.

## Setup that works

- **Clone**: `/eos/user/c/cgupta/flashjet/b-hive` (master `448bb65`).
  Repo is **private** on gitlab.cern.ch — anonymous HTTPS gives 401 and git then
  hangs silently on a credential prompt in non-interactive shells.
- **Env**: reuse the existing `b_hive` micromamba env at
  `/eos/user/c/cgupta/EPR_task/b-hive/micromamba`. New master needs three extra
  packages: `mlflow-skinny==2.22.0`, `pynvml==12.0.0`, `mlflow-token==1.1.0`.
  Without `mlflow`, `law index` silently drops `tasks.training` / `tasks.inference`
  (3 tasks indexed instead of 11). pip upgrades protobuf past TF 2.15's pin, but
  TF still imports fine.
- **`local_setup.sh`** (gitignored, sets `DATA_PATH`) must be created by hand —
  copied from the EPR_task checkout with the output path changed.
- **`config/jet_class.yml` needs a `processes:` key** — `tasks/dataset.py:63` does
  `config["processes"]` (direct index, not `.get`), so it is a hard `KeyError`
  otherwise. Processes are matched as **substrings of the file path, first match
  wins**, so order longest-first or `TTBar` swallows `TTBarLep`:

  ```yaml
  processes: ["TTBarLep","TTBar","HToWW2Q1L","HToWW4Q","HToBB","HToCC","HToGG","ZJetsToNuNu","ZToQQ","WToQQ"]
  ```

- **Data** (already on EOS, do **not** re-download via `Download_JetClass.py`):
  `/eos/cms/store/group/phys_btag/b_hive_HLT/jetclass/` — `jetclass_data/`
  (10 classes × 100 train files), `jetclass_val/` (50), `jetclass_test/` (200).
  100k events/file → train = 100M jets, matching the ParT paper.
- **Prebuilt datasets already exist** in the group area — check here *first*:
  `/eos/cms/store/group/phys_btag/b_hive_HLT/b-hive/output/DatasetConstructorTask/jet_class/`
  → `JetClass_train_100_mod` (239 GB), `JetClass_val_mod` (12 GB),
  `JetClass_test_mod` (48 GB).

## Storage

EOS user quota is **1 TB logical**, ~734 GB used → **~265 GB free**.
Building train (239 GB) + test (48 GB) = 287 GB does **not** fit. Train alone does,
barely. Reusing the prebuilt sets costs nothing.

## Model name

The command being reproduced specifies `--model-name ParticleTransformer2_JetClass_orig`,
which **does not exist** in b-hive — not on master, not on any branch, never in git
history (`git log --all -S`). Master has `ParticleTransformer2_JetClass`
(`utils/models/particletransformer2.py:767`): 10 classes, 8 encoder layers, 8 heads,
`embed_dim=128`, pair-embed + CLS token — the paper architecture, but with RMSNorm
and SwiGLU. The `_orig` suffix is presumably a local variant restoring the original
LayerNorm/GELU blocks. **Ask the author for it rather than assuming equivalence.**

## Training command (not yet run)

Needs a **GPU** — lxplus login nodes report `torch.cuda.is_available() == False`,
so `TrainingTask` must go through HTCondor (submit from AFS, e.g.
`~/flashjet_condor/`; EOS submit paths are rejected).

```bash
law run ROCCurveTask --training-version v_fg_1 \
  --dataset-version JetClass_train_100_mod_fine \
  --TrainingTask-val-dataset-version JetClass_val_mod \
  --test-dataset-version JetClass_test_mod \
  --config jet_class --model-name ParticleTransformer2_JetClass \
  --lr-scheduler batch_exp_decay --n-threads 16 --batch-size 512 \
  --learning-rate 0.001 --TrainingTask-loss-weighting True \
  --TrainingTask-use-iterations True --TrainingTask-total-iterations 1000000 \
  --TrainingTask-n-iters-per-save 20000 --epochs 0
```

The last five flags are the paper-reproduction settings — iteration-based training
(1M iterations, `--epochs 0`) with loss weighting, not epoch-based.

Related: [[flashjet-workflow]], [[2026-08-16-cmssw-integration-plan]]
