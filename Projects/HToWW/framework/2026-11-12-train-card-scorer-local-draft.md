---
tags: [reference, framework]
status: active
date: 2026-11-12
source: laptop
evidence: local-draft-syntax-only
---

# TRAIN-to-card scorer: local draft, installation blocked

Continues [[2026-11-12-train-stat-only-limit]] after Chirayu returned and asked to continue the A/B result and presentation work. Current analysis source71eef55 was read over SSH; no tracked dirty code was observed. No delegate, GPU test or unchanged unit test was started.

At20:17CET the owner queue has A9706926–9706928 running,9706929–9706930 idle, B9706954 idle. Both DAGs running, no completed/failed nodes in their saved summaries. Live `condor_tail` of A9706926 confirms repaired startup reached DatasetConstructorTask and was reading input split shards around018477. It is not evidence of completed GPU epochs. Laptop suspension did not terminate submitted work.

Local draft `/tmp/htoww-edits/build_cards_from_train.py` implements the planned nominal offline path: production FoldModels held-out scoring, complete MC marker/partition/file checks, per-shard metadata/fold/source/row validation, reuse of make_templates/make_process_hists/finalize_templates/write_datacard, current negrw rescoring with BaseProcessor's hashed-bytes loader and predictor, current full-sample/Route B normalization, explicit merged-SR flag, and separate stat-only or rate-systematics modes. It retains autoMCStats and configured rateParams. No historical negrw weights are reused. It does not submit jobs or run Combine. No production model exists yet to execute the full path.

Local focused test draft `/tmp/htoww-edits/test_train_cards.py` checks hand-calculated signed counts/variances, uint64 fold IDs, current negrw rescoring and normalization after shard accumulation, incomplete/duplicate input rejection, wrong fold/source rejection, explicit split-variable merge requirement, and actual card nuisance/statistics rows. Tests have **not executed**: local environment lacks coffea/pyarrow/awkward. AST syntax parsing passed for both files. This is not a validated implementation or a new physics result.

Installing the scorer with scp to the analysis scripts/combine directory was **rejected by automatic approval review**: retained user instruction limited the monitoring schedule to read-only work and did not authorize code installation. The remote file was not written. No indirect workaround was attempted. Explicit approval to install and run the new tests in the established remote environment is required before dependent work. Drafts remain concrete/reviewable locally; no analysis input, live training recipe or output was changed. No push.
