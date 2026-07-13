---
tags: [reference]
status: active
date: 2026-07-13
source: lxplus
---

# Substructure features — paper basis + justification plots

## Is the work based on papers? Yes — every algorithm is a published definition

The F1/F2/F3 implementation is not novel physics: it is a faithful, batched-GPU
implementation of standard published algorithms (that's the point — flashjet must
reproduce the community-standard definitions to be usable). The exact map:

| our code | paper | what it defines |
|---|---|---|
| `hist_d`, the p=−1/0/+1 family | Cacciari–Salam–Soyez, **anti-kt**, arXiv:0802.1189 | the generalized-kt distance measure |
| F1 `exclusive_jets_from_history` | **FastJet manual**, arXiv:1111.6097 (§ exclusive jets) | the d_cut / n_jets exclusive stopping rules |
| F2 `groom_from_history` (μ option) | Butterworth–Davison–Rubin–Salam, arXiv:0802.2470 | the original Mass-Drop Tagger |
| F2 default β=0 | Dasgupta–Fregoso–Marzani–Salam, **mMDT**, arXiv:1307.0007 | the modified mass-drop condition z > z_cut |
| F2 general (z_cut, β) | Larkoski–Marzani–Soyez–Thaler, **Soft Drop**, arXiv:1402.2657 | z > z_cut·(ΔR/R)^β declustering |
| F3 `lund_coordinates_from_history` | Dreyer–Salam–Soyez, **Lund jet plane**, arXiv:1807.04758 | the (z, ΔR, kt, ln 1/ΔR, ln kt) split coordinates |

The printable reader bundling the cheatsheet + the algorithm-definition pages of
each paper: [[flashjet-substructure-reader.pdf]] (see `References/Flashjet/papers.md`).
What *is* ours is the engineering: all three features are vectorized post-reads of
the recorded merge history (pointer jumping / lockstep tree walks), no re-clustering,
no kernel changes, CPU/GPU-agnostic.

## Justification plots (toy MC, generated 2026-07-13)

Toys: 1500 events each of QCD-like (one core + soft radiation) and W-like
(two prongs, pair mass 80.4 GeV, z∈[0.30,0.45]) fat jets, pt=500 GeV, R=0.8,
clustered with the f64 torch backend. Script: `make_plots.py` in the EOS dir below.
Link entries with previews: [[plots.md]].

1. **Lund plane** (F3): QCD gives the triangular soft plane; W-like shows the hard
   2-prong island exactly at the predicted (ln 1/ΔR, ln kt). ✔ shape physics.
2. **Soft-drop mass** (F2): QCD 70→38 GeV; W-like retained at m_W (95→85 GeV);
   100% tagged. ✔ grooming does what arXiv:1402.2657 promises.
3. **kt observables** (F1 + splitting scales): √d12 separates 25 vs 65 GeV;
   exclusive n=2 subjet z reproduces the generated z plateau for W. ✔.
4. **Parity + cost**: groomed mass vs an independent NumPy declustering agrees to
   1.7e-13 GeV (=f64 roundoff, exact); the decoders cost 10–100× less than the
   clustering itself on CPU. ✔ correctness + negligible overhead.

EOS: `/eos/user/c/cgupta/flashjet/plots/2026-07-13-substructure/`
(These complement `tests/test_substructure.py`, which pins the same algorithms to
independent NumPy tree-walks exactly, over all three algorithms and 30 random events.)

## Paper-figure reproductions (make_paper_plots.py)

A second script reproduces the *signature figures* of the papers themselves, for
side-by-side comparison — jet areas (anti-kt Fig 1), the Lund triangle closure
(Lund Fig 2), z_g vs analytic 1/z (Soft Drop), and groomed-mass ρ vs β (Soft Drop
Figs 3–4). Link entries + previews in [[plots.md]].

## The simulation

flashjet does not generate events; it only clusters them. The toy events in every
plot are hand-written generators I added in the plot scripts (NOT in the repo — the
only pre-existing event maker is `conftest.random_event`, uncorrelated noise for
tests). The paper-figure script uses a **toy leading-log parton shower**: emissions
sampled uniformly in the Lund plane (the fixed-coupling QCD picture the analytic
predictions assume), so the closure tests are quantitative. Full explanation of the
simulation and a step-by-step path to understanding the whole implementation:
[[2026-07-13-how-it-works]].
