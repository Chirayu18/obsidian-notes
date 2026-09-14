---
tags: [reference, talk]
status: active
date: 2026-09-14
source: laptop
---

# ML4Jets 2026 — Hong, ATLAS 4-prong LundNet tagger

**JaeJin Hong** (Indiana University), on behalf of ATLAS.
*"A machine learning based 4-prong tagger for hadronic decays of highly boosted
WW in ATLAS."* ML4Jets 2026, Vienna, 14 Sep 2026, 14:10, parallel session.

- Indico: https://indico.global/event/15240/contributions/165301/
- Slides committed at `References/Flashjet/ML4Jets2026-Hong-ATLAS-4prong-LundNet-tagger.pdf`
  (19 slides + 4 backup)

Seen live while presenting our own talk at the same workshop. Relevant to us because
it is **LundNet applied at ATLAS**, i.e. the GNN-on-the-declustering-tree branch of
the Lund-feature literature that our PLuM study does *not* cover —
see [[2026-09-07-plum-paper-vs-our-result]].

## What the talk did

**First 4-prong tagger in ATLAS.** Target is $S \to WW \to 4q$ inside a single
large-$R$ ($R=1.0$, anti-$k_t$) jet, using Unified-Flow Objects (calo + tracker) as
constituents. Motivation is BSM searches in a 4-prong topology and the $H$-$VV$
coupling. Extends the existing ATLAS 2-prong (ATL-PHYS-PUB-2023-020) and 3-prong
(JETM-2026-03) constituent-based taggers.

**Architecture: LundNet** (Dreyer & Qu), unchanged in its essentials.
- binary-tree input from the **C/A clustering history**
- **three node features** per splitting — split angle, transverse momentum, momentum
  ratio (the usual $\Delta R$, $k_t$, $z$ triple)
- number of tracks as a **global** feature
- **four output classes**, 1-prong (QCD $q/g$) / 2-prong ($W,Z\to qq$) /
  3-prong (top $\to bqq$) / 4-prong ($S \to WW \to 4q$, on-shell $W$ only)

**Dataset scale: 1M jets per class** — so ~4M jets total.

**Performance.**
- vs $\tau_{43}$ (4-subjettiness ratio): LundNet is **4× better QCD rejection** at
  50 % signal efficiency, $m_S = 300$ GeV.
- rejects QCD and $WZ$ well; **weakest against top** — 3-prong and 4-prong topologies
  look similar and there is **no flavour information** in the three node features.
  The backup confusion matrix shows a high top↔4-prong mis-tag rate.
- mass/$p_T$ **decorrelated by reweighting the training set**, since there is no mass
  constraint on the BSM scalar and a mass-agnostic tagger is wanted.
- the Lund plane's **upper-left region depends on the scalar mass** (125 / 300 / 500
  GeV shown), which is exactly the region the decorrelation has to handle.

## The half worth our attention: per-prong calibration

This is the part that is *not* in the LundNet paper, and it is the more original
contribution of the talk.

**The problem.** There is no SM proxy for a 4-prong jet in data, so $\varepsilon_{\rm data}$
for the tagger cannot be measured the usual way.

**The method** (following CMS PAS JME-23-001, which ATLAS is now also exploring):
subjet Lund jet planes are **approximately identical for all $n$-prong topologies**,
so you can calibrate bottom-up from known topologies.

1. identify subjets inside the large-$R$ jet with **C/A exclusive reclustering**
2. for **each subjet**, build a Lund jet plane, again with C/A
3. take the **subjet Lund-plane density ratio** between two datasets → correction factor
4. multiply the CF in **per C/A split** as a weight

**Proof of concept** is MC2MC on $t\bar t$: apply the Sherpa→PowhegPY8 correction and
compare normalised $\tau_{32}$ and LundNet 3-prong discriminant distributions.
$\chi^2/\rm ndf$ improves 35.6/18 → 12.2/18 and 17.6/12 → 13.0/12.

**Stated open systematics** — both are "is the subjet plane really universal?" checks:
- 2-prong vs 3-prong subjet planes differ; the ratio is much flatter once a
  **subjet $\Delta R$ selection** is applied (so part of the difference is kinematic,
  not topological)
- **flavour dependence**: $b$-subjet vs light-subjet planes ($Zbb/Zqq$) differ at
  **small $\Delta R$**; smaller than the $n$-prong difference, but unresolved.

## Why this matters for flashjet

**1. It is a live, per-split, production-scale consumer of exactly what we emit.**
The calibration multiplies a correction factor **per C/A splitting**, for **every
subjet of every jet**, across full ATLAS MC samples. That is a C/A reclustering plus
a Lund-plane read per subjet — the exact workload
`lund_coordinates_from_history` + exclusive subjets serve, and it is done *twice*
(once per dataset) to form the density ratio. Strong argument that the cost we
removed is a cost someone is actually paying. See [[2026-07-22-full-merge-history]].

**2. It is the architecture arm our null result does not cover.** Our PLuM study says
Lund *variables handed to a transformer as tokens* give no gain at convergence on
JetClass. This talk is Lund structure **as the graph itself**, message-passing on the
declustering tree. Our result says nothing about that, and this is the distinction to
keep making when the null is challenged — the inductive bias, not the variables.

**3. Dataset scale supports the convergence reading.** They train on **1M jets/class**
(~4M). Our arms train on **100M** jets for $10^6$ iterations, and that is precisely
where our early gain (10–25 % at 40k) decays to null. A Lund-feature gain that is real
at few-M scale and gone at 100M is consistent with **both** results —
see [[2026-09-04-ca-1M-verdict-and-pairwise]]. Do not read this talk as contradicting ours.

**4. Their weakness is our CA5 feature's stated strength — and it is still unclaimed.**
Their 3-prong/4-prong confusion is attributed to *no flavour information*. Our AK4
study found C/A branch-point features give **essentially no flavour separation**
(AUC ~0.5–0.55, $b$ vs light) while separating **boosted decay structure** strongly.
So our features would *not* fix their specific problem. Worth being precise about
that rather than offering it.

## Follow-ups

- [ ] Ask how the per-split correction is computed today — FastJet per subjet on CPU?
      If so, get a wall-clock number; that is the concrete adoption case.
- [ ] Check whether CMS PAS JME-23-001 states a timing/throughput cost for the same
      method. If the calibration is the expensive half, that reframes our speed
      argument away from training loops.
- [ ] LundNet at JetClass scale is an open question worth a direct answer — nobody
      seems to have trained it on 100M jets.
