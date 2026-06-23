---
tags:
  - reference
status: done
date: 2026-06-17
source: lxplus
---

# HToWW — lxplus combine dump (index)

lxplus dump of the H+c → WW analysis docs + combine findings (2026-06-17 session).
Notes live here under `Projects/HToWW/`; reference papers (PDFs) live under `References/HToWW/` ([[papers]]).

## Curated session notes (combine v11/v32)
- [[2026-06-17-combine-v11-v32-findings]] — full combine findings: limits, why-√L-scaling-fails, σ_syst floor, autoMCStats domination, dead ends, fixes, v32 specifics.
- [[2026-06-17-systematics-reference]] — every systematic implemented + missing vs AN-23-102.
- [[combine-plots]] — combine final plots (CERNBox links).

## b-hive docs (`bhive-docs/`)
- `combine_findings_v11_v32.md`, `combine_v11_study.md`, `systematics_reference.md` — this session's combine work.
- `combine.md` — combine experiment log (v1/v2/v3…).
- `combine_framework_plan.md`, `combine_framework_presentation.md` — combine framework design/slides.
- `framework.md` — b-hive framework overview.
- `MVA.md`, `MVA_presentation.md`, `HPlusCHToWW_MVA_Guide.md` — MVA training (incl. kappa-HCE novel auto-grouping idea).
- `migration_plan.md`, `migration_slides.md`, `migration_v2_state.md` — higgscharm migration line.

## higgscharm docs (`higgscharm-docs/`)
- `README.md`, `GUIDE.md`, `QUICKSTART.md` — repo overview / how-to.
- `workflows-README.md`, `data-README.md` — analysis workflows & data config.

## Key takeaways (one screen)
- **Limits @26.7 fb⁻¹:** v11 = 1742 (stat 771), v32 = 1919 (stat 584). AN = 505 @138 fb⁻¹.
- **Systematics-limited, not stat-limited:** our stat floors *beat* the AN's at equal lumi; the gap is σ_syst (923 vs 170, ×5.4, lumi-independent → plateau ~1550).
- **Dominant systematic = autoMCStats (MC-stat, ~41%)**, not theory. Fix = cross-era MC template averaging.
- **Biggest missing systematic = charm-jet tagging** (no weight column exists; needs upstream PNet SF).
- Dead ends (all tested): binning, tt rateParam, discriminant/collapse, variation-smoothing, S/B.
