---
tags: [reference]
status: active
date: 2026-09-04
source: lxplus
---

# Herwig generator-robustness test — build plan

## Why

Alex's suggestion: if C/A features don't help in-domain, do they help **robustness**
across generators? Precedent is Sung Hak Lim (AEI/KIAS 2019, arXiv:1807.03312 +
1904.02092), slide 22: trains on MG5+PY8+Delphes, tests on PY8 and HW7, finds CNN
and MLP+S2 "comparable within the PY8/HW7 uncertainty". Generator transfer is the
discriminating axis when in-domain performance is tied — which is our situation.

Physics argument: C/A merge history is built from **angular ordering**, exactly where
PY8 (dipole, pT-ordered) and HW7 (angular-ordered) differ most in structure. If ParT's
in-domain solution leans on generator-specific soft radiation while C/A features encode
the perturbative splitting sequence, C/A could degrade less under transfer.

**Prior: ~25–30%** that a real robustness gap shows up. The redundancy result
(share_bp recoverable at AUC 0.87) predicts both arms shift together.

**Decide in advance to report either way** — running a robustness test after an
in-domain null and only publishing a win is a look-elsewhere problem.

## Input data (verified present)

```
/eos/cms/store/user/hqu/datasets/JetClass/Herwig/
  test_20M    29G   <- ONLY THIS ONE IS NEEDED (inference only)
  train_100M  144G
  val_5M      7.2G
  train_10M   54K
```
200 ROOT files in test_20M, named `<Process>_<N>.root` (e.g. `HToBB_100.root`) —
same convention as the Pythia set. The existing Pythia `JetClass_test_mod` is
199 lz4 files, so it's a clean 1:1 correspondence.

## How DatasetConstructorTask works (read from tasks/dataset.py)

- Driven by a `--filelist <path>.txt`: one ROOT path per line.
- `read_in_samples_match_processes` (tasks/dataset.py:18) matches each line against
  `config["processes"]` by **substring**, first match wins, and groups them.
  So the .txt just needs full paths — the process is inferred from the filename.
- Output: `processed_files.txt`, `histogram.npy`, `weights.json` under
  `$DATA_PATH/DatasetConstructorTask/<config>/<dataset-version>/`
- `DATA_PATH` = `<b-hive dir>/output` (setup.sh:12), but the existing JetClass sets
  live at `/eos/cms/store/group/phys_btag/b_hive_HLT/b-hive/output/...` — check which
  is active before assuming the write location.

## Config facts (config/jet_class.yml)

- `processes`: TTBarLep, TTBar, HToWW2Q1L, HToWW4Q, HToBB, HToCC, HToGG,
  ZJetsToNuNu, ZToQQ, WToQQ  (10, order matters — matches truths)
- `truths`: label_QCD, label_Hbb, label_Hcc, label_Hgg, label_H4q, label_Hqql,
  label_Zqq, label_Wqq, label_Tbqq, label_Tbl
- `reference_flavour: label_Hbb`
- `treename: tree`
- `n_cpf_candidates: 128`
- bins_pt: 18 edges 500..1000 ; bins_eta: 11 edges -2.5..2.51

**~~TRAP~~ — pt/eta reweighting: RESOLVED, it does not matter.** Read
`utils/dataset/merging.py` and `tasks/inference.py` to settle this:
- `merge_datasets` only *writes a `weight` column* (`merged['weight'] = w`). It does
  **not** drop or resample jets — every jet is kept.
- `tasks/inference.py:143` opens `weights.json` **only to read `chunk_size`**, to compute
  the expected batch count for the progress bar. The per-jet weight is never applied to
  predictions, loss, or any reported metric.

So the Herwig set having its own pt/eta histogram has **no effect** on the comparison.
Both test sets are evaluated jet-for-jet unweighted. No need to force the Pythia
histogram through.

## Build — DONE, via `~/flashjet_condor/run_herwig_dataset.sh`

Wrapped in a script rather than run by hand, because of two gotchas:

1. **No `set -e`.** Sourcing `.bashrc` in a non-interactive shell returns nonzero,
   which aborts the script before it starts — the symptom is a **completely empty
   log** and no process, which looks like the job never launched.
2. **Must run under `tmux`.** `nohup` is not enough; the process is killed when the
   ssh session closes. (Same finding as [[lxplus-proxy-and-tmux]].)

```bash
tmux new-session -d -s herwig "cd ~/flashjet_condor && bash ./run_herwig_dataset.sh > herwig_full.log 2>&1"
```
tmux is **node-local** — this ran on `lxplus962.cern.ch`, so reattach there.

`--debug` first (1 file/process): completed in ~4 min, 1M jets, 10 classes balanced.

### Pre-flight checks that passed
- **Substring matching is safe.** `TTBarLep` precedes `TTBar` in `config["processes"]`,
  so the first-match-wins loop assigns correctly. Simulated the parse over all 200
  lines: 20 files per process, **0 unmatched**.
- **Herwig ROOT schema matches Pythia.** treename `tree`, 41 branches, 100k
  entries/file, all 10 `label_*` and every `part_*`/`jet_*` branch the config needs.
- **Space:** 2.1 PB free on `/eos/home-c`. Not a constraint.

### Verified output (debug build, `~/flashjet_condor/check_herwig.py`)
The lz4 files are **not** numpy — raw float32 buffer, `s[2:].reshape(-1, int(s[1]))`,
with trailing columns `[process, labels(10), weight]`. Read them the way
`utils/torch/LZ4Dataset.py` does.
- 2971 columns = **2959 features** (128 cand x 23 + 15 global) + 10 labels + 2 — matches Pythia.
- process -> label mapping correct; `TTBar` splits into `Tbqq`/`Tbl`, `ZJetsToNuNu` -> `label_QCD`.
- **0 NaNs, 0 multi-label rows, 0 unlabeled rows.**

## Then: inference + comparison — scripts written, ready to run

### 1. Symlink the dataset into the other config dirs
`~/flashjet_condor/link_herwig.sh`. b-hive resolves datasets at
`DatasetConstructorTask/<config>/<version>/`, and **every existing JetClass set here is
a symlink** into the shared `phys_btag` area (built by pkashko) — this Herwig set is the
first dataset actually built in my own tree. Each arm's config needs its own link.

### 2. Run inference
`~/flashjet_condor/run_herwig_roc.sh <baseline|ca|subjet> <iters>`

Same as `run_roc480_*.sh` with **only** `--test-dataset-version JetClass_herwig_test_mod`
changed. Guards before launching: N_CA_FEATURES==5 for the ca arm, the Herwig set exists
for that config, and `best_model.pt` is staged.

Checkpoints live at `.../<version>/ParticleTransformer_Paper_JetClass/epochs_0/nominal/`
(**two levels deeper** than the training-version dir). Verified staged and identical in
size to `model_480000.pt` for baseline and ca. The subjet training version is
`b_hive_paper_subjet_1`, **not** `b_hive_paper_compile_4_subjet`.

### 3. Compare
`perclass.py [test_dataset_version] [iters_k]` — now takes the test set as an argument
and dumps `~/flashjet_condor/perclass_results/<gen>_<K>k.json`. Re-ran on Pythia after
patching and it reproduces exactly (85.625 vs 85.523, Tbqq ratio 0.636), so the load
path is intact. Pythia 480k JSON is already saved.

`gen_robustness.py [iters_k]` — the actual answer. Reports per class

    deg_arm = rej_pythia / rej_herwig        (>1 = degraded under Herwig)
    d_deg   = deg_CA - deg_baseline          (<0 = C/A more robust)

**Metric is Δ(degradation), not absolute Herwig accuracy**, quoted on 1/eps_B.

**Checkpoint picked in advance: 480k** — both arms already have Pythia inference there,
so it is the cheap matched point. Testing several and reporting the best would be a
look-elsewhere problem.

## Scripts on AFS (~/flashjet_condor/)
- `run_herwig_dataset.sh` — build the Herwig test set (`--debug` for a smoke test)
- `check_herwig.py` — validate a built set: columns, label mapping, NaNs
- `link_herwig.sh` — symlink it into the ca / subjet / capair config dirs
- `run_herwig_roc.sh <arm> <iters>` — inference on Herwig
- `gen_robustness.py [K]` — the Pythia->Herwig degradation diff
- `perclass.py [test_ds] [K]` — per-class acc/rejection/AUC, now saves JSON
- `compare_arms.py` — 3-arm val/train table, `--last N`, `--loss`, `--csv`
- `prong.py` — subjet features vs prong count (val only)
- `prong2.py` — set-model version; **killed before producing results**
