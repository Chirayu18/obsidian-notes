---
tags: [reference]
status: active
date: 2026-07-13
source: lxplus
---

# How the plots were simulated + how to understand the whole thing

Two questions answered here: (1) where the "events" in the plots come from, and
whether any of that was pre-existing, and (2) how to actually understand the
implementation rather than take it on faith.

## The simulation

### There is no Monte-Carlo generator involved

flashjet is a **clustering** library — it takes a list of particle 4-momenta and
groups them into jets. It does NOT generate physics events. So to make plots I had
to *create* input particles myself. Nothing in the repo generates events; the only
pre-existing "event maker" is `tests/conftest.py::random_event`, which throws
uniformly-random uncorrelated particles — fine for testing that two code paths agree,
useless for a physics plot (random noise has no jet structure to see).

So **all the toy event generators are new, written by me in the two plot scripts**
(`make_plots.py`, `make_paper_plots.py`), living on EOS *outside* the repo. They are
deliberately simple hand-written toys, not Pythia/Herwig:

- **make_plots.py** — ad-hoc: a QCD-like jet = one hard collinear core + soft
  wide-angle spray; a W-like jet = two hard prongs with pair-mass set to 80.4 GeV.
  Enough to show "grooming strips the soft stuff / keeps the two-prong mass".

- **make_paper_plots.py** — a proper **toy parton shower** for the closure tests. Real
  QCD radiates gluons with a probability density that is *uniform in the Lund plane*
  (flat in ln(1/θ) and ln kt) with strength ᾱ ≈ α_s C/π — this is the leading-log,
  fixed-coupling picture, and it's the exact approximation the Lund-plane and
  Soft-Drop analytic predictions are derived in. So I sample emissions uniformly in
  that triangle (density ᾱ=0.25 per unit area), attach each as a particle off a hard
  spine, and feed the result to flashjet. Because the *input* density is uniform-by-
  construction, the *measured* Lund plane must come back flat (it does: 0.17±0.02,
  flat to ~12%), and z_g must follow the analytic 1/z_g (it does, near-perfectly).

That last point is why these are called **closure tests**: I put in a distribution
whose answer is known analytically, and check the code reproduces it. The residual
Lund normalization offset (0.17 vs 0.25) is real physics — wide-angle primary
emissions merge into each other before C/A de-clusters them, so not every emission
survives as a distinct split. It is not a bug; it is why the shape is right but the
absolute plateau sits a bit low.

### Where clustering itself runs
The clustering IS the pre-existing repo code (Alex's backends). The plots call
`flashjet.cluster(..., backend="torch")` (f64 CPU) and, for Fig 1, the repo's
`nn_reference.cluster_event_nn`. The substructure reads (`lund_coordinates`,
`groomed_jets`, `splitting_scales`, `exclusive_jets`) are OUR additions. So the plots
exercise exactly the new code on top of Alex's clustering.

## How to understand all of this

The honest answer to "how did you implement this": I did **not** invent the physics —
every algorithm is a published recipe (see the paper map in
[[2026-07-13-substructure-plots]] and `References/Flashjet/papers.md`). The work was
(a) reading each paper's operational definition, (b) expressing it as a batched read
of the merge tree the kernels already record, (c) pinning it to an independent NumPy
walk so I know it's right. You can retrace exactly that path:

### Layer 1 — the physics (what the algorithms DO), ~half a day
Read the bundled reader `References/Flashjet/flashjet-substructure-reader.pdf`:
1-page cheatsheet first, then the clipped paper pages. You only need the operational
"what to compute at each split" from each paper, not the resummation theory. Order:
anti-kt (the distance) → FastJet manual (exclusive) → mMDT/Soft-Drop (grooming) →
Lund plane (coordinates). After this you can read every formula in the cheatsheet and
say what it means.

### Layer 2 — the one idea the code is built on
Every feature is a read of ONE data structure: the **merge tree**. Clustering merges
the closest pair repeatedly, building a binary tree per jet; the kernels record it as
four arrays (`hist_p1/p2/child/d`). Convince yourself of this by reading the single
readable clustering implementation, `src/flashjet/reference.py` (120 lines, plain
NumPy, no batching, no GPU). It builds the exact same history the fast kernels do.
Everything else is downstream of this file.

### Layer 3 — the features, read in this order
In `src/flashjet/history.py`, read the functions paired with their test in
`tests/test_substructure.py` (the test's `_ref_*` NumPy walk is the plain-English
version of the vectorized code):
1. `_pseudojet_p4` — rebuild every tree node's 4-momentum (just parent+parent sums).
2. `splitting_scales_from_history` (Alex's) — the one-hot-cumsum "rank each merge
   within its jet" trick; F3 and grooming reuse its layout.
3. `groom_from_history` ↔ `_ref_groom` — walk down the harder branch, test the
   soft-drop condition. The NumPy ref is a literal while-loop; the torch version is
   the same loop done for all jets at once with masks.
4. `lund_coordinates_from_history` ↔ `_ref_lund` — same walk, but log each split.
5. `exclusive_jets_from_history` ↔ `_ref_exclusive_partition` — "undo the last k
   merges" = keep a prefix of the sequence, re-root.

The trick that makes them fast (and looks intimidating) is **pointer jumping**
(`_resolve_parents`/`_resolve_roots`): instead of walking a chain of length N, you do
log₂N rounds of "everyone points to their pointer's pointer". Read `_decode` first —
it's the simplest use.

### Layer 4 — the GPU kernels (optional, only if you touch performance)
`triton_backend.py` (small-N, all in registers) then `triton_large.py` (the
Cacciari-Salam NN-array strategy). You do NOT need these to use or extend the
features — they produce the same history arrays; our code never touched them.

### The meta-lesson
The reason a large amount of code got written correctly is the **validation ladder**:
nothing is trusted against itself. Reference vs real FastJet → torch vs reference →
kernels vs torch → each feature vs an independent NumPy walk. If you add a feature,
you write its independent checker first; then the implementation only has to match
something you already believe. That discipline, not cleverness, is what made it work —
and it's the part most worth copying.
