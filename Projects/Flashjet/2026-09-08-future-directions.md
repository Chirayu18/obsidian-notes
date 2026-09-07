---
tags: [reference]
status: active
date: 2026-09-08
source: lxplus
---

# Where to go after PLuM — ideas worth trying, and why the obvious ones are not

## The pattern in what has already failed

| attempt | verdict | why |
|---|---|---|
| per-particle C/A (5 feat) | null, −0.114 over the full run | 2-body → `PairEmbed` computes it by construction |
| share_bp rule A | identically zero | degenerate encoding |
| share_bp rule C | dropped | recoverable at AUC 0.87 from the pair's own Lund vars |
| subjet (mass / ptfrac / nconst) | null, +0.007 (t = +0.34) | **n-body and genuinely unrecoverable (probe R² = 0.05) — and still nothing** |
| PLuM kT Lund tokens | running, [[2026-09-08-plum-arm-launched]] | — |

The **arity argument** explains the first three: Lund coordinates at a splitting are
built from two 4-vectors, and ParT's `PairEmbed` already computes a learned function
of every pair. **It does not explain subjet.** That one was n-body, probe-confirmed
unrecoverable from ParT's own per-particle inputs, and still trained to parity.

Gouskos & Maier reach the same conclusion from the other direction — their attention
analysis finds splitting tokens attend to particles and not the reverse, and they
write that "the hierarchical branching structure is already implicitly encoded in the
particle embeddings through self-attention" ([[2026-09-07-plum-paper-vs-our-result]]).

**The lesson: ParT with full pairwise attention over 128 constituents is close to
saturated on JetClass.** "Add another engineered feature" is therefore the family of
ideas *least* likely to work — it has been falsified four times. The directions below
are the ones that are not that.

---

## 1. Subjet-level DISPLACEMENT aggregates (the highest-upside new arm)

**The idea:** keep the subjet grouping that `utils/flashjet_subjet_features.py`
already computes (C/A tree declustered at a kT cut, each particle assigned to a
subjet). Change only *what is summed over the group*.

- **now:** mass, pT fraction, constituent count — all built from the 4-vectors
- **instead:** Σ IP significance from `d0val/d0err`; count of tracks with
  |d0|/σ > 2 and > 3; a vertex-mass proxy built from the displaced tracks only

**Why this is different in kind from all four nulls.** Every previous arm added a
quantity *derivable from the constituent four-vectors ParT already sees*. Displacement
lives in different input columns — `part_d0val`, `part_d0err`, `part_dzval`,
`part_dzerr` — and ParT sees those **per particle** but has no mechanism to form
"the collective displacement of a coherent group". That is a genuine n-body operation
over a set the model must first identify.

It is also the mechanism the PLuM authors themselves name for their **only** real
gain: b vs c decay length ("charm hadrons exhibit decay lengths roughly a factor of
two to three shorter than those of B hadrons"), obtained in a Delphes setup **with no
secondary-vertex inputs**.

**Honest prior: ~30–35%.** Higher than the previous arms, still not high. ParT does
see per-track IP, and 8 attention layers over 128 tokens is a lot of capacity for
learning "several tracks share a displaced origin" — so this could fail exactly the
way subjet mass did: real information, already reachable.

**Design notes if built:**
- cut on **displacement significance**, not raw d0
- denominator should be the subjet's **track** multiplicity, not all constituents —
  neutrals carry no IP and dilute the aggregate
- run the **probe first** (variant of `prong.py`, reuses the subjet assignment, no
  new clustering): can an MLP recover `subjet_ip_sum` from that particle's own inputs
  plus the 2-body control? **A good probe is NOT sufficient** — subjet mass had
  R² = 0.05 and trained to nothing — but a *bad* probe kills the idea for one day's
  work instead of a training slot.

---

## 2. Ablate `pair_embed` on the baseline (cheapest, most certain to yield a slide)

Not a new feature: **remove** one. Train stock ParT with the pairwise attention bias
switched off.

- if accuracy barely moves → the redundancy claim is **proven**, and the whole study
  becomes "ParT's attention already does substructure, here is the measurement"
- if it drops a lot → you have **quantified what the 2-body channel is worth**, which
  is the number the arity argument has been asserting without measuring

Either outcome is a result, which is what makes this the safest use of a training
slot. It is the natural companion to the arity argument rather than another test of it.

---

## 3. Data-scaling scan — reframes four nulls as one finding

Every null so far is at **100M jets / 1M iterations**, where the model has enough data
to learn anything learnable. The honest hypothesis for why engineered features fail:
**they are a prior, and priors help when data is scarce.**

Train baseline vs CA5 vs subjet at **1M and 10M jets** as well. If the features win at
low statistics and converge at high, that is a real, quotable, physically sensible
result — and it changes the talk from *"we tried four things, none worked"* to
*"engineered substructure features are a prior that ParT outgrows, and here is the
crossover."* Same experiments already done, much stronger claim.

---

## Ranking

1. **(2)** — cheapest, guaranteed slide either way
2. **(3)** — turns the existing negative results into a positive story
3. **(1)** — highest upside, genuinely new information channel

## The constraint that matters more than the idea

There is a **0.088-point checkpoint noise floor** at 900k+ and **one seed per arm**.
Whatever comes next, the seed budget dominates: **two seeds of one experiment beats
one seed of three.** PLuM's own Table I quotes a top-5-of-10 subsample with no spread
published — do not repeat that; quote the full-sample mean and spread.

## Related

[[2026-09-07-plum-reproduction-plan]] · [[2026-09-07-herwig-robustness-result]] ·
[[2026-09-04-subjet-verdict]] · [[2026-09-06-logit-discriminant-bug]]
