---
name: hww-dy-nanov12-invalid
description: All 10 central DY NanoAODv12 datasets in the HToWW era yamls are INVALID in DBS (checked 2026-10-29); must be replaced before the full rerun
metadata:
  node_type: memory
  type: project
  originSessionId: a5acb22c-f02e-4ffe-83d8-d6c106008ce6
  modified: 2026-11-03T06:16:38.076Z
---

MEASURED 2026-10-29 with dasgoclient `status=*`: every `DYto2L-*` query in
`analysis/filesets/{2022preEE,2022postEE,2023preBPix,2023postBPix}_nanov12.yaml`
(2Jets MLL-50 and 10to50, 4Jets MLL-50) is INVALID. The chains were remade from
DIGI-RECO in late 2025, so files disappear from disk; jobs die in preprocessing with
`[3011] No servers are available`. Found via Saranya's HcZZ branch (her README "Known
traps"); her replacement map lives in her second-brain, not in the repo.

**Resolved in DAS 2026-11-03:** each sample has a VALID v12 re-processing in the same campaign (only the `-vN` changes). The exception is 2023 4Jets_MLL-50: its JMENano12p5 copies are all INVALID, so it moves to the standard 130X processing. The mapping table is in vault `Projects/HToWW/2026-11-03-dy-replacements.md`. The yamls are NOT edited yet.

**Why:** blocks the post-fix full rerun ([[Meta/claude-memory/_history/projects/HToWW/vault/hww-jer-split-tag-noop|hww-jer-split-tag-noop]]); a plain resubmit
fails the same way and the jobs_status blacklist cannot help ([[Meta/claude-memory/_history/projects/HToWW/vault/hww-jobs-status-blacklist-memoryless|hww-jobs-status-blacklist-memoryless]]).
**How to apply:** find the VALID replacement datasets in DAS before submitting any MC.
Loop dasgoclient queries one at a time with `</dev/null` and a long timeout; parallel or
-json loops returned empty strings (looked like "valid") on 2026-10-29.
