---
tags: [reference]
status: active
date: 2026-07-18
source: lxplus
---

# Merge-history variables as jet-tagger inputs (kT + C/A)

The Status.md TODO: *use jet understanding from kT (splitting scales, exclusive
structure) + C/A variables (Lund coordinates, grooming sequence) as tagger inputs.*
Everything below is a **post-read of the two merge histories flashjet already
records** — no re-clustering, GPU-batchable, so an 18-variable input vector costs
essentially nothing on top of the jets themselves.

## Setup

- **Signal**: leading AK8 jets, $t\bar t\to 4q$ (Run 3 2024, 13.6 TeV JMENanoV15) — real boosted W/top.
- **Background**: QCD flat (UL18 JMENano 150X).
- Selection identical to the validation plots (raw $p_T>300$, $|\eta|<2.4$, 2–200 linked PFCands),
  restricted to $p_T$ 300–800 and **background pt-reweighted to the signal spectrum** so pt itself
  is not the discriminant. 16 281 signal / 51 008 background jets.
- Discriminant = weighted logistic regression on standardized (log-scaled where dimensionful)
  features; AUC from the weighted ROC. Deliberately linear/simple — this measures the
  *information content of the inputs*, not classifier power.
- Scripts: `tagger_quick.py` (checkpoint-only first pass), `extract_tagger_vars.py`
  (per-jet extraction, HTCondor **9128460**, full files → `tagger_vars_sample{0,1,2}.npz`),
  `tagger_study.py` (this study). All in
  `/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`.

## Variables (all from the two histories)

| group | variables | source |
|---|---|---|
| mass-scale | $m_{SD}$, $\sqrt{d_{12}}$, $m_{ung}$, $k_{t,g}=z_g p_T R_g$ | C/A groom + kT scales |
| 3-prong kT | $\sqrt{d_{23}}$, $\sqrt{d_{34}}$, $\sqrt{d_{23}}/\sqrt{d_{12}}$ | kT `splitting_scales()` |
| Lund/counting | $n_{Lund}$, $n(k_t>1)$, $n(k_t>5)$, $\ln k_t^{(2)}$, $\ln k_t^{(3)}$, $n_{drop}$, $n_{const}$ | C/A `lund_coordinates()` + groom |
| groom geometry | $z_g$, $R_g$, $z$ and $\Delta R$ of hardest-$k_t$ emission | C/A groom + Lund |

## Results

Single-variable AUCs: every **mass-scale** variable sits at 0.78–0.79 and they are
0.8–0.97 correlated (all probe the same 2-prong decay mass) — combining them alone
gives only 0.794. The complementary information is elsewhere:

| ladder step | # vars | AUC |
|---|---|---|
| mass-scale only | 4 | 0.794 |
| + 3-prong kT | 7 | 0.802 |
| + groom geometry | 11 | 0.806 |
| **+ Lund counting (full set)** | **18** | **0.827** |
| counting alone (no mass info) | 7 | 0.787 |

- **$n_{drop}$ is the sleeper** (AUC 0.764 by itself): decay jets pass soft drop after
  0–1 declusterings (the hard prong is the first wide split); QCD needs up to ~12.
- **$\ln k_t^{(2)}$** (second-hardest Lund emission, AUC 0.688) shows a second bump at
  $\ln k_t\approx 3.5$–4.5 in signal — the *second* decay splitting (top → W then W → qq̄),
  exactly the merge-history information a mass variable cannot see.
- **$\sqrt{d_{23}}$** (0.684) carries the 3-prong top structure; its ratio to $\sqrt{d_{12}}$
  peaks near 0.1 for signal (decay scales are hierarchical) vs broad for QCD.
- At 30% signal efficiency the full set roughly **doubles QCD rejection** (~100 vs ~45).

## Caveats

- Cross-era comparison (Run 3 signal vs UL18 background): counting variables are
  pileup-sensitive in principle. But the effect goes the *wrong way* to fake the result —
  the signal is the **higher**-pileup sample yet has **fewer** primary Lund emissions
  ($n_{Lund}$ shifted low, as expected for a color-singlet decay), so the discrimination
  is physical. A same-era QCD sample would still be the clean version.
- "Signal" = all TTto4Q leading jets (no gen-matching), so it is a W/top *mixture* with
  some unmerged jets — AUCs understate what a matched study would give.
- Logistic is linear; a BDT/NN on the same 18 inputs would land higher. The point here is
  input information, and the ladder ordering is the deliverable.

## Takeaway

The TODO's premise holds: **kT and C/A histories carry complementary tagger
information beyond the mass scale** — the declustering *sequence* (how many drops, how
hard the 2nd/3rd emissions) adds +0.03 AUC over mass-scale variables even with a linear
model, and it's free once the histories exist. Natural next step if pursued: gen-matched
W vs top vs QCD classes, same-era samples, and the full per-emission Lund list into a
small transformer/LundNet-style model (flashjet emits exactly that list, batched).

Plots: `tagger_quick.png` (first pass), `tagger_study.png` (full set) — links in [[plots]].
Related: [[2026-07-17-plots-explained]], [[2026-07-13-cms-validation]].
