---
tags: [slides]
status: active
date: 2026-11-05
source: laptop
---
# Framework review deck

## r2 — 2026-11-06

Chirayu explicitly requested detailed, human-readable slides (verbatim feedback in Meta/roles/update-slide-style.md). Expanded to 10 slides: 8 main explanations and 2 backup finding tables. Covers one validation owner, approximate split bars, per-fold cache safety, correction that b-hive ignores event weights, mode schemas, test boundaries, F1–F18 status, decisions and approval-dependent next steps. Stable status/result-schemas/open IDs preserved. Sources are worker commit 9ef65a9 and its saved logs; patch hash checked by keeper. All analysis claims remain agent-reported; no keeper rerun of unchanged tests.

Checks for r2: 10 slides / PDF pages; headless Chromium reports zero overflow, script errors, failed requests or external requests. Every slide was inspected (changed slides for the full-rerun deck); representative PDF raster inspected. Scripts-disabled Chromium shows all sections without horizontal overflow; not opened in Obsidian itself. All source-note targets and slide anchors were checked. PNG/PDF exports remain gitignored.

## r1 — 2026-11-05

Requested by Chirayu after the two audits: “deck updated? Maybe this goes in a different leaf? idk”. Framework-core results live here; no notes moved. Three slides: reproduced integration blockers, mode schemas/consumers, remaining guards and validation. Run A physics/training gates remain in the full-rerun deck. All research findings remain agent-reported. Build: `node Projects/HToWW/framework/deck/render.mjs --revision=1`; PDF stays local-only.

Render check (2026-11-05): headless Chrome found no slide overflow, script errors, failed requests or external requests. Scripts-disabled Chromium showed every section (3 framework / 8 full-rerun), without horizontal overflow; this emulates the viewer setting, not an inspection in Obsidian itself. Exported PDFs have 3 / 8 pages; representative rasterized pages were inspected. PDFs and render PNGs remain local-only.

Navigation, same review iteration: source-note links now use `obsidian://open` for vault `obsidian-notes`; each deck links to its owner README and root slide index. The hub links back to the vault, Dashboard and HToWW. Paths were checked locally; Obsidian URI dispatch itself was not exercised.
