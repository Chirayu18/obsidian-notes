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

### HIG-24-018 (paper) ⭐ the primary methodological reference
- **File:** [[HIG-24-018-paper-v15.pdf]]
- **Title:** Simultaneous probe of the charm and bottom quark Yukawa couplings using ttH events, 138 fb⁻¹.
- **Why:** the argmax-channelization (SR + CRs) strategy our combine pipeline mirrors — and it
  matches us on **three** axes: argmax-defined regions, the **same 11 mutually-exclusive 2D
  c-tag categories** (B0–B4/C0–C4, fed to the classifier as booleans exactly like our one-hots),
  and a charm-Yukawa target.
- **Key technique we do NOT use:** CRs are assigned by a **weighted argmax** — per-class weights
  100/12/4/2/1 "optimized to enhance the purity of each CR" (lines 576–578). Config-level lever,
  no retraining. Also has a **validation sideband** (0.4 < D_ttX < 0.6) and a hierarchical cut on
  the *summed* discriminant before the argmax.
- **Read with:** [[2026-08-11-mva-defined-regions-literature]] §0.
- **EOS original:** `/eos/home-c/cgupta/HToWW/b-hive/docs/HIG-24-018-paper-v15.pdf`

### arXiv:2011.03652 — CMS ttH/tH multilepton (the published argmax precedent)
- **File:** [[2011.03652-ttH-multilepton-argmax-ANN.pdf]]
- **Why:** peer-reviewed CMS result **in a H→WW decay channel** that classifies events into
  "ANN output node categories" **by the highest-activation output node**, uses background nodes
  as fit categories, and leaves **ttW and ttZ rates unconstrained** — the published justification
  for our argmax regions + `rate_params: [tt]`. Also feeds two *conventional* CRs into the same
  fit alongside the argmax categories.
- **Sections:** §6 (ANN, p.17), §7.3 (CRs, p.24), §7.4 (unconstrained rates).

### arXiv:2503.08797 — CMS cH → γγ (same physics, different choices)
- **File:** [[2503.08797-cH-diphoton-charm.pdf]]
- **Why:** charm-associated Higgs with **ggH as the degenerate background** — our exact problem.
  Uses **two binary BDTs** (cH-vs-ggH, cH-vs-continuum) rather than one multiclass, and
  **deliberately excludes c-tagging from the training** so the ggH heavy-flavour uncertainty stays
  a clean normalisation (contrast HIG-24-018, which does the opposite). Chose ~30% charm
  efficiency and **dropped CvsB** as only a minor improvement — independent support for our
  CvL/CvB findings and for keeping the medium WP.

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

### Negative-weight REWEIGHTING — arXiv:2510.16217  ← THE method we implemented
- **File:** [[2510.16217-negweight-reweighting.pdf]]
- **Title:** *Reweighting negative-weight Monte Carlo events with uncertainty quantification* — Palmer & Kronheim.
- **Method:** train a classifier for P₊(x⃗)=P(weight>0|gen kinematics); reweight by g(x⃗)=2P₊−1 so the
  estimator is `Σ|w|·g` (no ±cancellation) → higher N_eff. Ensemble → observable-level shape uncertainty.
- **Key results we use:** normalization preserved **exactly by construction for the true g** (Eqs. 2–6,
  "PDF = PDF_reweight"); closure demonstrated on **training variables** (§V C); uncertainty from an
  ensemble (§IV B), applied event-level (§IV C) or observable-level (§IV D). Validated on a **V+jets Sherpa
  sample, ~70% positive weights** in the hard-Vpt region — our exact regime.
- **Our implementation + a subtlety:** we see a finite-stat SR closure offset (~6%) and renormalize the
  reweighted vjets template per dataset — an **extension beyond** the paper (theirs closed cleanly enough
  to skip it). Full reasoning: [[2026-07-17-closure-renormalization-decision]]. Training deck +
  results: `Projects/HToWW/negrw-training/slides.md`.

> Convention: reference papers/PDFs live here under `References/<Project>/` (committed); generated
> notes live under `Projects/<Project>/`; regenerable plots/data stay on EOS and are linked.
