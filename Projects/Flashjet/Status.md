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
- [ ] Have Alex review the working-tree changes (NOT committed to repo per instruction)
- [ ] GPU-node follow-up: these are pure-torch so run on CUDA unchanged, but the Triton `decode=False` parity tests still need a GPU node

---

## Log

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
