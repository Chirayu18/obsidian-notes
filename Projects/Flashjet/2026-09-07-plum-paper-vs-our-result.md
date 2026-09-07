---
tags: [reference]
status: active
date: 2026-09-07
source: lxplus
---

# PLuM (arXiv:2605.26821) vs our C/A + subjet result

Paper: **Gouskos & Maier, *Particle-Lund Multimodality in Jet Taggers*, 26 May 2026.**
PDF committed at `References/Flashjet/2605.26821-PLuM-particle-lund-multimodality.pdf`.

Closest published work to this study. Same baseline (ParT), same dataset (JetClass),
same question: does explicit clustering-hierarchy information add anything to a
transformer that already sees all particles and their pairwise relations?

## The headline: their C/A ablation is our result

> "Using splittings from clustering with the **CA algorithm did not result in a
> measurable performance increase** compared to the ParT algorithm."
> — §V Ablation studies

That is an independent null on C/A clustering-history features added to ParT, on
JetClass, from a group training **ten seeds per configuration**. Our CA5 arm reaches
the same conclusion at 980k iterations. **Our negative result is corroborated, not
scooped** — see [[2026-09-04-subjet-verdict]].

Their gains come **only from kT-ordered declustering**. The variables are the same
three we use ({log kT, log ΔR, log z}); the *ordering* and the *representation* differ.

## What they did differently — three axes, in order of likely importance

**1. Tokens, not per-particle features.** They add up to **48 splitting tokens** per
jet, embedded 3→64→256→128 by a small MLP, concatenated to the 128 particle tokens
and processed by one unified transformer with full cross-attention. We attach 5
numbers to each *particle*, at that particle's first branch point. A splitting is a
property of a subtree, not of a particle — flattening it onto leaves is lossy in a
way adding tokens is not. **This is the most plausible reason the same variables
behaved differently.** Params 2.14M → 2.19M (a genuinely cheap addition).

**2. Binary classification, not 10-class.** Line-level detail from the PDF: *"ten
copies are trained for 50 epochs in **binary classification mode**"*, 8M signal + 8M
background per epoch, tested on 2M+2M. Ours is the full 10-class JetClass problem on
20M test jets. A binary H→bb-vs-QCD tagger can spend its whole capacity on
b-fragmentation; a 10-class model cannot. **Their setup is the one most favourable to
a flavour-specific feature.**

**3. Ten seeds, we have one.** They resolve effects at a scale we cannot.

## Their numbers (Table I)

"Average performance for the **five best models**" — a selected top-5-of-10 subsample.

| task | metric | ParT | PLuM | ratio |
|---|---|---|---|---|
| H→bb vs QCD | Rej @ 50% | 5864 | 6567 | 1.120 |
| H→bb vs QCD | Rej @ 90% | 386 | 398 | 1.031 |
| t→bqq vs QCD | Rej @ 50% | 13422 | 14388 | 1.072 |
| t→bqq vs QCD | Rej @ 90% | 331 | 353 | 1.066 |

**No per-seed spread, standard deviation, or uncertainty is quoted anywhere in the
paper.** They assert the gain "persists well beyond the observed variation across
repeated seeds" but do not show it. For a +12% claim on rejection at 50% efficiency —
a tail-sensitive quantity — that omission matters. Compare our own tail-limit
finding in [[2026-09-06-logit-discriminant-bug]].

**The 25% headline is compounded, not measured.** From the text: the H→bb gain is up
to 16%, then *"a (1.12)² ∼25% higher background rejection could be achieved in
boosted di-Higgs(4b) searches"*. It squares the per-jet gain for a two-jet final
state, uses 1.12 (not 1.16), and assumes independence. **Quote 6567/5864 from Table I,
never the 25%.**

## Where they get nothing

**No measurable benefit for H→cc or H→4q** — "comparable to or slightly below the
baseline". Only two of JetClass's classes appear in Table I at all.

Their own explanation is *flavour lifetime*, not hierarchy:

> "For H→cc̄ jets, the fragmentation and displaced heavy-hadron decays on the
> soft/wide-angle region of the Lund plane is substantially less pronounced than in
> H→bb̄, as charm hadrons exhibit decay lengths roughly a factor of two to three
> shorter than those of B hadrons"

And the limitation they concede:

> "This was not checked because of the absence of reliable **secondary vertex
> features** in the fast simulation framework used in this study."

**Reading (ours, not their claim):** in a Delphes setup lacking SV inputs, the kT-Lund
representation is acting as a *proxy for b-lifetime* rather than delivering branching
hierarchy. With real SV features — which every experiment's tagger has — the gain
should shrink. This is inference; flag it as such when presenting.

## What supports the arity argument

Their attention analysis finds the flow is **asymmetric** — splitting tokens attend to
particles, not the reverse — and they conclude:

> "the hierarchical branching structure is already implicitly encoded in the particle
> embeddings through self-attention."

That is our redundancy claim, stated by the authors of the paper reporting a gain.
It sits in visible tension with their own Table I; the SV-proxy reading above is the
most natural resolution.

Also: their 96-splitting ablation gave no further gain over 48, and 8 attention heads
were used throughout.

## Our standing result, for contrast

In-domain @980k, 20,046,720 test jets, 10-class:

| | baseline | CA5 | subjet |
|---|---|---|---|
| accuracy | **86.211** | 86.156 | 86.190 |

Ordering **baseline ≥ subjet ≥ CA5** across accuracy, AUC, and rejection at 50%/70%.
Training-paired: CA5 −0.041 at 800k+ (t = −4.65); subjet +0.007 (t = +0.34, a clean null).

## Talk framing

> A concurrent paper (Gouskos & Maier, arXiv:2605.26821) adds Lund splittings to ParT
> as separate tokens and reports gains on H→bb and top — but **explicitly finds no
> measurable gain from C/A-ordered splittings**, matching our null on C/A features.
> Their improvement is confined to heavy-flavour channels (none for H→cc or H→4q),
> obtained in binary mode, and attributed to displaced-hadron decay patterns in a
> fast simulation **without secondary-vertex inputs**. Consistent with the arity
> argument: 2-body Lund coordinates are redundant with ParT's pairwise attention
> bias; what remains is flavour-lifetime information, not clustering hierarchy.

## Open

The **subjet arm is the untested n-body question** neither paper addresses. A subjet
mass is a sum over a set the model must first identify — not computable by PairEmbed
*or* by 2-body Lund tokens. See [[2026-09-04-subjet-verdict]].

Reproduction of PLuM's setup is tracked separately in
[[2026-09-07-plum-reproduction-plan]].
