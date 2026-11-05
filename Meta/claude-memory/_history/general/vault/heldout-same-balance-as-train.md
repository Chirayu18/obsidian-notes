---
name: heldout-same-balance-as-train
description: Validation/test sets must have exactly the training class balance; never evaluate on a balanced set reweighted to the training priors
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8cb963cf-d304-4ee6-8f09-c79b0129a6f5
  modified: 2026-11-03T06:02:03.267Z
---

Held-out sets (validation for checkpoint selection, and test) must have the SAME class balance as the training set. Do not use a balanced set (e.g. JetClass val/test, 10% per class) reweighted to the training priors, even though the reweighting is right in expectation.

**Why:** the user rejected the reweighted evaluation on 2026-11-03 (kappa-HCE replica). A balanced validation set also holds far more rare-signal events (20k Hcc vs ~355 at training balance), so checkpoint selection becomes unrealistically well informed compared with a real held-out split of the training data.

**How to apply:** subsample each class to counts exactly proportional to the training counts; the most abundant class binds (keep all of it). Score unweighted. For a stable estimate use several such subsamples with fixed seeds and score every model on the same ones. Implemented in `flashjet/kappa_hce/htoww_replica/check/rescore_natural.py` and `train_rescue.py` load_natural. Related: [[Meta/claude-memory/_history/projects/Flashjet/vault/flashjet-workflow|flashjet-workflow]].
