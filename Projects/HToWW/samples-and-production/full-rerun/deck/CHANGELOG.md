---
tags: [slides]
status: active
date: 2026-11-05
source: laptop
---

# Full rerun progress deck

## r6 — 2026-11-05

Requested after the completed audits. Updated status, TRAIN/RUN impact, Run A gates, dated 3FS DAS progress and sources. Eight slides retained, stable IDs preserved. Framework details are in [[Projects/HToWW/framework/deck/CHANGELOG|the new three-slide framework deck]], linked from `result-trainrun`. Models, SFs and c-tag concerns remain evidence-qualified; code was not changed. Historical tests are distinguished from the reviewer-run 49-test log.

## r5 — 2026-11-05

The 3FS PDF item now reads "re-NANO submitted 2026-11-05, pending" (worker commit `187ce65`, Chirayu's OK). Route B stays parked. Same 8 slides.

## r4 — 2026-11-05

Chirayu: the slides lacked the TRAIN/RUN work, and things changed in the HToWW thread that were not recorded. The keeper read the Sol review thread in full and inspected the live higgscharm tree read-only. Changes:
- new `result-trainrun` slide (modes, chain, HZZ ports, checks and gaps);
- `status` now lists the uncommitted TRAIN/RUN work, the 49 tests (worker-reported), Route B's A/B-comparison aim and the ordered 3FS re-NANO;
- `result-routeb` records that the re-NANO was ordered and its submission is in progress;
- `open`: no EOS removal (new output location needed); uncommitted code needs review and commit.
8 slides. Render: no overflow, no errors; all 8 sections visible with scripts off. Still agent-reported.

## r3 — 2026-11-05

Requested by Chirayu ("update the slides and push") after the Sol review addenda (vault `667d396`, `fec22c9`, `729a8e7`, `75a193a`, `ce9211a`). Added `result-routeb`: Route B is parked and proposal-only, the review results, and the 3FS `LHEPdfWeight` cause as a non-blocking TODO. `status` and `open` now include the one-mH decision (0.7% BR offset). Scale-variation normalisation is listed only for the case where Route B returns. 7 slides.
Checks: `render.mjs --revision=3` gave no overflow, errors or external requests. The JS-disabled check shows all 7 sections. Still agent-reported.

## r2 — 2026-11-05

Requested: worker commits `f027bdc` and `9aa71d5` carry `make slides`, and Chirayu asked for a summary of the recent work and the independent review. Rebuilt from scratch as 6 slides (`status`, `result-code`, `result-review`, `result-pdf-alphas`, `open`, `backup-sources`). Static HTML, no Markdown plugin. A `<noscript>` layout shows every slide in Obsidian's viewer, which runs with scripts off.
Checks: `node render.mjs --revision=2` gave 6 slides, no overflow, no errors, no external requests. The JS-disabled Chromium check showed all 6 sections, and the screenshot was inspected. Not opened in Obsidian itself.
Sources: [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state]], [[Projects/HToWW/2026-11-05-sol-review-unpushed-work]], H+b, BR and speed-up notes. All content is agent-reported.

## Withdrawn from active index — 2026-11-05

Chirayu said this routine handoff did not need slides and the deck was too long; his exact feedback is in [[Meta/roles/update-slide-style]]. The draft and original r1 PDF are preserved, but removed from the active root slide index and README embeds. Current status lives in the [[Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state|handoff note]]. Likely cause of the blank render: Obsidian's HTML Page Viewer runs with scripts disabled by default, and this deck builds its slides from Markdown with JavaScript. The draft was not repaired, since it is withdrawn; future decks must be readable without scripts.

## r1 — 2026-11-05

First leaf-subproject progress deck: current status, Run A corrections and test boundary, unresolved normalisation, Run B production/filesets, recorded decisions, open choices, keeper changes, and dated production/evidence backup. Stable section IDs are kept in `index.html`; text is Markdown inside each section. Scientific content is agent-reported, primarily from worker commit `f26a601` and its final handoff. No new measured plot is invented.

- HTML: [open locally](index.html).
- Export: `full-rerun_r1.pdf` (local-only, gitignored).
- Runtime: vault-root `_shared/reveal/`, copied from existing local assets; no CDN.
- Build/check helper: `render.mjs`; uses installed `playwright-core` and headless Google Chrome. Run with `node Projects/HToWW/samples-and-production/full-rerun/deck/render.mjs` from the vault root; pass `--revision=N` for a later PDF revision.
- Outputs: local PDF plus render screenshots and a machine-readable check report in the ignored `.render/` directory. Every slide is checked for overflow, JavaScript errors, failed local requests and external network requests. The PDF is also rendered with Poppler and inspected before delivery.
- Review: [[Meta/keeper/2026-11-05-fullfix-review]].

Existing flavour-scheme and gridpack decks remain with their own leaf subprojects; this deck does not replace their methods or source plots.

Render check (2026-11-05): headless Chrome found no slide overflow, script errors, failed requests or external requests. Scripts-disabled Chromium showed every section (3 framework / 8 full-rerun), without horizontal overflow; this emulates the viewer setting, not an inspection in Obsidian itself. Exported PDFs have 3 / 8 pages; representative rasterized pages were inspected. PDFs and render PNGs remain local-only.

Navigation, same review iteration: source-note links now use `obsidian://open` for vault `obsidian-notes`; each deck links to its owner README and root slide index. The hub links back to the vault, Dashboard and HToWW. Paths were checked locally; Obsidian URI dispatch itself was not exercised.
