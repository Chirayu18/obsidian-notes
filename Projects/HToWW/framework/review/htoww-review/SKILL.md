---
name: htoww-review
description: Review HToWW or higgscharm analysis changes by tracing approved prescriptions through code, checks and saved outputs. Use for analysis correctness reviews, systematic audits and verification of fixes; not routine status summaries or CombineAgent nugget scoring.
---

# HToWW review

Apply the review protocol in [the vault review brief](../../2026-11-05-htoww-review-protocol.md). Resolve this skill directory's real path before following the relative link when it is installed through a symlink. The protocol contains the evidence table, HToWW-specific checks, finding requirements and downstream verification rules.

Use the existing analysis environment and the current task's authorization. This skill adds review criteria; it does not authorize edits, additional agents, submissions, unblinding or changes to physics prescriptions.

Start from current vault decisions and the actual repository revision/diff. Keep a bounded scope. Produce an evidence table connecting prescription, implementation, check, saved output and status. Distinguish a demonstrated software defect from missing physics input or a check that was not run. Require a reproducible example when feasible; do not label an unexecuted proposed test as passed.

When a fix is authorized, trace its downstream consumers, check closely related failure modes and verify each finding against the changed code and outputs. Record what was actually checked and what remains agent-reported or unresolved.

The protocol is adapted from the public JFC survey for the existing HToWW workflow. It supplies no automatic physics validator and makes no claim of improved bug-detection performance.
