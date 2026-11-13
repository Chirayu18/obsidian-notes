---
tags: [reference, plot, production]
status: active
date: 2026-11-13
source: laptop
evidence: computed-from-held-out-outputs
---

# A completed training, performance plots and export in progress

Follows [[2026-11-12-train-card-scorer-implemented]]. All five A replacement DAG nodes finished successfully at **02:39:27CET** (`~/bhive_prod_20261112_sol/A/relaunch_20261112_startup1/folds.dag.dagman.out`, DAG9706925). Read all five production training_provenance.json files and independently compared each best_model.pt SHA256 to its recorded hash: status completed and checksums match. Seeds20261112, current config SHA2562024ecc544912967a47927d8557320336d84cb4ebe5b82b588c2d07db095e5ed, LZ4 validation-duplication fix recorded. Hardware is heterogeneous A100/H100MIG, so no cross-hardware bitwise reproducibility claim.

## Held-out performance

Computed from the already completed five InferenceTask prediction.npy/truth.npy outputs under `/eos/user/c/cgupta/HToWW/b-hive/output/InferenceTask/HPlusCHToWW_2dcats/hwwAv2sol_fde9a35d_f<i>_train/hwwAv2sol_fde9a35d_f<i>_test/hwwAv2sol_fde9a35d_f<i>/SimpleMLP_MultiClass/epochs_30/nominal/test_attack_nominal/`.

Exact per-fold row counts1390662/1392167/1393887/1390880/1391712 match the split manifest and total **6959308**. Saved predictions are logits; explicitly applied row-wise softmax before probability-based ROC calculations. Current config hash matched all five training records, fixing class order. These are **unweighted held-out MC, one class versus all others**; not luminosity-weighted yields, negrw-weighted performance, an A/B improvement claim or a fit result.

| Class | One-vs-rest AUC |
|---|---:|
|H+c|0.9558303563168085|
|Higgs background|0.7501446229329637|
|tt|0.7236757195524689|
|single top|0.5696579890550526|
|diboson|0.849010637095601|
|V+jets|0.9568905774149444|

Source calculation: [[2026-11-13-compute-a-performance.py]]. Numerical record: `~/bhive_prod_20261112_sol/A/performance_20261113.json`, copied to `framework/figures/2026-11-13-A-performance/performance.json`. Rendering source in the same local figure folder. Training/validation curves read the saved30-epoch metrics per fold. They are labelled **reported metrics**: b-hive averages training metrics over batches and validation metrics over events (`utils/models/base_model.py`). Validation accuracy is visibly variable; do not claim smooth convergence or full model acceptance from those curves alone. Source-inspected aggregation is not evidence of a new demonstrated training defect.

PNG files remain gitignored. Plot/source bytes on EOS were SHA256-compared with local artifacts and match; numerical record SHA256efe200a6ecce3f65ee79eb2a6959bbce39c5a7e3211c9d810c2f67b74f39d66f. ROC/training curves visually inspected locally; no deck edited.

## Plot entries

- **Date:**2026-11-13. **Description:**A held-out class-probability ROC curves, unweighted MC, five folds. **Path:**`/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_heldout_roc.png`. **Link:**[CERNBox ROC](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_heldout_roc.png).
- **Date:**2026-11-13. **Description:**A training/internal-validation loss and accuracy, all five folds, reported metrics. **Path:**`/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_training_curves.png`. **Link:**[CERNBox curves](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_training_curves.png).
- **Date:**2026-11-13. **Description:**A held-out confusion matrix, row-normalized within each true class, unweighted MC. **Path:**`/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_confusion_matrix.png`. **Link:**[CERNBox confusion matrix](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/output/prod_20261112_sol_A_performance_20261113/A_confusion_matrix.png).

## Export and continuation boundary

Existing unchanged `scripts/mva/export_fold_onnx.py` runs in the established b_hive environment against all five real checkpoints and the original split directory. Output directory `~/bhive_prod_20261112_sol/A/export_20261113/`, log `A/export_20261113.log`; remote PID2369295 at launch. Full held-out parity chosen, no diagnostic substitutions or new training. Fold0 completed parity on1390662held-out events, max|ONNX−PyTorch| **1.52e−6**, below1e−5. The remaining exports and final export_validation.json were not yet present at this snapshot. Do not register partial exports or run production cards with missing folds.

A local draft to make the exporter's max_events option stop reading early was rejected by automatic approval review under the retained read-only schedule instruction. It was **not installed**; source remains unchanged. Used the existing exporter instead, with full held-out reads/comparisons. No rejection workaround, source mutation, repeated GPU test, retraining or tolerance change.

Next: wait for the actual exporter result, inspect every fold and export validation record, then strict production registration using `register_folds.py`. Then invoke the tested `build_cards_from_train.py` per era with `--stat_only --also_rate_systematics --merge_channel_splits`, review policy/yields, combine cards and execute blind expected limits in CMSSW. No A or B new limit claimed yet. G3 fit-bin negrw closure remains scientifically open; it does not reinstate the superseded v2 adoption hold. B fold0 completed, fold1 ongoing, later folds4/3/2 newly submitted per [[Projects/HToWW/samples-and-production/full-rerun/2026-11-13-b-later-folds-parallel]].
