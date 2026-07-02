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

- Waiting on **Alex's latest commits** before proceeding (see 2026-07-01 log).

---

## Commands

```bash

```

---

## Tasks

- [x] See latest report [[report.pdf]] by Alex and advise how to proceed
- [x] Get Alex's unpushed commits, then explore code + try a basic CMSSW integration
- [ ] Implement new features

---

## Log

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
