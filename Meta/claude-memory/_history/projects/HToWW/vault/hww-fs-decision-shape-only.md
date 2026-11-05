---
name: hww-fs-decision-shape-only
description: FINAL (2026-09-30) H+c FS treatment — 4FS FxFx nominal unchanged, FS uncertainty = 3FS/4FS shape systematic only, no NNLO/normalisation; slides must carry the caveat
metadata:
  type: feedback
---

The H+c flavour-scheme uncertainty covers ONLY the 3FS vs 4FS scheme difference (as in Run 2, AN-23-102 §7.1).
Nominal stays 4FS FxFx with its NLO cross section; no stitching, no NNLO normalisation, no NLO-vs-NNLO lnN.
The 30% `xsec_hplusc_4FS_5FS` lnN is replaced by a shape systematic in leading GEN c-hadron pT, derived with both
schemes at the same inclusive cross section.

**Why:** the user rejects normalising an NLO sample to NNLO (different selection efficiency), and considers the FS
uncertainty's sole job to be the scheme difference. I argued repeatedly for stitching / NNLO / a normalisation lnN and
the user found this frustrating ("Why don't you get it").

**How to apply:** don't re-propose stitching, NNLO normalisation or a normalisation lnN. Every slide / AN paragraph on
this must state the caveat that NLO-vs-NNLO normalisation (~25% lower in LHCHWG-2026-007 Table 3) is NOT covered.
Framework/parquets still need an explicit go. See [[Meta/claude-memory/_history/projects/HToWW/vault/hww-fs-stitching-reweight|hww-fs-stitching-reweight]], [[Meta/claude-memory/_history/slides/vault/hww-fs-private-results-not-for-ppt|hww-fs-private-results-not-for-ppt]].
