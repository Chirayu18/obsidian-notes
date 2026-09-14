---
tags: [reference]
status: active
date: 2026-09-14
source: laptop
---

# Two interpretability papers that explain our PLuM null

Found 2026-09-14 while at ML4Jets. Both from Sanmay Ganguly's group (IIT Kanpur).
Together they give an **independent, citable mechanism** for why all three of our
feature arms came out null — see [[2026-09-11-plum-final-verdict]].

| paper | arXiv | PDF |
|---|---|---|
| Patel & Ganguly, *Explainable AI for Jet Tagging ... in the Lund Jet Plane* | [2604.25885](https://arxiv.org/abs/2604.25885) (28 Apr 2026) | `References/Flashjet/2604.25885-PatelGanguly-XAI-jet-tagging-lund-plane.pdf` |
| Rai & Ganguly, *Dissecting Jet-Tagger Through Mechanistic Interpretability* | [2605.09881](https://arxiv.org/abs/2605.09881) (12 May 2026) | `References/Flashjet/2605.09881-RaiGanguly-dissecting-jet-tagger-mech-interp.pdf` |

Neither proposes an architecture. Neither competes with our study. Both are
**evidence for the arity argument**, arrived at by methods orthogonal to ours.

## Why this matters to us

Our claim has been: PLuM hands ParT a 48-row, $k_T$-ordered subsample of
$\{\ln k_T, \ln z, \ln\Delta\}$, which `pairwise_lv_fts_paper` **already computes for
every particle pair** and injects as a $(B,H,P,P)$ attention bias. Verified in the
code (`utils/models/particletransformer_paper.py:63`). So the tokens are a coarser
copy of an existing channel.

That was our own reading of our own code. These two papers support it from outside.

## Paper 1 (XAI) — attention bias is the effective channel

Applies GNNExplainer / GNNShap / GradCAM to **LundNet, ParticleNet and ParT**, and
correlates explainer node-importance with $\tau_{21}$, $\tau_{32}$, $C_2$, $C_3$.

Their conclusion #3, verbatim:

> "**Attention-based architectures encode substructure observables more directly than
> message-passing GNNs.** The stronger Pearson correlations achieved by the Particle
> Transformer ($|\rho| \approx 0.5$–$0.6$) compared to LundNet and ParticleNet
> ($|\rho| \approx 0.4$) suggest that **pairwise attention biases are particularly
> well-suited for representing $N$-point energy correlation features**."

And the mechanism:

> "attention-based architectures, by allowing every constituent to interact with every
> other, **encode a more direct representation of pairwise kinematic features** ...
> Local message-passing architectures (LundNet, ParticleNet) require multiple layers
> to assemble the same global features."

They also report ParT "approaches functional equivalence with $\tau_{21}$
($|\rho|\approx0.65$)" for $H\to c\bar c$ — reconstructing a classical observable
from four-vectors alone.

**Caveat (they flag it themselves, Limitations #1):** correlations are Pearson, and
$|\rho|\approx0.4$–$0.6$ leaves real unexplained variance. This is *explanation
importance*, not a performance claim. It supports the mechanism; it does not prove
no encoding can help.

## Paper 2 (mech-interp) — the causal version, and one number that is awkward for PLuM

Small ParT (4 layers, 4 heads, 128 embed, ~1.3M params) on Top Quark Tagging.
Zero ablation + path patching + logit lens + linear probes.

**Causal feature ablation (their §8.2)** — zero each pairwise feature at the input to
the pairwise MLP and measure the change in mean logit difference (positive =
degradation):

| feature | effect of zeroing |
|---|---|
| $\ln k_T$ | **+4.44** — the largest, "the most causally important pairwise feature" |
| $\ln z$ | **−2.69** — *the model gets slightly BETTER without it* |

> "A counter-intuitive observation is that zeroing $\ln z$ produces a positive change
> in the mean logit difference (+2.69), meaning that **the model performs slightly
> better when this feature is removed**. ... $\ln z$ ... can drive the attention onto
> soft fragments with high $z$ asymmetry but small absolute momentum scale, and
> removing this input partially suppresses a confounding signal."

**PLuM's tokens are $[\ln k_T, \ln 1/\Delta R, \ln z]$.** One third of what we fed the
model is a feature that is, in the pairwise channel, mildly *harmful*. They explicitly
decline to recommend removing it from the architecture (it feeds the relay heads'
$\ln m^2$ representation), so this is not "drop $\ln z$" — but it is a concrete reason
not to expect a gain from supplying more of it.

**Other findings that bear on us:**

- A **six-head circuit recovers 97.3 % of full-model AUC**. The task is concentrated,
  not spread thin — consistent with a model that has already solved it and has no use
  for redundant input.
- **Linearly accessible class information is already at AUC ≈ 0.97 in the particle
  attention layers**; the class-attention block is "more like a basis rotation" than a
  decision. *This is the same shape as our result*: our CLS attention on Lund tokens
  decays 46 % while encoder self-attention rises — the work happens in the particle
  layers, and CLS reads out. See the attention section of [[2026-09-11-plum-final-verdict]].
- The model **prefers the energy-correlator basis to $N$-subjettiness**, and prefers
  **2-prong observables over 3-prong ones even for top tagging** — it factorizes top
  into "find the hadronic $W$".

## What to take for the deck

1. The arity argument now has **two independent citations**, from a different group
   using different methods (explainability, mechanistic interpretability) on a
   different dataset (Top Quark Tagging).
2. The strongest single line to quote is the XAI conclusion #3 — "pairwise attention
   biases are particularly well-suited" — because it names the channel our features
   were competing with.
3. The $\ln z$ result is a good backup slide if anyone argues we under-engineered the
   PLuM features.

## What this changes about "can we embed Lund info better?"

It **strengthens** the pairwise-bias direction and **weakens** more per-particle or
token encodings:

- The channel that demonstrably works is `PairEmbed`'s $(B,H,P,P)$ bias.
- What `PairEmbed` cannot compute from a pair's kinematics is the pair's **relationship
  in the clustering tree**: $\ln d_{ij}$ at their first common ancestor, the depth of
  that ancestor, whether that merge survives soft drop. Those are reads of
  `hist_p1/hist_p2/hist_child/hist_d` — no reclustering.
- Cost profile is completely unlike PLuM's: `pairwise_lv_dim` 4 → 7 widens a small
  conv, sequence length stays 128, so none of PLuM's 1.58× (which came from 176 vs
  128 tokens).

**Honest risk, now better quantified.** If ParT is already near-functionally-equivalent
to $\tau_{21}$ and a six-head circuit captures 97.3 % of AUC, the headroom for *any*
hand-supplied substructure feature is thin. A null here would be a stronger result than
a gain: it would say **pairwise attention over four-vectors is sufficient for everything
the clustering tree contains**, at 100M jets. Our three arms plus these two papers would
be the evidence.

## Not relevant: the hypergraph work

Checked, since it was asked for. Ganguly's hypergraph paper is
*Reconstructing particles in jets using set transformer and hypergraph prediction
networks* ([2212.01328](https://arxiv.org/abs/2212.01328), EPJC 2023) — **particle-flow
reconstruction** (set-to-set: detector hits → final-state particles), not jet tagging
and not Lund/substructure encoding. Same for the earlier *Secondary vertex finding in
jets with neural networks* (set-to-graph). Neither offers an encoding we can borrow for
the tagger question. The two interpretability papers above are the relevant ones.
