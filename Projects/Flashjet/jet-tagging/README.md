---
tags: [index]
status: active
date: 2026-11-05
source: laptop
---

# jet-tagging

JetClass/ParT inputs, controlled ablations, generator robustness and PLuM reproduction.

Status: Organized by topic; original results and evidence remain in their source notes.
Latest dated record: [[Projects/Flashjet/jet-tagging/2026-09-24-nopair-arms-final|No-pair arms C / E / F: final 1M results. Nothing we tried replaces the pairwise bias.]].
Needs Chirayu: unresolved source-note tasks remain open; see [[Meta/reorg/vault-20261105-report|keeper report]].

Organization and links were checked by the keeper. This does not independently validate scientific claims in the source notes.

## Records

- [[Projects/Flashjet/jet-tagging/2026-07-18-history-tagger-design|Design: feeding merge histories (C/A + kT + anti-kT) into a b-hive tagger]]
- [[Projects/Flashjet/jet-tagging/2026-07-18-tagger-inputs|Merge-history variables as jet-tagger inputs (kT + C/A)]]
- [[Projects/Flashjet/jet-tagging/2026-08-28-bhive-jetclass-part-setup|b-hive + JetClass ParT training — setup, and the XRootD filename trap]]
- [[Projects/Flashjet/jet-tagging/2026-08-28-bhive-jetclass-runbook|Runbook: b-hive JetClass → ParT training on lxplus]]
- [[Projects/Flashjet/jet-tagging/2026-08-28-bhive-maintainer-message|Draft message to b-hive maintainers]]
- [[Projects/Flashjet/jet-tagging/2026-08-28-part-ca-features-implementation|Per-particle C/A features in b-hive (+ a note on the JetClass ParT 4-vector ordering)]]
- [[Projects/Flashjet/jet-tagging/2026-09-04-ca-1M-verdict-and-pairwise|C/A on JetClass: the 1M verdict, why it failed, and the pairwise redesign]]
- [[Projects/Flashjet/jet-tagging/2026-09-04-herwig-dataset-plan|Herwig generator-robustness test — build plan]]
- [[Projects/Flashjet/jet-tagging/2026-09-04-subjet-verdict|Subjet arm: pre-registered test FAILED — both arms are nulls]]
- [[Projects/Flashjet/jet-tagging/2026-09-06-logit-discriminant-bug|BUG: rejection numbers computed on raw logits — all earlier 1/eps_B values invalid]]
- [[Projects/Flashjet/jet-tagging/2026-09-07-herwig-robustness-result|Herwig generator-robustness result (980k, all three arms)]]
- [[Projects/Flashjet/jet-tagging/2026-09-07-plum-paper-vs-our-result|PLuM (arXiv:2605.26821) vs our C/A + subjet result]]
- [[Projects/Flashjet/jet-tagging/2026-09-07-plum-reproduction-plan|Can we get PLuM's gains? — reproduction plan]]
- [[Projects/Flashjet/jet-tagging/2026-09-08-future-directions|Where to go after PLuM — ideas worth trying, and why the obvious ones are not]]
- [[Projects/Flashjet/jet-tagging/2026-09-11-plum-final-verdict|PLuM final verdict: validation gain is real, test-set reproduction FAILS]]
- [[Projects/Flashjet/jet-tagging/2026-09-14-ml4jets-hong-4prong-lundnet|ML4Jets 2026 — Hong, ATLAS 4-prong LundNet tagger]]
- [[Projects/Flashjet/jet-tagging/2026-09-14-xai-interp-papers-and-our-null|Two interpretability papers that explain our PLuM null]]
- [[Projects/Flashjet/jet-tagging/2026-09-24-nopair-arms-final|No-pair arms C / E / F: final 1M results. Nothing we tried replaces the pairwise bias.]]

## Historical records

Dated snapshots and replaced handoffs are retained here; their old resume instructions are historical.

- [[Projects/Flashjet/jet-tagging/_history/2026-08-31-reproduce-ca-plus1.3-result|Reproducing the +1.31 C/A result (5 features, pre-soft-drop)]]
- [[Projects/Flashjet/jet-tagging/_history/2026-09-01-sd-run-and-convergence|Second training (survives_SD) — and why +1.31 does not survive a controlled rerun]]
- [[Projects/Flashjet/jet-tagging/_history/2026-09-04-arm-status-and-probes|Arm status + probe results, 2026-09-04 16:00]]
- [[Projects/Flashjet/jet-tagging/_history/2026-09-08-plum-arm-launched|PLuM arm launched (4th arm) — condor 9283169]]
