---
tags: [reference, presentation, decision]
status: active
date: 2026-11-12
source: laptop
---

# Framework framing for tomorrow's presentation

## Latest agreed framing: problems and solutions

Chirayu clarified: **“I just want to say that these are the problems we found and this is how the fixes we made(showing actuallly what the legacy lite would do)”**. After the problem/solution outline below, he confirmed: **“Yeah this seems like a better way to present, record that”**.

This is the current presentation decision. It supersedes the earlier two-slide TRAIN/RUN-versus-next-mode framing below. Do not lead with four mode names or a legacy-lite label. Explain the concrete problems, show the optimized data flow, and state the implementation boundary once.

Suggested title: **Framework optimization: removing redundant storage and processing**.

| Problem found | Solution to explain |
|---|---|
| Weight-variation columns repeated in shifted event tables | Keep weight variations in nominal; shifted tables carry only what their evaluation needs. |
| Unnecessary columns and precision inflate storage | Use a compact column set and suitable precision, preserving event identifiers. |
| Retraining or rebinning of histogram-only outputs can require rereading NanoAOD | Preserve compact event inputs for offline scoring and template building. |
| Missing inputs or stale outputs can contaminate results | Check file coverage, provenance and model compatibility. |

Show the intended flow: **One NanoAOD pass → compact nominal + shifted inputs → offline training / scoring / rebinning → templates → Combine**.

Suggested spoken wording: **“We identified redundant storage and inflexible processing steps. The optimized design removes that duplication while preserving the information needed for offline iteration. The writers and validation infrastructure are implemented; integrating them into this single-pass chain is the remaining step.”**

The solution column describes the intended combined design, not a claim that the integrated mode is complete. Preserve the measured-storage-versus-unmeasured-runtime distinction below. This changes presentation framing only; no new implementation or processing submission is requested.

## Earlier framing, retained as decision history

Chirayu's exact wording: **“Okay, then what we do is, we show the TRAIN / RUN setup tomorrow, and say we are combining both modes to run in 1 pass... The opmised framework”**.

This updates the framework section of [[2026-11-12-november-update-slide-plan]]: show the implemented TRAIN/RUN setup first, then the planned combined one-pass processing framework. It replaces presenting legacy-lite/legacy-slim as already implemented. This is a presentation decision, not an instruction to implement or submit a new processing mode tonight.

Suggested slide wording: **“TRAIN/RUN provides compact training inputs, systematic templates and provenance checks. Next, we are combining their output paths into one NanoAOD processing pass, storing compact nominal and shifted event information for offline training, scoring and template building.”**

Keep the distinction explicit: a one-pass producer cannot fill the final newly trained MVA templates before that model exists. It saves the required event inputs, then scoring/template building happen offline. Reuse the current writers, fold-aware scoring and guards; the integrated one-pass mode and its validation remain planned, not established complete.

Quote measured storage reductions only with their tested comparison: the historical legacy tt partition2858MB versus TRAIN18.9MB is about150×, not a measured runtime speedup or a measured size for the proposed combined mode. Do not claim a production-wide speedup without a timed equivalent-output comparison. Keeper owns the actual deck; no deck/README/Meta edited here.
