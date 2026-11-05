---
name: s5-design-lessons
description: Design rules for agent s5+ learned from the s3-vs-s4 hold-out post-mortem (depth beats breadth)
metadata:
  node_type: memory
  type: project
  originSessionId: aa8f9519-67c8-4d6a-9ebd-3e82966c6ba2
  modified: 2026-10-02T08:35:47.497Z
---

Lessons from s3 (7/25) vs s4 (6/25) hold-out post-mortem, 2026-10-02 (details in ~/agenthon_hacathon/STATUS.md):

1. Depth beats breadth: build s5 on s3's core loop (generate → run → in-context output review vs spec → repair). Never stop iterating just because a run is "clean".
2. Draft B + judge: only as a fallback when the main script keeps crashing; never spend requests on it after a clean run. (Judge itself was right 3/4 when scored — not the problem.)
3. Keep s4's zero-request parts: spec ledger checks, revert-on-regression, JSON type / rounding / unused-param hints.
4. Truncation: never give up while requests remain (s4 get_script max_calls=4 bug cost fama-french); keep "no long comments/docstrings" in the cut-off message; model naturally continues after a cut-off (stitching possible — user previously declined it, ask before adding).
5. No rigid phase time-boxes; budget by requests + overall deadline. Provider speed varies (s4 ran 27% slower when sharing provider with s3b) — don't run A/B variants concurrently if comparing.
6. Fresh-context final review rubber-stamps (15-item cap, bare verdicts); prefer in-context review.
7. Crash loops: show actual qflib signature/return type on tracebacks; remember reverted fixes so trimming doesn't cause oscillation.
8. Add consistency checks (MC vs analytic, error ≈ value) to the scanner.

**Why:** s4's "better on paper" design lost because it spread effort over two shallow drafts under 25 req / 4k tok limits.
**How to apply:** any new stage (s5, s6 modular) should follow these; see [[Meta/claude-memory/_history/projects/Agenthon/agenthon/agenthon-track1-project|agenthon-track1-project]].
