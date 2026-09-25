---
tags: [reference, bug]
status: active
date: 2026-09-25
source: lxplus
---

# flashjet bug: `_pseudojet_p4` zeroed the last real particle in padded jets

**Fixed** on the flashjet `lmkt` branch, commit `46e566d` (local, not pushed). The fix is **not** on `benchmarking` or `origin`.

## The bug

`src/flashjet/history.py::_pseudojet_p4` seeds leaf four-vectors with

```python
ids = (mask.long().cumsum(1) - 1).clamp(0, M - 1)
pj.scatter_(1, ids, where(mask, p4, 0))
```

The mask-order cumsum stops growing after the last real particle, so **every padding slot gets the same id as the last real particle**. The scatter then writes both that particle's p4 and zeros into the same id:
- on CPU the last write wins, so the particle becomes zero;
- on CUDA, duplicate-index scatter order is undefined.

Every node containing that particle then has a wrong four-vector (its pT, mass, kT and so on).

It was found while testing the recursive merge embedding: a 71 GeV leaf came out with pT 0 in a boosted toy event.

## Fix

Padding slots are sent to the never-used id M−1 (real ids are at most 2n−2 ≤ M−2), and row M−1 is zeroed.

A regression test was added: `tests/test_history_decode.py::test_pseudojet_p4_padding_does_not_clobber_last_particle`. It checks that every leaf is intact and that the root equals the jet sum. It **fails on the old code** and passes on the fix. All 63 other history, substructure, splitting-scale and LM-kT tests pass.

## Who was affected

Every b-hive feature path that calls `_pseudojet_p4` on padded JetClass batches:
- `utils/flashjet_ca_features.py`: C/A branch-point features, used by **arms C, D, F**;
- `utils/flashjet_subjet_features.py`: the **subjet arm**;
- `utils/flashjet_ca_pair_features.py`: capair, which was only ever smoke-tested;
- anything else using `flashjet.history.lund_coordinates_from_history` or `groom_from_history`, which depend on the same helper.

JetClass constituents are pT-sorted, so the corrupted particle is usually the **softest one** in each jet. The effect on those arms' features is expected to be small but non-zero. **It has not been quantified yet.** To do so: recompute the arm C features with and without the fix on about 10k test jets and compare them.

## Caveat for future runs

b-hive imports flashjet from the working tree `/eos/home-c/cgupta/flashjet/FlastJetDemo/src` (`FLASHJET_SRC`). That repo is now on branch `lmkt`, so **any new or rerun b-hive job gets the fixed behaviour**. A rerun of an old arm is therefore not bit-identical to its original run.
