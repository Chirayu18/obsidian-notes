---
tags:
  - flashjet
status: active
pinned: true
related:
date: 2026-06-23
---

# Flashjet — Status

> `BUTTON[toggle-status, toggle-pin]`  `VIEW[{status}]` · pinned: `VIEW[{pinned}]`

Repo: `../flashjet/FlastJetDemo/` (branch `benchmarking`). Report: [[report.pdf]] by Alexandre De Moor (19 Jun 2026, A100).

---

## Blocked on

- ~~Waiting on Alex's latest commits~~ — arrived 2026-07-08 (commit `29c9da8`), FF'd. Now unblocked.

---

## Commands

```bash
# work lives at /eos/home-c/cgupta/flashjet/FlastJetDemo (branch benchmarking)
# tests run in micromamba env b_hive (torch 2.5.1; pytest pip-installed there)
micromamba run -n b_hive python -m pytest -q          # 85 passed, 13 skipped (CUDA)
```

---

## Tasks

- [x] See latest report [[report.pdf]] by Alex and advise how to proceed
- [x] Get Alex's unpushed commits, then explore code + try a basic CMSSW integration
- [x] Implement new features — kt & C/A substructure (F1/F2/F3), see 2026-07-08 log
- [ ] Review the working-tree changes (NOT committed to repo per instruction)
- [ ] GPU-node follow-up: these are pure-torch so run on CUDA unchanged, but the Triton `decode=False` parity tests still need a GPU node

---

## Log

### 2026-09-25 — ParT pair-bias anatomy, flashjet p4 bug fixed, recursive-tree plan (Claude, lxplus)
- Tree substitution: ParT's pair bias is about 80% a function of the C/A common-ancestor node. C/A is the best tree; LM-kT and GNN trees do not help. See [[2026-09-25-part-pairbias-anatomy-and-tree-substitution]].
- **flashjet bug:** `history._pseudojet_p4` zeroed the last real particle in padded jets. Fixed on `lmkt` (`46e566d`), with a regression test. Arms C/D/F and subjet features were affected slightly; impact not yet quantified. See [[2026-09-25-flashjet-pseudojet-p4-padding-bug]].
- Next: recursive merge-embedding ParT. See [[2026-09-25-recursive-tree-network-plan]]. Recursion module written and tested; b-hive model not yet written.

### 2026-09-24 — LM-kT GNN ceiling evaluated (Claude, lxplus)
LM-kT is an IRC-safe learned clustering in flashjet: branch `lmkt`, `0bddc57`, 22 tests.
The GNN was trained on own Pythia truth-level jets on lxplus905 (T4).
- Top W pairing: C/A 0.33 → LM-kT 0.66 (truth oracle 0.86).
- W/Z: no gain.
- QCD: no sculpting.
- JetClass tagger proxy: +0.5 points over C/A tree features.
- IRC: identical to C/A.
- The GNN costs about 130× flashjet's Triton C/A, so inference needs the student.
Next: G2 (no pair bias + rank-K prong-membership channels), approved after this evaluation, with precomputed memberships.
See [[2026-09-24-lmkt-gnn-ceiling]].

### 2026-09-24 — No-pair arms C/E/F final at 1M (Claude, lxplus)
Full write-up in [[2026-09-24-nopair-arms-final]]. On test accuracy, measured against A (86.21): C −1.35, E −1.05, F −1.42, P −0.01, D −0.06.
F − C ≈ 0, so adding ln m² neither helps nor hurts. That answers Alex's "why is F worse than C".
The loss sits in the Zqq, Wqq, Hcc and Hgg AUCs. Conclusion: the pairwise bias is valuable for pair *selection*, not pair *description*.
Next: the learned carried-state teacher/student on the C/A recluster (Hi-LANDER-style).
Before that, check whether the raw JetClass ROOT files carry parton truth (`aux_genpart_*`) for prong labels.

### 2026-09-14 — PR #1 (cpu-backend) reviewed + test-merged clean (Claude, lxplus)
`DickyChant/FlastJetDemo` **PR #1** is Sitian Qian's **C++ CPU backend** (12 commits,
4–7 Sep, open, `cpu-backend`→`main`): `_cpu_kernel.cpp` running FastJet's strategy
ladder (N2Plain <24, tiled min-heap above) + OpenMP over events, a NumPy fallback,
CI that asserts the kernel actually built, and a pure-C++ benchmark claiming
**1.13–1.37× over FastJet single-threaded at every N from 20 to 6000** — measured
honestly (21 interleaved rounds, within-round ratios, FastJet timed *from-raw*).
It branches from `0c4314c`, i.e. **before** our substructure work.
**Test merge into `benchmarking` is clean**: 3 union conflicts (`api.py`, `CLAUDE.md`,
`.gitignore`), **154 passed / 13 skipped**, and F1/F2/F3 all still match the torch
backend exactly through the new CPU auto-routing. The p1/p2 swap seen vs torch
(28/480, same pair, same child, identical `d`) is **not a PR bug**: cpu(C++) matches
`nn_reference` in **0** disagreements, and `reference` vs `nn_reference` (24/60) and
`reference` vs `torch` (19/60) already disagree on `benchmarking` with no PR code.
Parent *order* is an undefined contract — it's a mutual-NN argmin tie; `hist_child`
and `hist_d` agree bitwise everywhere. Merge lives on
`merge-cpu-backend-test` at `/tmp/fj-merge-test` (node-local `/tmp`, will be reaped).
`benchmarking` untouched at `2e912ef`.
Note: [[2026-09-14-cpu-backend-pr-merge-test]].

### 2026-07-18 — Tagger-inputs study: the declustering sequence is the payload (Claude, lxplus)
Closed the tagger-inputs TODO. Per-jet extraction of kT scales (√d12/√d23/√d34) + C/A
grooming + Lund summaries on all three samples (HTCondor 9128460), then a weighted-logistic
AUC ladder on TTto4Q vs pt-reweighted QCD: mass-scale vars saturate at 0.794 (they're
0.8–0.97 correlated); adding the sequence/counting variables lifts it to **0.827** and
doubles QCD rejection at 30% eff. Best single non-mass variable: **n_drop** (0.764) —
decay jets pass soft drop in 0–1 declusterings, QCD needs many. ln kt of the 2nd-hardest
emission resolves the second decay splitting. Counting alone (no mass) matches the
mass-scale set. Signal has *fewer* Lund emissions than QCD despite higher pileup, so the
effect is physical. Note: [[2026-07-18-tagger-inputs]].

### 2026-07-17 — Outlier anatomy + three-sample comparison + Run3 TTto4Q (Claude, lxplus)
Two big items, both in the deck (now 34 slides) and pushed:
1. **m_SD outliers explained** (`outliers.py` + 3 follow-ups, HTCondor 9098953): the 4.4%
   |Δm|>0.5 GeV tail = 50% soft candidates missing from `FatJetPFCand` (~0.1 GeV table
   floor; proven via one-sided groomed-pt deficit, corr 0.42 with Δm) + 23% storage
   rounding + 20% rounding-sensitive C/A trees + 7% z≈z_cut prong flips. Relative
   agreement ~0.1% at all masses. NOT fixable from NanoAOD, not an algorithm error.
   Note: [[2026-07-17-msd-outlier-anatomy]].
2. **Three-sample comparison** (`make_compare_plots.py`, HTCondor 9099026): pulled Run3
   2024 `TTto4Q` JMENanoV15 (only other JMENano-with-constituents dataset anywhere;
   UL18 v9 TTToHadronic has NO PFCands). Lund planes QCD/2ℓ2ν/4q + ratio (top blob at
   ln kt≈ln(m_W/2), >2×), m_W/m_t peaks in our m_SD, NEW R_g jet-by-jet match
   (Δ ≤ 2×10⁻⁴), β-ordering on real data. Run3's larger tail = the same table-floor
   mechanism at 2024 pileup (90% jets pt<1, 99% Δm<0; rel. agreement 0.14%).

### 2026-07-15 — Committed substructure to benchmarking + presentation update (Claude, lxplus)
Committed the F1/F2/F3 working-tree changes to the flashjet repo and pushed:
`29c9da8..2e912ef` on `origin/benchmarking` (`src/flashjet/{history,api,__init__}.py`,
`README.md`, `tests/test_substructure.py`; 85 passed / 13 skipped confirmed green first).
Reworked the Marp deck for Alex (`presentation/flashjet-substructure.md`, now 25 slides):
**re-added** the CMS `FatJet_pt` reclustering and `FatJet_msoftdrop` soft-drop comparison
slides (with the PUPPI caveat), and added a **"How this plot was made"** block to every
correctness slide — dataset/toy generator, real-constituents-vs-toy input class (A/B/C),
selection cuts, R/z_cut/β, event counts, seed. Next: ttbar Lund + proper FastJet comparison.

### 2026-07-13 — Ran the clustering on REAL CMS data (Claude, lxplus)
Pulled UL18 QCD **JMENano** (150X reprocessing — the one format with `PFCand` +
`FatJetPFCand` so constituents exist) via DAS/xrdcp, grouped PF candidates per AK8
jet, and ran **our** flashjet anti-kt R=0.8 + F2 soft-drop + F3 Lund on them
(`make_cms_plots.py`, chunked to dodge the O(N³) torch-backend OOM):
- **`cms_recluster.png`** — our reclustered pt vs CMS `FatJet_pt`: tight diagonal.
- **`cms_softdrop.png`** — our `groom_from_history` (z_cut=0.1,β=0) vs CMS
  `FatJet_msoftdrop` jet-by-jet: hugs diagonal, median Δ=−4.19 GeV.
- **`cms_lund.png`** — primary Lund plane of 60285 real jets, full 1807.04758 structure.
Both pt and mass sit ~6%/~4 GeV below CMS — **PUPPI**, not a bug: CMS clusters
PUPPI-weighted constituents, NanoAOD stores raw pt with no per-candidate weight.
`diagnose.py` proves it: a per-jet `cms_pt/raw_pt` rescale drives the pt ratio to
1.000 and halves the mass offset, so F2 grooming is structurally correct.
Note: **[[2026-07-13-cms-validation]]**; entries in [[plots.md]].

### 2026-07-13 — Justification plots + paper-figure reproductions (Claude, lxplus)
Two plot scripts on EOS (`.../plots/2026-07-13-substructure/`):
- `make_plots.py` — justification plots on ad-hoc QCD/W toys: Lund plane (F3),
  soft-drop mass (F2), √d12 + exclusive-subjet z (F1), parity (matches independent
  NumPy declustering to 1.7e-13 GeV) + CPU cost (decoders 10–100× cheaper than
  clustering).
- `make_paper_plots.py` — reproduces the papers' signature figures using a toy
  leading-log parton shower: anti-kt Fig 1 jet areas, Lund Fig 2 triangle closure
  (flat interior 0.17±0.02), Soft-Drop z_g vs analytic 1/z (near-perfect), ρ vs β.
Notes: [[2026-07-13-substructure-plots]], [[plots.md]], and **[[2026-07-13-how-it-works]]**
(explains the toy simulation — none of it pre-existing — and a step-by-step path to
understanding the implementation). Paper basis: `References/Flashjet/papers.md`.
NOTE: the toy generators are mine, in the plot scripts (outside the repo); flashjet
itself only clusters, it does not generate events.

### 2026-07-08 — Alex's commit landed + new kt/C-A substructure features (Claude, lxplus)
**Alex pushed `29c9da8` "Adding new bench and opt"** to `origin/benchmarking`
(FF'd into local). It turned out to be exactly the four items the 2026-07-01
audit flagged as "in the report but missing from code" — so his unpushed local
work is now in: `decode=False` (T2.1), `ClusterOutput.splitting_scales()` +
`splitting_scales_from_history` (T2.2), the `N<=32 → N<=16` auto crossover
(T2.3), GPU-side collation `_scatter_gpu` (T3.1), plus the A100 profiling
artifacts. User then said: skip re-validating that; **implement the new features**.

**Implemented three substructure features** (all pure-torch reads of the merge
history Alex added — no kernel changes, CPU-runnable), each pinned to an
independent NumPy tree-walk + physical anchors:
- **F1 exclusive jets (kt)** — `exclusive_jets_from_history(..., n_jets=|d_cut=)`
  + `ClusterOutput.exclusive_jets`. Reduces to inclusive at the trivial cut.
- **F2 C/A declustering grooming** — `groom_from_history(...)` soft-drop / mMDT /
  mass-drop (`μ`), walking each jet down the harder branch (the O(log₂n) in the
  photo); `ClusterOutput.groomed_jets` / `mass_drop`.
- **F3 Lund coordinates** — `lund_coordinates_from_history(...)` → (B,J,S,6):
  z, ΔR, kt, ln1/ΔR, ln kt, d (the `Σℓw/Σw` weighted-recomb picture);
  `ClusterOutput.lund_coordinates`. d-channel ties exactly to splitting_scales.

Added `ClusterOutput.mask` (needed to map slots→ids), `tests/test_substructure.py`,
README + `__init__` exports. **Full suite: 85 passed, 13 skipped (CUDA-only).**

**NOT committed to the flashjet repo** (per user instruction) — changes are in
the working tree at `/eos/home-c/cgupta/flashjet/FlastJetDemo` for review:
`src/flashjet/{history,api,__init__}.py`, `README.md`, `tests/test_substructure.py`.

### 2026-07-01 — Message sent to Alex
Sent to **Alexandre De Moor**:
> Hello @Alexandre De Moor, I was wondering if you have your latest commits
> somewhere? I was thinking of exploring the code a bit more and trying a basic
> cmssw integration.

Waiting for his reply before proceeding.

### 2026-07-01 — Report vs. code audit (Claude, lxplus)
Read the 6-page [[report.pdf]] and cross-checked every claim against the repo
**and the full git history of all branches** (`main`, `benchmarking`,
`audit-remediation`). We are on `benchmarking`.

**The report describes four changes as implemented + validated (105 passing).
NONE of them are in the code or in git history on any branch:**

| ID | Report claim | Reality |
|----|--------------|---------|
| T2.3 | crossover `N≤32 → N≤16` | `api.py:151` still `N <= 32`; comment still says "crossover between N=32 and N=64" (the exact old wording report says it contradicts) |
| T2.1 | `cluster(..., decode=False)` | no `decode` param; 0 hits in history |
| T2.2 | `ClusterOutput.splitting_scales()` | 0 hits in history |
| T3.1 | GPU-side collation `_scatter_gpu` in `data.py` | 0 hits in history |

Supporting artifacts also absent: report cites `benchmarks/results/a100/`,
`report/gen_figures.py`, `PROFILING.md` — none exist. Actual results dir is
**T4**-based (`flashjet_ncu_B128_N512.ncu-rep`), matching HEAD commit
"Add standalone benchmarking + profiling suite (T4)". Report says "105 passed";
repo has **46 test functions**.

**Conclusion:** repo is at baseline (roadmap + T4 bench suite). Alex most likely
has **local commits he never pushed** → hence the message asking for them.

**How to proceed once Alex replies / code arrives** (my advice):
- T2.1 (`decode=False`), T2.2 (`splitting_scales`) — safe, self-contained; add pinning tests per the validation-ladder discipline. *(User chose to implement these two — on hold pending Alex.)*
- T2.3 crossover — **re-measure on the actual GPU first** (`scripts/tune_large.py`), don't hardcode 16 on faith; the A100 rationale artifacts aren't present.
- T3.1 collation — must stay bitwise-identical to NumPy collation.

---
- Forget the things above, as discussed with alex, the next task would be to implement some new things for kT and CA algorithm. Alex pushed latest comments and apparently he already started working on that. ![[PXL_20260702_123224004.MP.jpg]]
