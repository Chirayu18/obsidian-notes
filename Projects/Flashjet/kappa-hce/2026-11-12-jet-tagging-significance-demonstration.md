---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# A jet-tagging demonstration of the HToWW significance advantage

Chirayu's objective: “I want to demonstrate the same betterness in jet tagging tho”. This authorizes preparing a jet-tagging study, not assuming a positive result. No new job submission is authorized by this note. This is a proposed protocol; no new experiment has run, and the sample/yield manifest below must be resolved before it becomes a frozen preregistration.

## What should transfer

The recovered HToWW comparison favours the **13-class κ-HCE configuration over a six-class CE configuration** on historical signed event-yield-weighted significance. It does not isolate the loss. Source: [[Projects/HToWW/selection-and-mva/2026-11-10-kappa-hce-weighted-significance-recovery]].

For jet tagging, test both claims separately:

1. **Configuration benefit:** a fine-grained κ-HCE tagger improves an analysis significance relative to a conventional coarse CE classifier.
2. **Loss benefit:** κ-HCE improves the same significance relative to a CE tagger with the identical fine-grained outputs, architecture and inputs.

A positive first comparison alone supports the complete configuration. A positive second comparison is needed to credit κ-HCE specifically. Existing negative JetClass results remain part of the evidence; they are not superseded by this proposed study.

## Focused use case and four arms

Target Hcc tagging in a search with Hbb and QCD as explicit background components. Other available JetClass labels remain separate in the fine classifier and merge into a common “other” output in the coarse classifier. The signal definition and evaluated background set must be the same for every arm. The background mixture must come from an independent target-analysis yield manifest, not from which mixture makes κ-HCE win.

| Arm | Outputs | Purpose |
|---|---|---|
| Coarse CE | Hcc / Hbb / QCD / other | Conventional task-specific reference |
| Fine CE | Existing ten JetClass classes | Strong baseline; separates class decomposition from loss |
| Fine class-weighted CE | Same ten classes | Tests whether simple weighting explains an advantage |
| Fine κ-HCE v2, natural-prior arm | Same ten classes | Best-supported existing κ candidate; `beta=0, k_fine=1, lam=1` |

Use the same backbone, feature processing, source events, train/validation/test partition, paired initialization where the shapes agree, batch order, training budget and three seed IDs for all arms. Only the output dimension differs in the coarse arm; record that difference. CE receives comparable validation tuning and any discriminant optimization used for κ-HCE. Keep training class weights distinct from analysis evaluation weights.

This is a minimum four-arm comparison, not a claim that the existing v2 candidate will win. The natural-prior v2 arm was near CE in the rescue test; the tempered arm was worse. Do not silently try numerous loss modifications until one passes. A modified loss would require a separately specified mechanism and study record.

## Metric and selection

For each arm define Z(t)=S(t)/sqrt(B(t)), where S and B are sums of the target-analysis event weights passing its score threshold. Preserve signed weights; record sumw, sumabsw and sumw² per signal/background component. A nonpositive B has no valid Z and must not be turned into an apparent gain. Do not clip negative weights or use inverse-frequency class weights as physics weights.

Primary comparison: the ratio Z(κ-HCE)/Z(fine CE) at a **validation-selected operating point**, transferred unchanged to test. Restrict validation selection to a prespecified useful signal-efficiency range (proposed count-based 30–70%) and adequate MC precision. Select checkpoints by this task metric for every arm, not AUC for one arm and significance for another. Any score calibration, background-mixture correction or κ optimization uses validation only, with equal freedom/budget for CE. Report achieved count and signed-weight efficiencies separately; signed weights do not automatically define a monotonic efficiency quantile.

Proposed precision guard: positive S and B, and sqrt(sumw²)/abs(sumw) no greater than 20% for both at eligible validation thresholds. Freeze the threshold grid and guards before reading new results. This is an analyst-selected diagnostic criterion, not an established CMS prescription.

Secondary comparisons: ratio to coarse CE and class-weighted CE; Z at frozen validation thresholds targeting 30%, 50%, 70% count efficiency; background efficiency and composition; Hcc/Hbb separation; score calibration and non-target-class trade-offs. AUC remains diagnostic.

Proposed success requirement: at least +5% mean test Z relative to **both** fine CE baselines, positive paired differences in all three seeds, and a prespecified paired uncertainty analysis whose 95% interval excludes zero gain. Report event-resampling and seed variability separately; resampling three seeds is not strong evidence about arbitrary retraining. The +5% floor is a proposed practical target, not a result or a power calculation. Assess whether available effective MC counts can resolve it before authorizing the full study. A gain only against coarse CE is labelled a configuration benefit.

## First step: a bounded diagnosis before further training

Use existing saved validation checkpoints/predictions to determine whether the current κ candidate offers a different **background-rejection pattern** that could help the independently chosen analysis mixture. Audit what validation logits and event identities are available before scheduling new inference. Fit/select on validation only. Existing repeatedly inspected JetClass test predictions can supply an explicitly exploratory diagnostic, never the confirmatory endpoint or a reason to choose a winning mixture.

The already measured rescue comparison is insufficient for a new positive claim: [[Projects/Flashjet/kappa-hce/2026-11-02-kappa-hce-rescue]] selected by validation AUC at the training mixture and produced an exact NOT RESCUED verdict. Changing the metric now does not change that verdict. A metric-aligned follow-up needs its own record and an untouched evaluation partition.

For a JetClass-only diagnostic, declared class-mixture weights are **synthetic target weights**, not a CMS sensitivity projection. A CMS claim requires a selected CMS sample, per-event normalization/selection weights and a documented tagger-to-analysis mapping. Do not derive those weights from HToWW event counts or tune them on the test result. JetClass process labels and an event-analysis background yield are not interchangeable.

## Inputs still needed before freezing or executing

- Identify the target analysis/sample and its Hcc, Hbb, QCD and other background yields after the same preselection; preserve source files and normalization provenance.
- Identify a fresh evaluation partition with stable sample/event IDs disjoint from training and all development. Audit existing data manifests; a new random slice of already inspected events does not create independent confirmation.
- Inventory reusable validation artifacts, then make the exact inference/training resource request and commands reviewable. New submission requires Chirayu's explicit OK under the standing vault rule: “No push … job submission … without Chirayu's explicit OK.”

## Deliverable and interpretation

Produce one comparison plot with event-weighted Z versus achieved signal efficiency and a κ/CE ratio, plus a table of S, B, sumw², background composition, seeds and frozen selection settings. Save configuration/manifests, code revision and metrics together. Report a null or negative outcome unchanged.

If the loss comparison succeeds, motivate an optional b-hive training loss for this specific rare-signal tagging task; CMSSW runs the exported inference model. If only the configuration comparison succeeds, describe that narrower result. Internal CMS inputs/results require the established publication approval before inclusion in a public PR. No universal claim that κ-HCE beats CE follows from either one task or the HToWW historical curve.
