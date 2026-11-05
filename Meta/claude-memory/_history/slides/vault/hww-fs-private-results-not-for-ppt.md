---
name: hww-fs-private-results-not-for-ppt
description: H+c 3FS/4FS private-generation results (R=0.789 etc., fs_unc/ratio_full.json, fs_ratio_* plots) must NEVER go in slides, the AN or talks
metadata:
  type: feedback
---

The privately generated H->gg H+c 3FS/4FS results (Run 3, 400k per scheme: R(>=1c)=0.789,
R_incl=0.659, the fs_ratio_cjet1_pt / higgs_pt / stats plots, `fs_unc/ratio_full.json`,
`fs_unc/out/`) are **kept as an internal cross-check but must never appear in a ppt, deck,
AN section or talk.** User instruction, 2026-09-29.

**Why:** they came from a mistake — private generation when official NanoAOD existed on DAS
(see [[Meta/claude-memory/_history/general/vault/check-das-before-generating|check-das-before-generating]]). Only official-sample results are presentable.

**How to apply:** when building any deck/AN/summary on the flavour-scheme uncertainty, use only
`ratio_run3_official_GG.json`, `ratio_run2_{GG,WW}.json` and plots named `*_official*` / `cmp_*`.
Marked in the vault note `Projects/HToWW/fs-unc-2026-09-29/` and in
`/eos/user/c/cgupta/HToWW/fs_unc/README_PRIVATE_RESULTS_DO_NOT_PRESENT.txt`.
