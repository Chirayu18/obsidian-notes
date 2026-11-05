---
name: agenthon-track3-project
description: "Agenthon 2026 Track 3 (simulation, events/sec) — this session builds it; layout, design decision, rival intel sources"
metadata:
  node_type: memory
  type: project
  originSessionId: 3477df76-3114-48d5-83ee-4179ecf775e1
  modified: 2026-10-10T14:39:49.485Z
---

Started 2026-10-10. Track 3 = exact-replay LOB simulator (ABIDES fork); rank = events/sec, host-measured over the WHOLE container run (startup counts); Tier A needs exact fill sequence + message ledger. Dev closes 2026-10-12 AoE.

Layout ~/agenthon_hacathon/track3/: kit/ (public repo + LFS via ~/.local/bin/git-lfs), abides/ (pinned f9cbe513 + 4 patches), .venv311 (reference stack; reproduces refs byte-exact), tools/, runs/, spec/src (stripped ABIDES sources).

Design (user asked: take best rival ideas): native static C++ binary, numpy-RandomState-exact RNG, own parquet writer, ABIDES python fallback for unsupported scenarios. Rival warren618 t3 image does exactly this (t3native + snappy, strict FP). Scorer checks trace_sha256 only against OUR file, not the reference.

Rival intel came from peer sessions "Track 2 submission build" and "track1-coding-public" (track2/RIVALS.md, survey/images/*t3*). Related: [[Meta/claude-memory/_history/projects/Agenthon/agenthon/agenthon-track1-project|agenthon-track1-project]], [[Meta/claude-memory/_history/projects/Agenthon/agenthon/never-disrupt-running-jobs|never-disrupt-running-jobs]].

- 2026-10-12: t3sim v1 done and verified: 95/95 reference traces+ledgers exact, 71/71 admissible (kit developer verifier, also end-to-end via docker), fuzz 188/188 comparable scenarios exact vs local ABIDES. Image t3sim:v1 (python:3.11-slim + static t3sim + ABIDES fork as crash fallback). Container-timed geomean ~223k ev/s vs ref 13.8k. Push+pack is the USER's step: track3/submission/push_and_pack_t3.sh (tags ghcr blipblipblopa/qr-691272f3:t3sim-v1; auto-mode classifier blocks Claude from pushing). Next: Final submission (Oct 13-25); perf ideas: SHA-NI, smaller heap entries, faster ledger encode.
- 2026-10-27: Final deadline EXTENDED to 27 Oct 23:59 AoE (28 Oct 11:59 UTC). Ranking = ARITHMETIC mean over units of events / container window (State.StartedAt->FinishedAt, median of repeats); ~100 ms container floor; big units dominate; close top-6 re-timed (median of 3). t3sim v2 (src = t3sim/src; v1 kept in t3sim/src_v1): parallel column encode, O(n) fill classification, perm-gather trace, moved ledger cols, reserves, SHA-NI, flat order store, -O3 v2. Byte-identical to v1 on all 71 units; projected score +10.7% (563k -> 624k ev/s); mega 504 -> 367 ms. Image t3sim:v2; Final descriptor track3/submission/submission-final.json (agenthon2026-simulation-final, phase final, models []); script push_and_pack_t3_final.sh (tag t3sim-v2).
