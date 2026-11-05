---
tags: [reference, decision]
status: active
date: 2026-11-05
source: laptop
---
# Standing decision (Chirayu, 2026-11-05): reviewers trust existing test logs

During reviews of HToWW work, a reviewer **does not rerun unit tests that have already been run on the same code**. It cites the existing log as evidence instead (e.g. `diagnostics/unittest_routeb.log`, 20/20 OK for proposal HTOWW-ROUTEB-SOL-20261105).

- Rerun only if the code under test changed after the logged run (check file mtimes or SHA256SUMS against the log time), or if no log exists.
- In findings, mark the result "author-run test log, not re-executed by the reviewer". Do not call it independently verified.
- Origin: Chirayu stopped a reviewer that was rerunning the Route B tests, then said: "Trust the log... Keep it a standing decision during reviews, dont run same unit tests on the same code again".

Approved by Chirayu 2026-11-05. Folded in by the keeper (2026-11-05) into [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol|the HToWW review protocol]] and the `htoww-review` skill (`Projects/HToWW/framework/review/htoww-review/SKILL.md`).
