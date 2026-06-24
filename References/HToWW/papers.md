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

> Convention: reference papers/PDFs live here under `References/<Project>/` (committed); generated
> notes live under `Projects/<Project>/`; regenerable plots/data stay on EOS and are linked.
