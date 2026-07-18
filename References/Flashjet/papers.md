---
tags: [reference]
status: active
date: 2026-07-08
source: lxplus
---

# Flashjet — physics references (substructure algorithms)

Reading list for understanding **how the flashjet substructure algorithms work**
(operational, not theory). Downloaded 2026-07-08.

## 📄 Print this: [[flashjet-substructure-reader.pdf]]

A single **19-page** combined reader, built to print and read in one sitting:

1. **1-page algo cheatsheet** — every formula the code implements, cross-referenced
   to the exact function (`exclusive_jets_from_history`, `groom_from_history`,
   `lund_coordinates_from_history`), with a mental model.
2. **primary-source excerpts** — only the algorithm-definition pages clipped from
   each paper (not the full papers), in reading order.

Source for the cheatsheet: `papers/00_cheatsheet.tex`. Rebuild the reader with
`papers/build.sh`.

## Full papers (in `papers/`, if you want more than the excerpt)

| # | Paper | arXiv | Implements | Excerpt pages |
|---|-------|-------|-----------|---------------|
| 0 | Cacciari-Salam-Soyez — *The anti-kt jet clustering algorithm* | [0802.1189](https://arxiv.org/abs/0802.1189) | the distance measure `hist_d`, the `p=-1/0/+1` family | p2–3 |
| 1 | Cacciari-Salam-Soyez — *FastJet User Manual* | [1111.6097](https://arxiv.org/abs/1111.6097) | **F1** exclusive jets (`d_cut` / `n_jets` interface) | p14, p20 |
| 2 | Butterworth-Davison-Rubin-Salam — original Mass-Drop Tagger | [0802.2470](https://arxiv.org/abs/0802.2470) | **F2** the `μ` mass-drop condition | all (5p) |
| 3 | Dasgupta-Fregoso-Marzani-Salam — *modified Mass-Drop Tagger (mMDT)* | [1307.0007](https://arxiv.org/abs/1307.0007) | **F2** the `β=0` default | p24–26 |
| 4 | Larkoski-Marzani-Soyez-Thaler — *Soft Drop* | [1402.2657](https://arxiv.org/abs/1402.2657) | **F2** the `z > z_cut·(ΔR/R)^β` condition | p3, p6–7 |
| 5 | Dreyer-Salam-Soyez — *The Lund Jet Plane* | [1807.04758](https://arxiv.org/abs/1807.04758) | **F3** the `(z, ΔR, kt, ln 1/ΔR, ln kt)` coordinates | p4–6 |

Broader review (all of the above, with context): Marzani-Soyez-Spannowsky,
*Looking Inside Jets* — [1901.10342](https://arxiv.org/abs/1901.10342). Not bundled
(it's a full textbook); read ch. 1–2, 5–6 if you want the connective tissue.

## Where the algorithms live in the code
- `../../` (repo) `src/flashjet/history.py` — all three features + the shared
  `_pseudojet_p4`, `_resolve_roots`, `_resolve_parents` primitives.
- `src/flashjet/reference.py` — the readable single-event NumPy clustering (the
  bridge from the papers to the vectorized code; same algorithm, no batching).
- Cross-check tests: `tests/test_substructure.py`.
