---
tags: [reference]
status: active
date: 2026-08-31
source: lxplus
---

# Reproducing the +1.31 C/A result (5 features, pre-soft-drop)

Exact state that produced the headline number: **ParT on JetClass gains +1.31
accuracy points from 5 per-particle C/A features**, once the 4-vector ordering
defect is fixed. Written down because the working tree on EOS has since moved on
to a 6th feature (`survives_SD`), and the b-hive changes are **not committed to
git** — they live only as edits in the EOS checkout.

Result detail and the investigation are in
[[2026-08-28-part-ca-features-implementation]]. This note is only "how to get back
here".

## The numbers being reproduced

Cluster 9251422, H100 NVL, batch 512, 20k iters (~2.4 epochs), seed 123456.

| checkpoint | baseline | + C/A (5 feat) | delta |
|---|---|---|---|
| 1 | 74.62% | 78.59% | +3.97 |
| 2 | 76.09% | 81.09% | +5.01 |
| 3 | **81.18%** | **82.49%** | **+1.31** |
| 4 | 80.82% | 82.32% | +1.50 |

Best val loss 0.5265 -> 0.4924. Clustering overhead **8.0 %** of the training step
(10.87 ms/batch vs 135.51 ms/batch).

## Frozen copies of every changed file

`Projects/Flashjet/code-snapshots/pre-sd-5features/` — committed to the vault, so
this survives anything that happens to the EOS checkout:

| file | goes to | what it carries |
|---|---|---|
| `flashjet_ca_features.py` | `utils/` | the 5-feature module, `N_CA_FEATURES = 5`, 186 lines, **no** SD code |
| `particletransformer2.py` | `utils/models/` | the **4-vector ordering fix** (class-level `cpf_candidates`, momenta last) |
| `base_model.py` | `utils/models/` | the train-time CA hook in `get_inpt` + `ca_feature_length` |
| `jet_class_ca.yml` | `config/` | `ca_features: true`, `ca_R: 0.8` |
| `jet_class.yml` | `config/` | stock + the required `processes:` key |

Base repo commit: **`448bb65`** (b-hive master). All five files are edits on top of
that; nothing else in the repo is touched.

## Restore

```bash
BH=/eos/user/c/cgupta/flashjet/b-hive
SNAP=~/obsidian-notes/Projects/Flashjet/code-snapshots/pre-sd-5features   # on the laptop
# (from lxplus, pull them out of the vault checkout wherever it lives)

cp $SNAP/flashjet_ca_features.py   $BH/utils/
cp $SNAP/particletransformer2.py   $BH/utils/models/
cp $SNAP/base_model.py             $BH/utils/models/
cp $SNAP/jet_class_ca.yml          $BH/config/
cp $SNAP/jet_class.yml             $BH/config/
```

On lxplus there is also `utils/flashjet_ca_features.py.bak_sd`, the same pre-SD
module — but that is an untracked file on EOS, so treat the vault copy as the
authority.

**Verify the restore before training** — this checks the thing that actually
mattered:

```bash
cd ~/cawork && python chk4.py      # expects: cpf width 23 (baseline) / 28 (ca)
                                   # "4-vector correct at [-4:]? True" in BOTH
```

`ALL CHECKS PASS` means the ordering fix is live and the CA columns sit at
`[-9:-4]`, i.e. before the trailing 4-momentum. With 6 features the CA block is at
`[-10:-4]` and the width is 29 — if you see that, you are on the SD version, not
this one.

## Prerequisites (already done, do not redo)

- **Datasets**: prebuilt, symlinked into `DATA_PATH` under **both** config names,
  so neither arm rebuilds:
  `output/DatasetConstructorTask/jet_class{,_ca}/JetClass_{val,test}_mod`
  -> `/eos/cms/store/group/phys_btag/b_hive_HLT/b-hive/output/DatasetConstructorTask/jet_class/...`
- **Env**: micromamba `b_hive` at `/eos/user/c/cgupta/EPR_task/b-hive/micromamba`.
  Python directly at
  `/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python`.
- **`FLASHJET_SRC`** must be exported: `/eos/home-c/cgupta/flashjet/FlastJetDemo/src`.

## Rerun

```bash
cd ~/flashjet_condor
condor_submit v4fix.sub          # run_v4fix.sh: baseline then CA, one job, one GPU
```

~2.1 h on an H100 NVL. Both trainings run **sequentially in a single job** so they
land on the same physical card and the timing comparison is apples-to-apples.

Results:
```
$BH/output/TrainingTask/jet_class/JetClass_val_mod/train_v4fix_baseline/...
$BH/output/TrainingTask/jet_class_ca/JetClass_val_mod/train_v4fix_ca/...
```
(To avoid clobbering, change `--training-version` in `run_v4fix.sh` — law skips a
training whose output already exists.)

## Gotchas that will bite on a rerun

- **`request_memory` is load-bearing.** Use the template's **32 GB** verbatim. The
  site policy scales `RequestCpus` from the memory ask (32 GB -> 11 CPUs); lowering
  it to 16 GB gives 6 CPUs and matched *fewer* free slots, not more.
- **`--val-dataset-version` is UNPREFIXED for `TrainingTask`** but must be
  `--TrainingTask-val-dataset-version` for `ROCCurveTask`, which does not inherit
  `ValDatasetDependency` and silently drops the unknown prefixed param — law would
  then look for a different, untrained task.
- **Do not add the CA names to `cpf_custom_features`.** That list drives the on-disk
  reshape (`input_dims`); adding them there corrupts the read. They are appended at
  runtime instead, and `calculate_feature_length` is deliberately left alone.
- **Never append the CA columns at the very end** — ParT reads `cpf_features[:, :, -4:]`
  as its Lorentz vector. They go *before* the trailing four.
- **`set -u` breaks micromamba activation** (`libblas_mkl_activate.sh` reads an unset
  `MKL_INTERFACE_LAYER`).
- A **T4** forces batch 128 and is flashjet's worst case — the `.sub` pins full
  H100 NVL / A100 / H200 cards for this reason.

## Caveats on the result itself

- Trains on `JetClass_val_mod` with `train_val_split=0.85` — a held-out split of the
  *validation* set, not the official test set. ROC on `JetClass_test_mod` was
  submitted as cluster 9252639.
- **~2.4 epochs, nowhere near converged.** The gap shrinks across checkpoints
  (+3.97, +5.01, +1.31, +1.50), so C/A may be mostly *accelerating convergence*
  rather than raising the ceiling. An 80k-iteration run would settle this and is the
  single most valuable follow-up.
- Do **not** quote cluster 9246381 (80.23 / 77.86, "C/A loses by 2.4"): that ran with
  the 4-vector defect in both arms.

## Known cleanups deferred in the SD version (not in this snapshot)

In `_survives_sd`, added after this snapshot: `kept` is populated but never read,
and `sib` is an unused parameter. Neither affects correctness (0 leaf mismatches vs
`groom_from_history`); both to be removed.

Related: [[2026-08-28-part-ca-features-implementation]],
[[2026-08-28-bhive-jetclass-part-setup]], [[flashjet-workflow]]
