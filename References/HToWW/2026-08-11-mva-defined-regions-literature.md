---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# Published precedent for MVA-defined signal AND control regions

Literature search for analyses that use a **multiclass** classifier's `argmax` (the
highest-scoring output node) to define *both* the signal region and the control regions,
then fit them simultaneously — i.e. the method used in `hww_combine_2dcat`.

This matters because §2 of [[2026-08-10-analysis-strategy-from-AN]] flagged auditability as
a weakness of the argmax approach ("requires showing the composition table every time"), and
noted that **AN-23-102 evaluates no argmax-style region definition at all**, leaving us
without an internal baseline. The papers below are that missing baseline.

> **Read this first:** the single closest reference — **HIG-24-018** — was **already in the
> vault** ([[papers]] lists it as "the argmax-channelization (SR + CRs) strategy our combine
> pipeline mirrors"). §0 below documents what it actually says, which is more specific and
> more useful than any of the external papers. §§1–3 are the external search results, kept
> because they add a published/peer-reviewed citation, a 2025 example, and a direct
> commentary on our c-tagging choice.

> **Era caveat.** §§0–3 are all **Run 2** (13 TeV, 137–138 fb⁻¹). Ours is **Run 3**
> (13.6 TeV, 2022–2023). **§4 is the closest Run 3 analogue** — same era, same
> argmax-defined SR+CR construction, and a WW final state.

---

## 0. CMS HIG-24-018 — already in the vault, and the closest match by far ⭐⭐

**`References/HToWW/HIG-24-018-paper-v15.pdf`** — *Simultaneous probe of the charm and
bottom quark Yukawa couplings using ttH events*, CMS, 138 fb⁻¹ (draft dated 2026/01/05).

This matches our setup on **three** axes at once — argmax regions, the 2D c-tag category
scheme, and a c-vs-b Yukawa target.

### It uses argmax for the CRs, explicitly (p.~13, lines 572–578)

> "Events with 0.6 < D_ttX < 0.85 are **categorized into one of the five CRs, determined by
> the background class with the highest weighted score.** The weights — 100, 12, 4, 2 and 1
> for D_tt+light, D_tt+c, D_tt+≥2c, D_tt+b, D_tt+≥2b, respectively — **are optimized to
> enhance the purity of each CR.**"

**This is the key technique we are missing.** They do *not* use a plain argmax for the CRs —
they use a **weighted argmax**, with per-class weights spanning two orders of magnitude,
tuned to maximise CR purity. Rare-but-important classes get boosted so they are not
swamped by the dominant one.

Directly applicable to us: our `CR_vjets` and `CR_diboson` are the sparse channels driving
the MC-stat penalty ([[2026-08-11-route-to-a-better-limit]]). A weighted argmax would let us
tune what lands in each CR without touching the training. **This is a config-level lever we
have not tried, with published CMS precedent.**

### The event classifier

Multiclass **PART** (Particle Transformer), classifying **directly from final-state objects**
(jets, leptons, MET) with no top/Higgs reconstruction. 10 classes in 0L, 9 in 1L/2L:

- 2 ttH classes: H→cc, H→bb
- 2 ttZ classes: Z→cc, Z→bb
- **5 tt+jets classes: tt+b, tt+≥2b, tt+c, tt+≥2c, tt+light**
- (0L only) QCD multijet

Note the shape of it: **five of the nine/ten classes are backgrounds**, each becoming its own
CR. Same philosophy as our 6-class `[hplusc, higgsbkg, tt, st, diboson, vjets]`.

### It uses the SAME 2D c-tag category scheme we do (p.3, lines 93–95)

> "Two discriminants are constructed from the PARTICLE NET outputs: **p_B+C**, which
> differentiates heavy-flavor from light jets, and **p_BvsC**, which distinguishes b from c
> jets. Based on these, **11 mutually exclusive tagging categories** are defined…"

and the classifier consumes them as booleans (lines 115–116):

> "Jet flavor is encoded via **10 boolean values corresponding to the tagging categories
> B0–B4 and C0–C4.**"

That is our `CTag2DCorrector` scheme and our 11 one-hot inputs
(`cjet_cand_ctag2d_{L0,C0–C4,B0–B4}`) — same construction, same names.

**This settles the concern raised in §3 below.** CMS's cH→γγ analysis deliberately kept
c-tagging *out* of its BDT training; HIG-24-018 feeds the tagging categories *into* the
classifier as one-hots, exactly as we do. So our choice has direct CMS precedent — cite this
paper, not the γγ one, when defending it.

### Region structure and fit

- **4 SRs** at `D_ttX > 0.85`, split by (D_ttH vs D_ttZ) × (D_X→cc vs D_X→bb)
- **5 CRs** at `0.6 < D_ttX < 0.85`, by weighted argmax over the background classes
- **A signal-depleted sideband** at `0.4 < D_ttX < 0.6` with an analogous SR/CR structure,
  "used to validate the background estimation strategy"
- **Fitted variable:** "the PART classifier discriminant for each category" — a *shape* fit
  per category, like ours
- Purity is further enhanced with **heavy-flavour multiplicity requirements** (≥3 b jets in
  b-enriched regions, ≥2 c jets in c-enriched ones)

Two more things we do not do: a **sideband region purely for validation**, and a
**hierarchical cut on the summed discriminant** (`D_ttX`) *before* the argmax, which is what
creates the clean SR/CR/sideband layering.

### What to take from HIG-24-018

1. **Weighted argmax for CR assignment** — the single most actionable idea; tunable purity
   with no retraining.
2. **A validation sideband** between the CRs and the noise.
3. **Our c-tag-in-training choice is CMS-endorsed**, contra the γγ analysis.
4. **Precedent for a shape fit in every category**, which is what we already do.

---

## 1. CMS ttH/tH multilepton — the closest methodological match ⭐

**arXiv:2011.03652** — *Measurement of the ttH and tH production rates in the H→WW, H→ττ
and H→ZZ decay channels*, CMS, 137 fb⁻¹.

This is the **strongest precedent**: it does exactly what we do, and it is a published,
peer-reviewed CMS result in a **H→WW** decay channel.

**Relevant sections:** §6 (ANN training, ~p.17), §7.3 (control regions, p.24), §7.4 / §8
(ML fit and unconstrained rates).

### The argmax construction — quoted verbatim (§6)

> "The events selected in the 2ℓSS + 0τh channel (3ℓ + 0τh and 2ℓSS + 1τh channels) are
> classified into four (three) categories, corresponding to the ttH signal, tH signal, ttW
> background, or other background … **according to the output node that has the highest
> such probability value.** We refer to these categories as **ANN output node categories**."

> "The four (three) distributions of the probability values of the output nodes … are used
> as input to the ML fit. **Events are prevented from entering more than one of these
> distributions by assigning each event only to the distribution corresponding to the output
> node that has the highest activation value.**"

Point-by-point against our setup:

| | ttH multilepton (2011.03652) | our `hww_combine_2dcat` |
|---|---|---|
| classifier | multiclass ANN, softmax | multiclass MLP, softmax |
| nodes | 4: ttH, tH, **ttW bkg**, other bkg | 6: hplusc, higgsbkg, tt, st, diboson, vjets |
| region definition | **argmax over output nodes** | **argmax over output nodes** |
| disjointness | explicit, by construction | explicit, by construction |
| background nodes | **are themselves fit categories** | **are themselves fit categories** |
| fitted variable | the output-node **probability distribution** | 10-bin discriminant shape |
| bkg normalisation | ttW and ttZ rates **left unconstrained** | `rate_params: [tt]` |

> "**The rates of the ttW and ttZ backgrounds are separately left unconstrained in the
> fit.**" (§7.4)

So the "let the network define a background-enriched category and float that background's
rate in the same fit" pattern is *established CMS practice*, not something we invented.

### One thing they do that we do not

Their fit **also receives two dedicated cut-based CRs** (§7.3, for ttZ/WZ and for ZZ), on top
of the ten channels and their ANN node categories — see their Fig. 3 caption:

> "In addition to the ten channels, the ML fit receives input from two control regions (CRs)
> defined in Section 7.3."

**They use argmax categories *and* conventional CRs together.** Our six-channel setup is
purely argmax. Worth considering as a defensive addition, and it directly answers the
auditability objection: a conventional CR gives conveners a region they can check by hand.

### Also relevant: they subdivide by jet/flavour multiplicity

The 2ℓSS+0τh and 3ℓ+0τh channels are further split by lepton flavour and by **b-tagged jet
multiplicity** — the same idea as the AN's Nc-j=1/Nc-j>1 split, which we found is currently
blocked by V+jets MC statistics ([[2026-08-11-route-to-a-better-limit]]).

---

## 2. CMS tZq / tWZ / ttZ trilepton — argmax stated compactly

**arXiv:2501.06070** (2025) — three-lepton final state, simultaneous tZq + ttZ measurement.

> "The output score is normalized such that for each event their sum gives unity."
> "**For use in a signal extraction fit each event is then assigned to a category, in which
> it has the highest output score.**"

Three nodes: **ttZ+tWZ**, **tZq**, **background**. The categories serve as signal *and*
constraining regions in one profile-likelihood fit with two POIs, supplemented by a
four-lepton category (ttZ-enriched) and a **b-jet veto region** (WZ-enriched).

Useful as a **recent (2025)** citation showing the method is current practice, and as
precedent for a **2-POI** fit — which is where the AN's `bkg-H+c` / `bkg-H+notc` split is
heading (§4 of the strategy note).

---

## 3. CMS cH → γγ — same physics problem, *different* solution ⚠️

**arXiv:2503.08797** — *Search for a cH signal in the associated production of at least one
charm quark with a Higgs boson in the diphoton decay channel*, CMS, 138 fb⁻¹.

Not an argmax analysis, but the **closest published analogue to our physics**: charm-associated
Higgs production, with **ggH as the dominant degenerate background**. Their choices are a
direct commentary on ours.

**Relevant sections:** §4 (c tagging, p.5), §6 (event categorization, p.6).

### They use two *binary* BDTs, not one multiclass

- **BDT1**: cH vs **ggH** — the resonant background, ">60% of the resonant background"
- **BDT2**: cH vs continuum background

That is a deliberate architectural choice: rather than one network separating everything,
they built a dedicated classifier for the degenerate competitor. Given that our
`hplusc`-vs-`higgsbkg` separation is the weak axis (AUC 0.731 on CvL), this is worth weighing.

### The critical design decision — they deliberately EXCLUDE c-tagging from the training

> "**The BDT trainings avoid using c tagging information, so that the event yield ratio
> between ggH+c jet and ggH+(u, d, s, g) jet is not strongly correlated with the BDT outputs
> and hence the heavy flavor (HF) modeling uncertainty can be applied on the overall
> normalization of ggH.** The use of tagging information in training classifiers can be
> further explored in future analyses."

**This is opposed to our design — but it is NOT the CMS consensus.** Our v11 2dcats model
takes **11 one-hot c-tag category features** (`cjet_cand_ctag2d_{L0,C0–C4,B0–B4}`) as inputs.
This γγ analysis avoided exactly that, so the ggH heavy-flavour uncertainty could stay a
clean overall normalisation.

**However, HIG-24-018 (§0) does what we do** — it feeds the B0–B4/C0–C4 tagging categories
into the PART classifier as 10 booleans. So the two CMS analyses disagree, and we are aligned
with the more recent and more closely-matched one. Their own sentence — "The use of tagging
information in training classifiers **can be further explored in future analyses**" — reads
as an acknowledgement that theirs was the conservative choice.

The real consequence for us is narrower: because our discriminant *is* correlated with c-tag
content, the 50% ggH+HF uncertainty is **shape-correlated** rather than a pure normalisation.
That is a modelling detail to handle properly (it is a sharper version of the mis-scoping we
measured — `flavor_composition_ggH` applied to the whole merged `higgsbkg`, worth 21 units,
see [[2026-08-11-route-to-a-better-limit]]), **not** a reason to change the training.

### Their c-tagging working point

> "The chosen working point has a typical efficiency for charm jets of ∼30% and a typical
> rejection for light-quark or gluon jets of ∼95%."

And they **drop CvsB entirely**:

> "given that the dominant backgrounds are the continuous background and the ggH process
> (most events of which do not contain bottom quark jets), the CvsB score provides only
> minor improvement in analysis sensitivity and hence is not used."

Compare our own measurements ([[kin-cuts-vs-mva]]): **CvL carries the H+c-vs-ggH separation
(AUC 0.731) while CvB does not (0.551 ≈ coin flip)** — we and CMS independently reached the
same conclusion about CvB. Their ~30% charm efficiency also brackets our medium WP (23.1%),
supporting the decision to keep medium rather than loosen.

---

## 4. CMS HH → bbWW dilepton, **Run 3** — the closest same-era match ⭐

**arXiv:2604.02127** — *Search for Higgs boson pair production in the bbWW decay channel with
two leptons in the final state*, CMS, **√s = 13.6 TeV, 62 fb⁻¹ (2022–2023)**.
Vault copy: `2604.02127-HH-bbWW-Run3-13p6TeV-multiclass.pdf`.

The only **Run 3** analysis found that defines signal *and* control regions by multiclass
argmax. Same era as us, same 13.6 TeV conditions, and a **WW final state with two leptons**.

### The argmax construction (§4, p.8)

> "The values obtained in the output nodes of the NN_cat are normalised to unity using a
> 'soft-max' function … **Events are assigned to the category corresponding to the most
> probable process according to this NN multiclassification.** The events are separated into
> one of two SRs targeting ggF HH production (SR_ggF) or VBF HH production (SR_VBF), **or
> into one of four background CRs targeting the main background processes: tt, single-t/t̄,
> DY, and H production.**"

Two SRs + **four background CRs**, all from one argmax — structurally almost identical to our
`SR_hplusc` + five background CRs.

### The design choice that matters most for us — a *staged* NN, and CRs fit by YIELD

> "The events in the SRs are classified by **additional NNs** designed to separate ggF or VBF
> signal events from background events. **The distributions of the output values of the binary
> NNs in the SRs, together with the event yield in the CRs, enter the final fit** as sensitive
> observables."

Two things we do differently:

1. **Staged classifiers.** A multiclass NN for *categorisation*, then a **separate binary NN**
   for the *discriminant* within each SR. We use one 6-class network for both jobs. Their
   "staged multiclassification-plus-binary NN approach" (line 123) lets each network optimise
   for one task. Note this is also the cH→γγ instinct (§3): a dedicated classifier against the
   degenerate competitor.
2. **CRs enter the fit as YIELD ONLY, not shape.** Exactly the recommendation in §3 of
   [[2026-08-10-analysis-strategy-from-AN]] (make `CR_tt` yield-only, per AN-23-102 line 662)
   — now with **Run 3 precedent** from an argmax-defined CR. We currently fit a 10-bin shape
   in all six channels. Given that our residual same-sign JES/JER flags are channel-migration
   artifacts ([[2026-08-11-jes-jer-bug-fixed]]), moving the CRs to yield-only is well
   supported.

Also: **`tt` and DY normalisations "are determined in the final fit to data"** — the same
floating-rate treatment as our `rate_params: [tt]`, and as ttW/ttZ in §1.

### Other structure worth noting

- SRs further split by jet content: **boosted / 1b / ≥2b** — a multiplicity split like the
  AN's Nc-j idea, but on b-tagged jets.
- Separate **DY and tt validation regions** (Table 1) — a VR distinct from the CRs, echoing
  the validation sideband in HIG-24-018 (§0).
- A **simultaneous binned profile likelihood fit** across all SRs and CRs.

---

## Summary — what to take from this

**The auditability worry in §2 of the strategy note is largely answered.** Argmax-defined
signal *and* control regions are established CMS practice across at least three analyses,
one of them peer-reviewed and in a H→WW decay channel.

Ranked by what we should actually do:

1. **Adopt the weighted argmax for CR assignment** (HIG-24-018). Per-class weights spanning
   100→1, tuned for CR purity. No retraining needed — it is a post-processing rule on scores
   we already have. Most actionable idea found, and it bears directly on our sparse
   `CR_vjets` / `CR_diboson`.
2. **Consider a hierarchical structure**: cut on the *summed* signal-class discriminant first
   (their `D_ttX`), then argmax within. This is what gives them a clean SR / CR / sideband
   layering rather than a flat six-way split.
3. **Add a validation sideband** (HIG-24-018) and/or **one conventional cut-based CR** (ttH
   multilepton uses argmax categories *plus* two hand-built CRs). Cheap insurance for
   conveners.
4. **Our c-tag-in-training choice has direct precedent** — HIG-24-018 encodes the same
   B0–B4/C0–C4 categories as classifier inputs. The γγ analysis chose otherwise and said so
   explicitly; cite HIG-24-018, and be ready to explain that our ggH+HF uncertainty is
   therefore shape-correlated.
5. **Independent support for keeping the medium WP**: the γγ analysis chose ~30% charm
   efficiency and **dropped CvsB entirely** as adding only "minor improvement" — matching our
   own finding that CvL carries the H+c-vs-ggH separation (AUC 0.731) and CvB does not
   (0.551).

6. **Make the CRs yield-only.** arXiv:2604.02127 (§4) fits "the event yield in the CRs" while
   fitting shapes only in the SRs — **Run 3 precedent** for what §3 of the strategy note
   already recommended from AN-23-102. We currently fit a 10-bin shape in all six channels.
7. **Consider staging the classifiers.** Multiclass for *categorisation*, a separate binary NN
   for the *discriminant* inside each SR (§4). Two of the four analyses here converge on a
   dedicated classifier against the degenerate competitor (§3, §4).

**Which to cite for what:**

| need | cite |
|---|---|
| **same era (Run 3, 13.6 TeV)** + argmax SR/CR + WW final state | **arXiv:2604.02127** (§4) |
| method **and** physics — charm Yukawa, 2D c-tag categories, argmax CRs | **HIG-24-018** (§0) |
| a *published, peer-reviewed* argmax reference, in a H→WW channel | **arXiv:2011.03652** (§1) |
| c-tagging WP / CvB choices in charm-Higgs | arXiv:2503.08797 (§3) |

**Era note:** §§0–3 are Run 2 (13 TeV, 137–138 fb⁻¹); only §4 is Run 3. No Run 3 analysis of
*charm-associated* Higgs production in H→WW was found — that space appears to still be open,
which is consistent with AN-23-102 being a full-Run-2 note.

## Sources

- [arXiv:2011.03652](https://arxiv.org/abs/2011.03652) — CMS ttH/tH multilepton (H→WW/ττ/ZZ)
- [arXiv:2501.06070](https://arxiv.org/abs/2501.06070) — CMS tZq/tWZ/ttZ trilepton (2025)
- [arXiv:2503.08797](https://arxiv.org/abs/2503.08797) — CMS cH → γγ, charm-associated Higgs
