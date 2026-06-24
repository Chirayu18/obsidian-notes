---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# HToWW — reference papers / analysis notes

The big PDFs that combine work is benchmarked against. Committed here in the vault so they
open directly in Obsidian on the laptop.

### AN-23-102 (the analysis note benchmarked against)
- **File:** [[AN-23-102.pdf]]
- **Title:** Search for the Higgs plus charm quark production mode in the H→WW leptonic channel, full Run 2.
- **Why:** the reference for all our combine comparisons — 1POI expected limit **505 @ 138 fb⁻¹**, S+B tt SF
  (Table 17), uncertainty breakdown (Table 18: 60% statistical), systematics list (§7.1/7.2).
- **EOS original:** `/eos/home-c/cgupta/HToWW/b-hive/docs/AN2023_102_v14 ... (1).pdf`

### HIG-24-018 (paper)
- **File:** [[HIG-24-018-paper-v15.pdf]]
- **Why:** the argmax-channelization (SR + CRs) strategy our combine pipeline mirrors.
- **EOS original:** `/eos/home-c/cgupta/HToWW/b-hive/docs/HIG-24-018-paper-v15.pdf`

### MVA_Studies (proposed Run 3 talk, Athens 2026)
- **File:** [[MVA_Studies.pdf]] (in `References/MVA_Studies_Athens_2026/`)
- **Why:** the proposed Run 3 H+c (H→WW) MVA talk — κ-HCE discriminant, v11/v32. Its backup
  flags the **autoMCStats / W+jets-DY SR-undersampling limitation** (the [[2026-06-23-automcstats-rootcause]]
  issue) and names the fix: cross-era template averaging = AN-23-102 §6.1's W+jets method.

### autoMCStats slides (Marp deck)
- **Folder:** `References/HToWW/automcstats-slides/` — `2026-06-24-automcstats-slides.md` (+ embedded plot PNGs).
- **Why:** the deck on the autoMCStats / DY-W+jets SR-undersampling issue and the DY-smoothing fix.
  Renders to PDF via `npx @marp-team/marp-cli ... --pdf --allow-local-files`. Source note:
  [[2026-06-23-automcstats-rootcause]]; cites AN-23-102 §6.1 + [[MVA_Studies.pdf]].

### Negative-weight elimination — arXiv:2109.07851  ← THE fix for our neg-weight problem
- **URL:** https://arxiv.org/abs/2109.07851
- **Title:** *Unbiased Elimination of Negative Weights in Monte Carlo Samples* — Andersen & Maier.
- **Method:** cell resampling — removes negative MC event weights while preserving all physical
  observables, process-independent, improves as sample size grows.
- **Why it's our fix:** the autoMCStats blow-up is driven by the DY/**W+jets** +79k/−79k generator-weight
  **cancellation** that makes SR bins like `0 ± 41` (see [[2026-06-23-automcstats-rootcause]]). This kills
  the negative weights at the source → no cancellation → real per-bin MC stats. **Validated in the paper on
  W+2-jet @ NLO — literally our `WtoLNu_2Jets` sample.** Strictly better than our template smoothing
  (which only masks the symptom). Apply upstream (resample the W+jets/DY parquets) before combine.

> Convention: reference papers/PDFs live here under `References/<Project>/` (committed); generated
> notes live under `Projects/<Project>/`; regenerable plots/data stay on EOS and are linked.
