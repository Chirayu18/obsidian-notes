---
tags: [reference]
status: active
date: 2026-07-17
source: lxplus
---

# Neg-weight reweighting: the SR closure offset + renormalization decision

## The observation
After the vjets SR re-run (clusters 9087051/52/53), the reweighted estimator
`Σ|w|·g` does **not** exactly reproduce the nominal yield `Σw` in the tight eμ SR:

| dataset | rows | closure ratio Σ\|w\|g / Σw |
|---|---|---|
| DYto2L_2Jets_50 | 9646 | **1.014** |
| WtoLNu_2Jets | 485 | **1.133** |
| DYto2L_2Jets_10to50 | 74 | 2.24 (74 rows → statistical noise) |
| **TOTAL** | 10205 | **1.058** (+6%) |

On the **training region** (9.83M events) closure was **0.994**. So the offset appears
only when we restrict to the SR.

## Is this a bug? No.
`g(x⃗)` is applied per-event with the values it was trained to produce. The columns are
sane (0 NaN, all g∈[−1,1], per-event varying). The offset is a **finite-statistics
closure residual**, not a code error. The SR is a small (~10⁴ events),
kinematically-biased corner of the training domain, so the per-event g values don't
perfectly average to the local positive-fraction there.

## What the paper (arXiv:2510.16217) actually says
The method preserves normalization **EXACTLY, by construction** — for the *true* P₊.
Derivation (their Eqs. 2–6):

- PDF(x⃗) = a·PDF₊(x⃗) − b·PDF₋(x⃗),  with a,b≥0, a>b, a−b=1   (Eq. 2)
- P₊(x⃗) = a·PDF₊ / (a·PDF₊ + b·PDF₋)   (Eq. 3)
- ⇒ PDF(x⃗) = (2P₊(x⃗) − 1)·(a·PDF₊ + b·PDF₋)   (Eq. 4)
- g(x⃗) ≡ 2P₊(x⃗) − 1   (Eq. 5)
- PDF_reweight(x⃗) = g(x⃗)·(a·PDF₊ + b·PDF₋)   (Eq. 6)

> **"By construction it is equal to the original construction, so PDF = PDF_reweight."**  (p.6)

So in the paper **there is no yield offset to correct, and they apply NO post-hoc
rescaling** — they don't need to, because Eq. 6 is an algebraic identity in the *exact* g.

**The catch:** that identity holds for the **true** P₊(x⃗). In practice we use an
*estimated* P̂₊ from a finite-statistics classifier, so closure becomes **empirical** —
which is exactly why the paper devotes §V to closure studies and §IV B to uncertainty
estimation. Their closure is demonstrated on the **training variables** (§V C) and is
good enough that no residual rescale is reported. They do **not** document a residual
SR-yield rescale — because theirs closed well enough not to need one.

## Our decision: renormalize the reweighted vjets template per dataset
Rescale each reweighted vjets SR template so its integral matches the nominal:
`template *= Σw / Σ|w|g` (per dataset), and scale sumw2 by the square.

**Why this is correct, not a fudge:**
1. The reweighting is meant to fix **VARIANCE (N_eff), not change the central yield.**
   The central yield should equal nominal — that is precisely what exact closure (the
   paper's Eq. 6) guarantees in the large-N limit. Renormalizing forces our *empirical*
   estimate back onto that guaranteed result.
2. It is **standard, shape-only template practice** — identical in spirit to what
   `dy_template_smooth.py` already does: it smooths the vjets shape then rescales the
   smoothed template back to its **own original yield** ("shape-only: rescale smoothed
   template to its OWN original yield so the datacard rate (nominal) ... [is] preserved").
   We are applying the same yield-preserving discipline to the reweighting step.
3. It **preserves the entire benefit**: the N_eff gain (**3.44× in the SR**, 455→1563)
   comes from the reduced per-bin variance of `Σ|w|g`, which a global rescale does not
   touch. We keep the variance reduction; we only pin the normalization.

**Honest caveat (documented):** this per-dataset renormalization is an **extension beyond
what the paper explicitly does** — the paper's closure was clean enough to skip it. It is
defensible and conventional, but it is *our* addition to handle the finite-stat SR offset,
not a step blessed in arXiv:2510.16217. It should be stated as such in any writeup/thesis.

**Alternatives considered:** (a) accept the 6% as-is — rejected: rides into the fit as a
real vjets normalization change, not a variance fix; (b) investigate WtoLNu's 13% first —
deferred: worth a look (feature coverage of the W SR corner) but the total 6% is tiny vs
the r₉₅=1742 problem and shouldn't block the limit.

## Implementation note
Do the rescale where the vjets SR template is built
(`make_combine_histograms_v11_v32.py`, filling with `|weight_nominal|·weight_negrw`), BEFORE
`dy_template_smooth.py` runs — smoothing already re-pins to its input yield, so as long as
the input is the renormalized template, the datacard rate stays = nominal. The ±weight_negrw_std
ensemble spread still provides the PCA/shape nuisance on top.

See [[hww-negweight-reweight-fix]] · paper: `References/HToWW/2510.16217-negweight-reweighting.pdf`
