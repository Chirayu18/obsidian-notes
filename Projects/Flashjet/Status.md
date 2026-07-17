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
- [x] Have Alex review the working-tree changes (NOT committed to repo per instruction) [completion:: 2026-07-15]
- [x] Commit changes — pushed to `origin/benchmarking` as `2e912ef` [completion:: 2026-07-15]
- [x] Add lund plane plot for ttbar + compare to the sample's STORED FastJet branches — done on
      HTCondor 9098883 (`make_ttbar_plots.py`, TTTo2L2Nu UL18 JMENano 150X, 12561 leading AK8 jets):
      (a) ttbar Lund plane w/ enhanced hard-splitting region; (b) pt 1.000002 / m_SD −0.041 GeV
      raw-to-raw vs stored `FatJet_*`/`SubJet_*`; (c) our z_g vs CMS subjet z |Δ|=1.6e-4, F1 √d12,
      stored τ ratios. [completion:: 2026-07-17]
- [x] Compare using all Jet candidates in an event as constituents — full-event anti-kt R=0.8
      on ALL PFCands/event, matched by dR to CMS's stored AK8 jets (`make_fullevent_plots.py`).
      Result: 7701 jets, pt median 1.0000 (100% within 2%), match dR 0.0019. [completion:: 2026-07-17]
- [x] Fix `make_cms_plots.py` to compare RAW-to-RAW (`FatJet_rawFactor` + raw subjets), regenerate all CMS plots — done on HTCondor 9087059 (pt 1.000000, m_SD −0.004 GeV) [completion:: 2026-07-17]
- [x] Re-title `cms_recluster.png` — now vs raw pt, median 1.000000 [completion:: 2026-07-17]
- [x] Regenerate `cms_lund.png` on the C/A tree [completion:: 2026-07-17]
- [x] Explain the ~4% m_SD outliers — fully attributed (50% missing soft constituents in
      `FatJetPFCand` [~0.1 GeV table floor], 23% storage rounding, 20% rounding-sensitive
      C/A trees, 7% z≈z_cut prong flips); relative agreement ~0.1% at all masses; NOT an
      algorithm error, not fixable from NanoAOD. See [[2026-07-17-msd-outlier-anatomy]].
      [completion:: 2026-07-17]
- [ ] Explore the merge history for **tagger inputs**: combine C/A variables (Lund coordinates,
      groomed z_g/R_g, declustering sequence) with jet understanding from kT (splitting scales
      √d12/√d23, exclusive-subjet structure) — idea: feed kT + C/A history-derived variables
      into jet taggers (all are cheap post-reads of the same histories, GPU-batchable)
- [x] Sample-comparison plots (QCD vs TTTo2L2Nu vs Run3 TTto4Q): Lund planes + 4q/QCD ratio
      (top-decay blob at ln kt≈3.7, >2× QCD), m_SD spectra w/ m_W peak + m_t shoulder, z_g,
      √d12, NEW R_g jet-by-jet exact match (99.2/95.9/87.0% within 0.01), β-family on 164k
      real QCD jets. HTCondor 9099026, full files. Run3 TTto4Q closes too — its bigger m_SD
      tail is the table-floor effect at 2024 pileup (90% pt<1, 99% Δm<0, rel. agreement 0.14%).
      [completion:: 2026-07-17]

---

## Log

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
