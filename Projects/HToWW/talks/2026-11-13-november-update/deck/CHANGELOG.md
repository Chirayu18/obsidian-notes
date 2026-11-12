---
tags: [slides]
status: active
date: 2026-11-12
source: laptop
---

# November analysis update deck

## r1 — 2026-11-12

Chirayu asked the keeper directly to make the slides he had requested from the HToWW discussion agent ("Stop, I need to ask the keeper to make the slides actually"; then to the keeper: "can you just make the slides which I asked the HtoWW agent for?"). Built from [[Projects/HToWW/talks/2026-11-12-november-update-slide-plan]] and its requests: "implement hdamp also", "add a detailed breakdown of each systematic and its implementation, with plots and results of checks where nessary", "also an explaination for each systematic on what it is etc in the slides".

28 slides: 16 main (status, definitions, analysis recap, arms A/B, samples and 125.09 normalisation, prompt-lepton ONNX, speed-ups, event MVA strategy and duplication fix, negrw v2 with two plots, systematics overview, hDamp, results slot, open questions) and 12 backup (8 systematic-group slides with what/why, prescription/scope, evidence/status for every source; negrw SR plots; c-tag categories; production bookkeeping).

Evidence boundary: only the corrected negrw v2 report has fresh plots (4 PNGs copied to `assets/` with provenance JSON; regenerable, gitignored). No RUN templates, systematic Up/Down plots, impacts or limits exist yet, so those are explicit "pending" slots. Status snapshot is 12 Nov ~16:45 CET and must be refreshed before the talk. hDamp: samples configured in all eras, no template or card; Chirayu deferred its implementation until after the MVA training ("do it later, not now"). The "since September 8" baseline deck is not in the vault, so nothing is labelled as new since that date. All analysis claims are agent-reported.

Checks for r1: 28 slides / PDF pages; headless Chromium reports zero overflow, script errors, failed or external requests; dense slides inspected visually. Scripts-disabled Chromium shows all 28 sections, no horizontal overflow, no broken images; not opened in Obsidian itself. Built by `build.py`.
