---
tags: [slides]
status: active
date: 2026-11-12
source: laptop
---

# November analysis update deck

## r2 — 2026-11-12

Complete presentation rebuild requested by Chirayu: “Decisions about the slides have been updated.... Update the slides... Make then GOOD like GOOD GOOD ... As good as the slides for the talk in Higgs2026 . And use that same template”; then “Revamp the slides completely, use elements from the CERN skill if needed.... Present it properly and it should look like substancial work done”.

Reused the actual Higgs2026 CSS, typography, teal/orange title and side rail, logo tile, takeaways and backup divider. 36 slides: 20 main + 16 backup. The narrative starts with August→October development and the explicitly pre-fix 691 result, immediately followed by the old-card Higgs-scale diagnostic, then the signal-weight/merging issues, rebuilt-gridpack evidence, A ratio/B stitching, lepton/SF work, negrw v2 and its limitations, systematics, measured storage/timing improvements, the agreed problems→solutions→one-pass framework design, held-out classifier checks, new TRAIN-to-card scorer and dated production state. No new A/B result is invented. hDamp remains deferred. Each systematic has a physical explanation, prescription and evidence boundary in backup. Companion speaker notes carry interpretation and caveats.

Updated decisions: [[Projects/HToWW/talks/2026-11-12-framework-presentation-decision]], [[Projects/HToWW/talks/2026-11-12-november-update-slide-plan]], [[Projects/HToWW/talks/2026-11-12-evening-results-and-restart-handoff]]. Later scorer evidence: [[Projects/HToWW/framework/2026-11-12-train-card-scorer-implemented]]. Production state is a saved 12 Nov 20:29 CET snapshot, not a live queue check. 691/703 are historical-card results, not corrected A/B limits.

Local checks: every slide rendered; contact sheets and full-resolution pages inspected against the Higgs2026 reference. Render helper checks body fit, header separation and broken figures. CERN deterministic PDF checks run in internal mode; density notices on detailed backup pages are reviewed as readability warnings, not independent physics validation. Scripts-disabled Chromium shows all36sections without broken images or horizontal overflow at1280px; actual Obsidian was not controlled. The PDF has36pages.172deck/hub source targets and slide anchors resolve. `review-checks.json` records the boundary. No external reviewer/model, new processing, training or Combine was run. PNGs/PDFs stay local. Vault-wide organization and lint cleanup remain deferred as requested.

## r1 — 2026-11-12

Chirayu asked the keeper directly to make the slides he had requested from the HToWW discussion agent ("Stop, I need to ask the keeper to make the slides actually"; then to the keeper: "can you just make the slides which I asked the HtoWW agent for?"). Built from [[Projects/HToWW/talks/2026-11-12-november-update-slide-plan]] and its requests: "implement hdamp also", "add a detailed breakdown of each systematic and its implementation, with plots and results of checks where nessary", "also an explaination for each systematic on what it is etc in the slides".

28 slides: 16 main (status, definitions, analysis recap, arms A/B, samples and 125.09 normalisation, prompt-lepton ONNX, speed-ups, event MVA strategy and duplication fix, negrw v2 with two plots, systematics overview, hDamp, results slot, open questions) and 12 backup (8 systematic-group slides with what/why, prescription/scope, evidence/status for every source; negrw SR plots; c-tag categories; production bookkeeping).

Evidence boundary: only the corrected negrw v2 report has fresh plots (4 PNGs copied to `assets/` with provenance JSON; regenerable, gitignored). No RUN templates, systematic Up/Down plots, impacts or limits exist yet, so those are explicit "pending" slots. Status snapshot is 12 Nov ~16:45 CET and must be refreshed before the talk. hDamp: samples configured in all eras, no template or card; Chirayu deferred its implementation until after the MVA training ("do it later, not now"). The "since September 8" baseline deck is not in the vault, so nothing is labelled as new since that date. All analysis claims are agent-reported.

Checks for r1: 28 slides / PDF pages; headless Chromium reports zero overflow, script errors, failed or external requests; dense slides inspected visually. Scripts-disabled Chromium shows all 28 sections, no horizontal overflow, no broken images; not opened in Obsidian itself. Built by `build.py`.
