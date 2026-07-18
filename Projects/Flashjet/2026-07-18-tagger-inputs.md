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

## Follow-up: 13 physics-motivated FUNCTIONS of the 18 variables (`tagger_functions.py`)

Dimensionless, physics-closed combinations to feed a tagger instead of raw variables
(mostly pt-decorrelated by construction):

| function | formula | physics |
|---|---|---|
| lnρ | $\ln(m_{SD}^2/p_T^2R^2)$ | QCD scaling variable (QCD flat in lnρ) |
| ln m_SD | — | the one absolute (resonance) scale |
| f_groom | $m_{SD}/m_{ung}$ | grooming survival: decays keep mass, QCD doesn't (0.747 alone) |
| f_z | $\sqrt{d_{12}}/m_{SD}=\sqrt{z/(1-z)}$ | momentum sharing of the mass-defining split |
| f_21, f_32 | $\sqrt{d_{23}}/\sqrt{d_{12}}$, $\sqrt{d_{34}}/\sqrt{d_{23}}$ | prong hierarchy |
| χ | $\sqrt{z_g(1-z_g)}\,p_T R_g/m_{SD}$ | 2-prong closure; χ<1 flags **massive prongs** (top→Wb) |
| ψ₁, ψ₂ | $\ln k_t^{(1,2)} - \ln m_{SD}$ | is the (2nd-)hardest emission at the decay scale? |
| f_match | $\ln(\Delta R_{kt1}/R_g)$ | hardest-kt emission ≡ soft-drop split? |
| ln(1+n_drop), n_kt1, n_kt5 | — | declustering patience + perturbative activity |

Results (same logistic setup): functions-only **0.813** (13 vars, vs 0.829 for raw-18 —
the counting variables carry some irreducible non-ratio information); functions+raw 0.831;
**mass-decorrelated set (no lnρ/ln m_SD): 0.797** — near mass-scale performance with no
explicit mass input, the sculpting-safe option. Logistic weight ranking after the two mass
scales: ψ₁, n_kt1, ψ₂, f_match, ln(1+n_drop). Plot: `tagger_functions.png`.

**Recommendation for a tagger**: feed the 13 functions as `global_features` (compact,
interpretable, decorrelation-friendly — drop lnρ/ln m_SD for a mass-decorrelated tagger),
and add the raw counting trio (n_lund, n_kt1, n_kt5) which the ratios don't fully cover.
For the *full* merge history as a sequence input, see [[2026-07-18-history-tagger-design]].

Plots: `tagger_quick.png` (first pass), `tagger_study.png` (full set),
`tagger_functions.png` (physics functions) — links in [[plots]].
Related: [[2026-07-17-plots-explained]], [[2026-07-13-cms-validation]].
