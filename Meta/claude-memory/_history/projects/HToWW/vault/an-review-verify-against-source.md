---
name: an-review-verify-against-source
description: When reviewing the HToWW AN, verify card/config claims against the actual card and code on lxplus, never against the AN prose
metadata:
  type: feedback
---

When reviewing an analysis note, any claim about what a datacard, config, or training
script *contains* must be checked against that file, not against the note's prose.

**Why:** In the 2026-08-21 review of the HToWW AN blue sections, I asserted that t̄t was
excluded from `lhe_pdf` and `lhe_alphaS`. That came from Table 36's "all except t̄t"
text. The card itself (`v11_hplusc_2dcat.txt`, lines 44-45) has `1` in every column
including t̄t. The prose was wrong, and because I reviewed the prose my report handed the
author's own error back to them looking like independent confirmation. Two other items
(v32 epoch count, empty B categories) failed the same way. A review inherits every error
of the document it reviews unless it goes to source.

**How to apply:** For HToWW specifically —
- Cards: `/eos/home-c/cgupta/higgscharm/outputs/combine/*.txt`. Process order per channel
  block is `hplusc, higgsbkg, tt, st, diboson, vjets`, so column 3 of each six is t̄t.
  Check the date matches the quoted result before trusting a card.
- Workflows: `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/`.
  `hww_combine_2dcat.yaml` is the H→WW one; `hplusc.yaml` in the same dir is ZZ→4l and
  has *different* WP settings (loose vs medium) — easy to grab the wrong file.
- Training: `/eos/home-c/cgupta/HToWW/b-hive/` (scripts + `config/*.yml`).
- Use `ssh lxplus` with targeted `grep`/`sed`; sshfs traversal over `~/mnt/lxplus` times
  out on broad `find`.

Cite the file and line in the review so the author can check the check. See
[[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]] and [[Meta/claude-memory/_history/projects/HToWW/vault/hww-ctag2d-sf-total-decision|hww-ctag2d-sf-total-decision]].
