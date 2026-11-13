---
tags: [reference, performance]
status: active
date: 2026-11-13
source: laptop
evidence: source-inspected-and-log-extracted
---

# Training input I/O and A epoch logs

Chirayu asked whether merging files would make training faster and requested A's training logs. No input merge, cache deletion, changed batching or retraining was performed.

Source inspection of `/eos/user/c/cgupta/HToWW/b-hive/tasks/dataset.py`, `DatasetConstructorTask.run`, shows the **parquet branch iterates sequentially** through sample file lists and calls `ak.from_parquet(infile)`; the requested coffea_worker parameter is used by the ROOT branch, not that parquet loop. The production commands separately construct each fold's training and test datasets, using chunk_size300. Thus many remote file opens/conversion steps repeat across the five overlapping training views. GPU training is not the dominant first-fold B elapsed time: B ran from01:36:58CET, training fold0 began04:22:17 and finished04:39:49 (17m32s). This supports a preparation/I/O bottleneck, not a measured benefit from an unimplemented merge optimization.

Sensible future design: keep original TRAIN outputs/provenance frozen; consolidate a fold-aware training cache into fewer, larger shards, preserving fold membership and source/sample/era lineage, and reuse constructed inputs via file lists. Do not merge held-out folds indiscriminately. Changing the constructed-file layout can change b-hive's internal85/15 validation assignment even with the same seed; equivalence, validation membership and full row/weight/schema checks are required before claiming unchanged training. This is a proposal, not an authorized new implementation or an extra production campaign. Current B outputs are untouched.

## User-readable A logs

New local folder `framework/logs/2026-11-13-A-training/` holds `fold0.training.log` through `fold4.training.log` and `manifest.json`. Each is a **verbatim stdout excerpt from “Epoch1of30” through the completion line**, preserving all30epochs, reported loss/accuracy, inference lines and route/fold completion. The huge preceding dataset-file listings are omitted. Raw stdout files remain unchanged at `~/bhive_prod_20261112_sol/A/relaunch_20261112_startup1/fold<i>.<9706926+i>.out` (about29.4MB each). Each excerpt header and manifest record the exact full-source SHA256 and source path. Only compact excerpts are committed locally; no raw full log copies, PNGs/PDFs or push.

Remote copies of the excerpts: `~/bhive_prod_20261112_sol/A/training_logs_20261113/`. Existing curve/ROC artifacts and their weighting/metric caveats are documented in [[2026-11-13-a-performance-plots]]. Excerpts are logs, not a new independent training run or full model acceptance. A export remains in progress; fold0 full held-out ONNX parity passed at1.52e−6.
