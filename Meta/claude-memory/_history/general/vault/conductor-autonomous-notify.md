---
name: conductor-autonomous-notify
description: Conductor works autonomously and notifies the user only when they are needed; user wants this permanent in the harness
metadata:
  node_type: memory
  type: feedback
  originSessionId: f4831488-5e23-4cfa-81f9-c3f0096db6eb
  modified: 2026-11-03T06:29:56.653Z
---

As conductor, keep working without the user: watch agent turns (poll the conductor state dir for new `.exit` files, since inotifywait is not installed), collect replies, cross-check, chain follow-ups. Notify (PushNotification / harness notify) ONLY when the user is needed: approval, a decision, a blocking question, a failure, or work ready for their test/sign-off. No routine "done" pings.

**Why:** user said on 2026-11-03 "keep working independently of me ... send me a notification if anything from me is needed" and "keep this change for future conductors as well in the harness".

**How to apply:** default behaviour of every conductor session; the rule is also written into ~/ai-orchestrator/conductor.md (the conductor role prompt) so new conductors inherit it. See [[Meta/claude-memory/_history/general/vault/omp-harness-decision|omp-harness-decision]].
