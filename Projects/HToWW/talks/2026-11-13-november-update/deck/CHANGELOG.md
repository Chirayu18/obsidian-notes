---
tags: [slides]
status: active
date: 2026-11-12
source: laptop
---

# November analysis update deck

## r4 — 2026-11-13

Chirayu: "If likelihood scan is not there , do it" (κc interpretation then withdrawn: "Forget the kc interpretation btw"), and "Also can you add a systematic share comparision with run 2... Our impacts vs their impacts?". The Codex keeper hit its usage limit mid-r3; the Claude keeper reviewed r3 and continued.

- **New `oct-scan`:** blind Asimov (μ = 1) scan of r on the unchanged October four-era workspace `full_run3.ws.root`, total and statistical-only (all constrained nuisances frozen). Run by the keeper on lxplus (`~/htoww_submit_logs/scan_oct691_20261113/`). Cross-check: AsymptoticLimits on the same workspace gives expected μ < 691.0 (16%/84%: 459.3/1090.4). 68% interval −294…+309 (stat-only −168…+171); 95% −637…+693. It replaces the August single-era scan in backup. Points and script are in `assets/oct_scan*`.
- **New `run2-compare`:** HIG-24-009 Table 3 (1POI) vs the 21 Oct group-freeze study of the same October card, both of our conventions shown. Numbers taken unchanged from [[Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3]]. Chart from `assets/run2_vs_run3_impacts.py`, colours validated with the dataviz palette checker.
- **Text fix:** the r2/r3 text had lost spaces between words and numbers ("The1October", "Top30of55") and some notes had lost all spaces. `spacing.py` restores them in the generated HTML and speaker notes; about a dozen fully glued phrases were rewritten by hand.
- **Conclusion reframed** (Chirayu, 13 Nov: "Say exactly this: With these prescriptions agreed, no further method development is needed; the remaining steps are production and the listed inputs."). `open` is now "Proposed baseline and path to the result": Arm A (all central samples, per-event scale fix) as baseline, B as cross-check, the agreements requested and the remaining production and input steps. The take-away is his sentence verbatim. `arms` now proposes A as nominal and B as cross-check. The deck still claims no corrected result or approval readiness.
- **No personal attributions on slides or in speaker notes** (Chirayu: "Dont mention: by Chirayu’s report..."): removed "by Chirayu’s report", "per Chirayu", "by user decision", "by the keeper" and "agent-reported" wording from the presented material. Only the speaker name on the title slide remains. Provenance stays in the vault notes.
- **Closing slide inputs updated** from Chirayu's answers ([[Projects/HToWW/combine-systematics/2026-11-13-open-inputs-decisions]]): "Inputs we will ask for" (H+c αS rate; H+b PDF+αS overlap), "Expected" (c-tag update), "We implement" (hDamp, BR decay-component scope, ttH→ττ check). negrw fit-bin closure dropped from the list.
- **negrw slides softened** (Chirayu: "Soften the negrw slide"): `negrw-limits` is now "Closure: good overall, residual shape in some samples"; the take-away states the 0.2% overall closure and that the nuisance partly covers the residual shape; the "required fit-bin check" line is removed (also from `syst-overview`). The backup SR take-away is reworded. The numbers are unchanged (χ² 47.2/20, 35.0/20 with the nuisance). The `hdamp` backup subtitle now reads "To be implemented after MVA training".
- **Updated from the two HToWW agent threads** (Chirayu: "check the things I discussed with both the HToWW agents, and update slides accordingly, we won't even present a stat only limit also now for A/B"). 58 slides (43 main + 15 backup).
  - **No A/B limit, not even stat-only.** The A stat-only and rate-systematics expected limits in [[Projects/HToWW/framework/2026-11-13-a-limit-plots]] are not shown; title and speaker-note scope lines say so.
  - **New `oct-fitband-sources` and `oct-fitband`:** October data/MC with the band built as the fit uses it (tt without μR/μF and PS), from [[Projects/HToWW/samples-and-production/full-rerun/2026-11-13-postfix-datamc]]. Symmetrised half-widths 18.7/20.1/17.5/18.0% → 10.6/12.8/8.3/9.3%; c-tag 2D SF is 65–89% of what remains; 2022postEE 5/18 MET bins inside the band.
  - **New `postfix-datamc`:** TRAIN v2 (Arm A inputs), nominal only, MC-stat band. MET slope gone in 2023, −0.097 ± 0.008 per 100 GeV remains in 2022postEE.
  - **New `a-performance`:** Arm A held-out ROC and confusion matrix (unweighted MC; H+c AUC 0.956) from [[Projects/HToWW/framework/2026-11-13-a-performance-plots]]. No v11 comparison claimed.
  - **`mva`:** v11 recipe with 2D c-tag inputs, class-weighted cross-entropy, and the ONNX export with held-out agreement (max 2.1×10⁻⁶) per [[Projects/HToWW/talks/2026-11-13-onnx-export-slide-decision]].
  - **c-tag split into sources "to come in the next limit":** on `syst-overview`, `backup-ctag` and `open`. No split numbers shown (the split was still running).
  - **`oct-impact-table`:** take-away now lists the ranking caveats from [[Projects/HToWW/combine-systematics/2026-11-13-october-impacts-checks-for-postfix-cards]] (three scale nuisances, one-sided old signal scale, 2022 c-tag at ±0.02).
  - **`arms`:** B's GEN split is stated as separate from the reco N<sub>c-jet</sub> SR split ([[Projects/HToWW/talks/2026-11-13-ab-physics-comparison-slide-decision]]).
  - **`open`:** production line updated (A trained, exported, scored; B training).
- No κc slide. No new A/B result: the scan and impacts belong to the pre-fix October card.

Checks: 54 slides / PDF pages, zero overflow, script errors or external requests; scripts-disabled Chromium shows all 54 sections, no broken images (`noscript-check.mjs`, now kept in the deck folder). New and respaced slides inspected visually. Not opened in Obsidian itself.

## r3 — 2026-11-12 (Codex keeper, not committed separately)

Selection pass after the r2 rebuild: physics results in the main story and engineering detail in backup; added central-sample inventory slides, October data/MC investigation, impact table and minor-update appendix (53 slides). Folded into r4.

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
