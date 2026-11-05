---
tags: [slides]
status: active
date: 2026-11-05
source: laptop
---

# Full rerun progress deck

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
