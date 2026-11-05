---
name: agenthon-track1-project
description: "Agenthon 2026 Track 1 coding-agent project — layout, variants, results, decisions, next steps (state as of 2026-10-01 ~13:30)"
metadata:
  node_type: memory
  type: project
  originSessionId: aa8f9519-67c8-4d6a-9ebd-3e82966c6ba2
  modified: 2026-10-01T11:10:06.319Z
---

Building a Docker "solve" agent for Agenthon 2026 Track 1 (QFBench quant-finance coding tasks), started 2026-10-01. Development closes 2026-10-12 AoE; Final (hidden units) 2026-10-13..25. Rules 8/9 (from 2026-10-05): no stored answers for the unit being solved; pass must come from run-time House-model use. Full project status: ~/agenthon_hacathon/STATUS.md (read it first after a compaction).

Constraints: House model nvidia/nemotron-3-super-120b-a12b (FP8 snapshot rl-030326-fp8); 25 requests/unit, 4000 output tokens/request (reasoning counts); ~8 min/unit avg over a 12h roster. No embedding models in image (in-image weights banned; issue #26 unanswered).

Dev model access: NVIDIA (preferred by user) key ~/.nvidia_api_key, `source harness/env_nvidia.sh`; OpenRouter fallback key ~/.openrouter_api_key ($10 limit), `harness/env_openrouter.sh` (DeepInfra bf16 → DekaLLM fp8). OpenRouter ignores chat_template_kwargs; agent maps thinking to reasoning on/off there.

Hold-out (frozen, user-approved): ~/agenthon_hacathon/holdout.txt, 25 units — never open their instruction/checks/reference. All decisions are measured on it.

User preferences: wants >90% (told realistic target is beating ~0.25-0.36 legitimately); chose qflib-only (no QuantLib/hybrid); prefers NVIDIA endpoint; 8 parallel jobs; terse status updates. See [[Meta/claude-memory/_history/projects/Agenthon/agenthon/never-disrupt-running-jobs|never-disrupt-running-jobs]].

Hold-out inspection policy (user-approved 2026-10-02): reading hold-out transcripts for diagnosis is OK, but only general failure patterns may become fixes, never task-specific rules; log inspected units in ~/agenthon_hacathon/holdout_inspected.txt.

- 2026-10-05 platform: s3 = 0.3488 (30/86, rank 9, shown as "Chirayu"); Arsen Ibragimov 0.3837 (33/86, rank 7). s11 built (qfb-t1:s11), push pending by user via submission/push_and_pack_s11.sh.
- 2026-10-05: dev runs default to harness/env_nvidia.sh (NIM 88 tok/s vs OpenRouter-DeepInfra 48, DekaLLM 16); keep NIM to -j3/-j4 (free-tier ~40 rpm). env_openrouter is DeepInfra-only.
- 2026-10-06: s12 = 32/86 public, 57/86 extra; Arsen v2.20 black-box = 32/86 public, 34/86 extra (his board lead = public-unit tuning + our stale s3 entry). agent_s13 (s12 + invariants/contract fixes/convention rules/gated review/snapshots) being tested; next = build qfb-t1:s13 image for user to push. Read the "STATE AT COMPACTION" block at the end of STATUS.md.
- 2026-10-07: platform s11 = 0.3837 (33/86) vs Arsen 0.4535 (39/86). s13 pushed (ghcr qr-691272f3@sha256:f2aed483...) and uploaded by user 2026-10-06; score pending. Kaggle base rate: public #5-10 wins ~1% (412 comps), but our private set = different units + rerun noise.
- 2026-10-07: s13 submitted; old-agent full-86 queue running (s3 29, s6 30, s7 30, s3a 31, s4 21, s10.. ETA 17:00 UTC); Team 229 = ghcr warren618 (watched, cron 6bad99f8). See 'STATE AT COMPACTION (2026-10-07)' in STATUS.md.
