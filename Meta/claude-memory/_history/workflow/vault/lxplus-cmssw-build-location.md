---
name: lxplus-cmssw-build-location
description: "AFS home is too full for a CMSSW build; build on EOS — setup is ~2 min because cms-init is sparse, NOT the multi-hour job the per-file I/O cost suggests"
metadata: 
  node_type: memory
  type: project
  originSessionId: 91388281-cecf-4de2-8f19-6b5975a2a1c0
  modified: 2026-09-21T18:22:42.887Z
---

Where a fresh CMSSW build can go on lxplus, measured 2026-09-21.

**AFS home is effectively full.** `fs lq ~` reported 9717435 / 10485760 KB = 93%, self-flagged `<<WARNING`, ~730 MB free. `git cms-init` pulls the full CMSSW history (~2-3 GB) *before* compiling anything, so a fresh build area does not fit. There is **no** `/afs/cern.ch/work/c/cgupta` volume provisioned.

**EOS works — my earlier "EOS lacks the POSIX semantics scram needs" was an untested assumption and is wrong.** Tested under `/eos/user/c/cgupta`: symlinks, hardlinks, chmod, mkfifo all succeed. Nothing blocks git or scram.

**But EOS is ~640x slower on the small-file pattern git/scram use.** Measured, 200 sequential small-file writes:

| Location | Time | Per file |
|---|---|---|
| `/eos/user/c/cgupta` | 6.40 s | ~32 ms |
| `/tmp` (node-local) | 0.01 s | ~0.05 ms |

**The "~33 min checkout / multi-hour build" prediction was WRONG — measured end-to-end 2026-09-21.** It assumed `git cms-init` materializes all 62,604 files. It does not: the checkout is **sparse**, the index tracks 62,604 files but only the packages you `git cms-addpkg` are written to disk. Actual timings on EOS, 10 packages:

| Stage | Time |
|---|---|
| `scram project` | 95 s |
| `git cms-init` | 6 s |
| fetch + 10× `addpkg` + checkout | ~30 s |
| `scram b -j 8` to first error | ~80 s |

Setup was **~2 minutes, not 33**. Still run it under tmux (see [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]]) because a dropped ssh kills the job, but don't budget hours for a package-scoped build or tell anyone it will take them.

`/tmp` has ~72 GB free and is 640x faster, but is node-local and wiped, and lxplus round-robins login nodes — only viable pinned to one node and treated as disposable.

Build area created for the Phase-2 study: `/eos/user/c/cgupta/phase2build`.

**Why:** the instinct is to build in AFS home; it no longer fits. EOS is the right fallback and is *fast enough* — the trap is the reverse of what I first assumed, i.e. talking people out of EOS (or budgeting hours) on the strength of a per-file I/O number that never gets multiplied by the whole tree.

**How to apply:** before proposing a CMSSW build location, run `fs lq ~` first. If AFS is tight, use EOS and quote ~2 min of setup for a package-scoped build. Verified 2026-09-21 in `/eos/user/c/cgupta/phase2build`: 440 files on disk vs 62,677 in the git index. Freeing AFS space means deleting Chirayu's files: ask, never do it unprompted.

**General lesson, the reason this memory is worth keeping:** a correct micro-benchmark (~32 ms/file, reproduced independently) became a wrong prediction by being multiplied by an unverified quantity. Measure the *end-to-end* thing before forecasting it, and don't let a real measurement lend false authority to the estimate built on top of it.
