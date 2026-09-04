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

**TRAP — pt/eta reweighting.** `merge_datasets` reweights to `reference_flavour`
using `histograms` computed *from the input files*. The Herwig set will get its OWN
histogram, so the reweighting differs from Pythia's. For a transfer test this is
probably what you want (each set internally balanced), but it means **the two test
sets are not jet-for-jet matched**. State this, or investigate passing the Pythia
histogram. Check `weights.json` in both after building.

## Build command (NOT yet run — needs `--filelist` written first)

```bash
# 1. write the filelist
ls /eos/cms/store/user/hqu/datasets/JetClass/Herwig/test_20M/*.root \
  > ~/flashjet_condor/herwig_test.txt     # 200 lines

# 2. construct (CPU/IO bound, no GPU — safe to run alongside the trainings)
cd /eos/user/c/cgupta/flashjet/b-hive
source /afs/cern.ch/user/c/cgupta/.bashrc && micromamba activate b_hive
source setup.sh && law index
law run DatasetConstructorTask \
    --config jet_class \
    --dataset-version JetClass_herwig_test_mod \
    --filelist ~/flashjet_condor/herwig_test.txt \
    --coffea-worker 8 \
    --chunk-size 100000
```
Add `--debug` first for a 1-file-per-process smoke test.

**Note:** build with `--config jet_class` (no C/A or subjet columns). Those features
are computed at TRAIN time in `get_inpt`, not baked into the dataset — so ONE Herwig
dataset serves all three arms.

## Then: inference + comparison

Pattern from `~/flashjet_condor/run_roc480_{baseline,ca}.sh`:
copy `model_<N>.pt` -> `best_model.pt` in a `<version>_at<N>k` dir, set
`--TrainingTask-total-iterations <N>` so luigi skips training, run ROCCurveTask with
`--test-dataset-version JetClass_herwig_test_mod`.

Then `~/flashjet_condor/perclass.py` (already written) reads `prediction.npy` /
`truth.npy` and gives per-class acc / rejection / AUC. **Extend it to take a
dataset-version argument** so it can diff Pythia vs Herwig.

**Metric that matters: Δ(degradation), not absolute Herwig accuracy.**
baseline drops X, CA5 drops Y; the question is Y < X. Quote it as a
**rejection ratio** (1/eps_B), not accuracy — that's what an analysis cares about
and where a tail effect appears first.

**Pick the checkpoint in advance.** 480k has existing Pythia inference for both arms
(cheap, immediate). 1M is the endpoint but needs CA5 to finish. Testing several and
reporting the best is a look-elsewhere problem.

## Existing scripts on AFS (~/flashjet_condor/)
- `compare_arms.py` — 3-arm val/train table, `--last N`, `--loss`, `--csv`
- `perclass.py` — per-class acc/rejection/AUC from saved predictions (480k pair)
- `prong.py` — subjet features vs prong count (val only); ran, results below
- `prong2.py` — set-model version; **killed before producing results**
