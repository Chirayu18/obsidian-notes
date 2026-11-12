---
tags: [reference, presentation, decision]
status: active
date: 2026-11-12
source: laptop
---

# Framework framing for tomorrow's presentation

Chirayu's exact wording: **“Okay, then what we do is, we show the TRAIN / RUN setup tomorrow, and say we are combining both modes to run in 1 pass... The opmised framework”**.

This updates the framework section of [[2026-11-12-november-update-slide-plan]]: show the implemented TRAIN/RUN setup first, then the planned combined one-pass processing framework. It replaces presenting legacy-lite/legacy-slim as already implemented. This is a presentation decision, not an instruction to implement or submit a new processing mode tonight.

Suggested slide wording: **“TRAIN/RUN provides compact training inputs, systematic templates and provenance checks. Next, we are combining their output paths into one NanoAOD processing pass, storing compact nominal and shifted event information for offline training, scoring and template building.”**

Keep the distinction explicit: a one-pass producer cannot fill the final newly trained MVA templates before that model exists. It saves the required event inputs, then scoring/template building happen offline. Reuse the current writers, fold-aware scoring and guards; the integrated one-pass mode and its validation remain planned, not established complete.

Quote measured storage reductions only with their tested comparison: the historical legacy tt partition2858MB versus TRAIN18.9MB is about150×, not a measured runtime speedup or a measured size for the proposed combined mode. Do not claim a production-wide speedup without a timed equivalent-output comparison. Keeper owns the actual deck; no deck/README/Meta edited here.
