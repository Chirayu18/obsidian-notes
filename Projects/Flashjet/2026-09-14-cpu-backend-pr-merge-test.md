---
tags: [reference]
status: active
date: 2026-09-14
source: lxplus
---

# PR #1 (cpu-backend) — what it is, and a test merge into `benchmarking`

## What the PR is

`DickyChant/FlastJetDemo` **PR #1**: `cpu-backend` → `main`, by **Sitian Qian**
(sitian.qian@cern.ch — the repo owner, not Alex), 12 commits dated 4–7 Sept 2026,
**open**, 12 ahead / 0 behind `main`. The repo is private, so the PR URL 404s
unauthenticated — read it via the authenticated clone:
`git fetch origin '+refs/pull/1/head:refs/remotes/origin/pr/1'`.

It adds a **compiled C++ CPU backend**, ~2430 lines / 13 files:

| file | what |
|---|---|
| `src/flashjet/_cpu_kernel.cpp` (980 L) | the generalized-kt algorithm in C++; FastJet's strategy ladder — N2Plain under 24 constituents, (y,φ) tile grid + indexed min-heap (N2MinHeapTiled) above, with FastJet's lazy-tiling pruning (`max_NN_dist` cell bound, R cap). OpenMP over events, per-worker scratch |
| `cpu_backend.py`, `_native.py`, `setup.py` | Python side + **NumPy fallback** if no C++ compiler (build is optional by design, ~6× slower) |
| `api.py` | `backend="auto"` now routes **CPU tensors to `cpu`** instead of `torch` — a default-behaviour change |
| `tests/test_cpu_vs_reference.py` (236 L) | step-for-step merge-history equivalence vs the NumPy mirror |
| `.github/workflows/cpu.yml` | ubuntu+macos × py3.9/3.12; **asserts `_native.HAS_NATIVE`** so a silent NumPy fallback can't pass green |
| `bench/bench_cpp_vs_fastjet.cpp`, `scripts/bench_cpp.sh` | pure-C++ vs pure-C++ benchmark harness |

**Headline claim:** beats FastJet single-threaded at *every* size measured,
**1.13–1.37×**, N=20 → 6000, including vs `N2MHTLazy9` (FastJet's fastest strategy).
Methodology is honest: 21 interleaved rounds, median + 16–84th percentile band,
ratio formed *within* each round so thermal drift cancels, and FastJet measured
**from-raw** (px,py,pz,E) rather than the flattering cached-`PseudoJet` path. It
explicitly **disclaims threading as an advantage** — FastJet is thread-safe too and
scales about as well; what flashjet's OpenMP buys is convenience + a provably
thread-count-independent result.

## Relation to our work

Branches from `0c4314c` — **before** Alex's `29c9da8` and before our substructure
commit `2e912ef`. Orthogonal axis to the ML4Jets story: that deck is GPU throughput
in the *jet* regime (39–99×) plus the event-regime starvation argument
([[2026-09-12-event-regime-sweep-run]]); this is single-core **CPU** parity-plus.
Useful complement — flashjet isn't only competitive when you have a GPU.

## Test merge result — CLEAN

Worktree `/tmp/fj-merge-test`, branch `merge-cpu-backend-test`, merge commit `6b1f857`.
`benchmarking` left untouched at `2e912ef`, clean tree.

Three conflicts, all resolved as unions:
- **`api.py`** — kept our `decode=`/`validate=` params and the **N ≤ 16 fused
  crossover**; added their `cpu` branch + auto routing. The auto-selection block
  itself auto-merged correctly (our `N<=16` first, their `cpu` slotted below).
- **`CLAUDE.md`** — kept ours (the validation-ladder docs are a strict superset);
  grafted in their two CPU commands.
- **`.gitignore`** — union (`.ab_fixtures/` + `*.so`).

**Full suite: 154 passed, 13 skipped** (was 85/13 on `benchmarking` alone; 13 skips
are the CUDA-only tests on a login node). C++ kernel built with
`HAS_NATIVE=True HAS_OPENMP=True`.

### Substructure survives the new CPU routing

The real risk was that `cluster()` on a CPU tensor now goes to the C++ kernel, and
F1/F2/F3 read the merge history. Checked CPU vs torch backend on identical input:

- **Exact match:** `jet_idx`, `n_jets`, `hist_child`, `hist_d`, F1 `exclusive_jets`,
  F3 `lund_coordinates`, `splitting_scales`, and **all six** F2 `groomed_jets` fields
  (`groomed_p4`, `z`, `dR`, `mu_split`, `n_drop`, `tagged`).
- **`hist_p1`/`hist_p2` differ in 28 of 480 entries — every one exactly a `p1`↔`p2`
  swap**: same pair, same `hist_child`, bitwise-identical `hist_d`.

### That swap is NOT a CPU-backend bug (corrected 2026-09-14)

First read said "unpinned contract, worth a PR comment". **Wrong — checked, and the
CPU backend is not the odd one out.** Comparing all four implementations on one event:

| | reference | nn_reference | cpu (C++) | torch |
|---|---|---|---|---|
| **reference** (brute force) | 0 | 24 | 24 | 19 |
| **nn_reference** (NumPy) | 24 | **0** | **0** | 5 |
| **cpu (C++)** | 24 | **0** | 0 | 5 |
| **torch** | 19 | 5 | 5 | 0 |

(`hist_p1` disagreements out of 60 steps.)

- **cpu(C++) vs nn_reference: 0** — the C++ kernel reproduces its stated validation
  target exactly, which is what `test_cpu_vs_reference.py` pins.
- **All four agree bitwise on `hist_child` and `hist_d`** — the merge *sequence* is
  universally agreed; only the labelling of which parent is "first" varies.
- **The divergence predates the PR.** Run on `benchmarking` with no PR code loaded:
  reference vs nn_reference differ in **24/60**, reference vs torch in **19/60**,
  nn_reference vs torch in **5/60**. Three orderings already coexist on our branch.

**Mechanism:** for a mutual-NN pair (a,b), `cand[a] == cand[b]` bitwise (both equal
`min(w_a,w_b)·dR²/R²`). Whichever slot wins that tie becomes `p1` and survives; the
other becomes `p2` and dies. The O(N²) geometric-NN family and the O(N³) brute force
simply reach that tie from different directions. In event 0 there were exactly **28
mutual-NN exact ties — matching the 28 swapped entries**.

So `p1`/`p2` **order is not a defined contract in flashjet**, and never has been. The
`CLAUDE.md` "Cross-backend contracts" section lists `hist_p1/p2` among tensors
"compared exactly", which overstates what the tests actually enforce — they pin
`hist_child`, `hist_d` and the resulting partition, all of which hold. **Nothing to
fix in the PR.** If anything is worth doing it is a docs correction on our side:
say that parent *order* within a merge is unspecified, and that consumers must treat
`{p1,p2}` as an unordered pair. Our F1/F2/F3 already do — they were verified to match
torch exactly through the CPU routing.

## Env trap hit (and repaired)

`pip install -e '.[torch,test]'` in `b_hive` pulled **awkward 1.10.3 → 2.13.0**,
breaking **coffea 0.7.22** (which the HToWW pipeline needs). The `test` extra wants
`fastjet` 3.5.1.3, which requires awkward>=2 — a genuine standing conflict with
coffea 0.7 in that env. Repaired with
`pip install "awkward==1.10.3" "awkward-cpp==53"`, then
`pip install -e . --no-deps` from the real repo to point the editable install back
(it had been redirected at the scratch worktree). Verified: awkward 1.10.3,
coffea 0.7.22, `coffea.nanoevents` imports, flashjet resolves to
`/eos/home-c/cgupta/flashjet/FlastJetDemo`.

**Next time: build the CPU backend in a throwaway env, not `b_hive`.**

## The Cacciari–Salam lemma question

Yes — this is exactly what flashjet does, and it predates the PR. Documented by name
in `nn_reference.py:10` and `triton_large.py:8`, with one addition worth knowing:
neighbours are maintained in the **geometric** metric ΔR², not in d_ij. The docstring's
own reasoning for why that matters — maintaining NNs in d_ij "is also correct but
cascades: every soft particle points at the hard core, so each core merge forces O(N)
rescans." Geometric NNs only go stale when a slot's *position* changes or dies, so a
merge that changes only momenta invalidates nothing → O(1) stale per step → O(N²).
`triton_large.py:301` adds a further shortcut: skip the rescan of a stale row when the
new pseudojet is strictly closer. The PR's C++ kernel inherits the same lemma and adds
FastJet's tile-bound pruning on top.
