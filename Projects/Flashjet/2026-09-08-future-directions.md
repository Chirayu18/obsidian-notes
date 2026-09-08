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

## 1. ~~Subjet-level DISPLACEMENT aggregates~~ — PROBED 2026-09-08, DON'T BUILD

**The idea:** keep a subjet grouping, but aggregate *displacement* over it
(sum/mean IP significance, counts of tracks above 2σ/3σ) instead of mass.
Motivation was that every previous arm added quantities derivable from the
constituent **four-vectors**, whereas displacement lives in different columns
(`part_d0val/d0err/dzval/dzerr`) that ParT sees per particle but cannot pool
into "these tracks share a displaced origin". It is also the mechanism
Gouskos & Maier credit for their only real gain (b vs c decay length), obtained
in Delphes **without** secondary-vertex features.

**Probe: `~/flashjet_condor/ip_probe2.py`.** Subjets from flashjet's own
`exclusive_jets_from_history` (`history.py:201` — the standard FastJet
`ClusterSequence::exclusive_jets` definition, cross-checked against FastJet in
`tests/`) with **`algorithm="kt"`**, n_jets=3 → 12.5 constituents/subjet.
Control = the particle's own 19 inputs (including all four IP columns) plus
jet-level 2-body moments. 20,000 particles, all 10 classes, zero NaN.

| target | linear R² | MLP R² | verdict |
|---|---|---|---|
| subjet sum IPsig | 0.346 | 0.421 | partly |
| subjet mean IPsig | 0.249 | 0.382 | partly |
| **subjet n(IPsig>2)** | 0.443 | **0.599** | **RECOVERABLE** |
| **subjet n(IPsig>3)** | 0.401 | **0.594** | **RECOVERABLE** |
| *[ref] subjet ln mass* | *0.044* | *0.052* | *unrecoverable — and STILL trained to parity* |

**Verdict: do not build this arm. Prior drops ~30–35% → ~12–15%.**

The aggregates are ~60% recoverable from what ParT already sees per particle —
a strictly **weaker** starting position than subjet mass, which was genuinely
unrecoverable (R²=0.05) and still gave +0.007 (t=+0.34, n=50). Counting tracks
above a significance threshold is nearly a sum over per-particle features the
model already has, and attention pools sums well.

**The tension worth stating in the talk.** The physics *is* there — this is a
strongly discriminating variable in absolute terms:

| | QCD | Hbb | Hcc | Tbqq |
|---|---|---|---|---|
| n(IPsig>3), jet-level | 0.549 | **3.315** | 1.376 | 2.144 |

Single-variable **Hbb vs QCD AUC = 0.953**, with the Hbb > Hcc > QCD ordering
reproducing the b-vs-c lifetime hierarchy the PLuM authors invoke. It is simply
**not new to ParT** — the same trap as all four arms: real information, already
reachable.

**Asymmetry fixed in advance:** a *low* R² would NOT have blessed the idea
(subjet mass proves that). A *high* R² does count against it, because it names a
concrete reason the model would not need the feature. The probe could only kill
the idea cheaply, and it did — one day instead of a training slot.

**If displacement is still wanted:** the version with a real chance is a
**learned vertex fit** — actual displaced-vertex reconstruction (position, mass,
flight significance), not aggregates of per-track IP. That is genuinely not a
sum over particle features. Substantially more work; wait for the PLuM arm.

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

## Ranking (updated 2026-09-08 after the displacement probe)

1. **(2)** ablate `pair_embed` — cheapest, guaranteed slide either way
2. **(3)** data-scaling scan — turns the existing negative results into a positive story
3. ~~(1) displacement aggregates~~ — **probed and rejected**, see above

With (1) out, the honest position is that **no remaining feature-engineering
idea has a good prior**. (2) and (3) are both *measurements about* the null
rather than attempts to overturn it, which is where the value now is.

## The constraint that matters more than the idea

There is a **0.088-point checkpoint noise floor** at 900k+ and **one seed per arm**.
Whatever comes next, the seed budget dominates: **two seeds of one experiment beats
one seed of three.** PLuM's own Table I quotes a top-5-of-10 subsample with no spread
published — do not repeat that; quote the full-sample mean and spread.

## Related

[[2026-09-07-plum-reproduction-plan]] · [[2026-09-07-herwig-robustness-result]] ·
[[2026-09-04-subjet-verdict]] · [[2026-09-06-logit-discriminant-bug]]
