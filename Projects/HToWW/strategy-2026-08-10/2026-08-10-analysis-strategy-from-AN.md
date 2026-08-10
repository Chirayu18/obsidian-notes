---
tags: [reference]
status: active
date: 2026-08-10
source: lxplus
---

# End-to-end analysis strategy, grounded in AN-23-102

Reference: `References/HToWW/AN-23-102.pdf`. Section/table/line numbers below are from that
note (pdftotext -layout). Measurements are 2022postEE, pooled MC 4,046,127 events,
raw/unweighted, from [[2026-08-07-v11-argmax-implicit-cuts]] and this session.

**Scope caveat.** The AN's expected limits (431 for 1POI, 969 for 2POI, line 669) are
**full Run 2**. Ours (1164 full / 676 stat-only) are **2022postEE only**. These are not
comparable — do not benchmark against 431.

---

## 1. Preselection

**AN (lines 322–330, Table 11 line ~1358).** Trigger + exactly one electron + one muon +
MET > 45 GeV + ≥1 c-jet. Then a dilepton block common to *all* regions: mℓℓ > 12 GeV,
pTℓℓ > 30 GeV, ΔR(ℓ1,ℓ2) > 0.4, opposite charge. Region-defining cuts (mT, mℓℓ ≤/> 72)
are applied **after**, as Table 11 columns — not as preselection.

**Recommendation: keep the base selection loose. Do NOT fold the mT/mℓℓ cuts into it.**

Two measurements say why:

- **The MVA has already internalised the SR wall.** argmax=signal rate is **0.0098%**
  below the mTll cut vs **11.36%** above — a 1,160× step — despite `mtll` not being an
  input feature. The cut adds nothing the classifier isn't already doing.
- **`mll ≤ 72` in the base selection empties the high-mll CR by construction.** That CR
  holds 2.38M events at 83.0% tt purity. Verified in `hww_2dcat_nocjet_kin`.

The AN's own layering agrees: the kinematic cuts belong at region level, not preselection.

## 2. Region definition — argmax vs cut-based

**AN (Table 11).** SR: ≥1 c-jet, mTl2>30, mTll>60, mℓℓ≤72, further **split Nc-j=1 /
Nc-j>1 for +8% sensitivity** (lines 337–338). Top CR: **≥2 c-jet**, mTl2>30, mTll≤60.
High-mℓℓ CR: ≥1 c-jet, mℓℓ>72, built so "contributions from both Higgs-Bkg and H+c are
negligible" (line 335).

**Measured comparison of tt-CR definitions:**

| definition | N | tt purity | signal contam. |
|---|---:|---:|---:|
| **argmax == tt, no kinematic cuts** | **1,565,461** | **87.86%** | **0.0004%** |
| mTl2>30 & mTll≤60 (AN-style, no ≥2cj) | 565,368 | 78.10% | 0.0142% |
| mll>72 | 2,375,781 | 83.04% | 0.0009% |

**The argmax CR is purer, 2.8× larger, and 35× cleaner in signal contamination.** That is
a genuine advantage over the cut-based region and worth keeping.

**What the argmax approach loses — state this explicitly:**

1. **Systematic-shift stability.** A cut-based region moves only events straddling the
   boundary under a JES/JER shift. An argmax region is defined by *which class wins*, so a
   shift that perturbs inputs can flip the winning class for many events at once, moving
   them between all six channels. This is not hypothetical — see the unresolved bug in §6.
2. **Auditability.** "≥2 c-jets, mTll≤60" is trivial to defend to conveners. "argmax of a
   6-class network" requires showing the composition table every time, and **any retraining
   silently redefines every region**.
3. **Disjointness is inherited, but by a different mechanism.** AN v4 (changelog line 40)
   explicitly "removed the overlap with the signal regions". Argmax regions are disjoint by
   construction (one winner per event) — same property, different route. Worth saying so.

**Not implemented from the AN: the Nc-j=1 / Nc-j>1 SR split, worth +8%.**

## 3. Fit variable

**AN (lines 662–665).** Top CR: **yield only**, deliberately. High-mℓℓ CR: BDT(H+c,Bkg-H)
shape. SR: BDT (1POI) or k-means 1D clustering (2POI).

The yield-only choice matters. §7.2.1 (lines 636–645) documents that JES and
MET-unclustered shape variations induce bin migrations that "lead to severe artificial
constraints on the respective nuisance parameters". A 10-bin shape fit in a 87.9%-pure,
1.56M-event tt CR is exactly that failure mode.

**Recommendation for the six channels:**

| channel | now | recommended |
|---|---|---|
| `SR_hplusc` | 10-bin shape | keep — this is the measurement |
| `CR_higgsbkg` | 10-bin shape | keep — plays the high-mℓℓ CR role |
| **`CR_tt`** | 10-bin shape | **yield-only / single bin** (AN line 662) |
| `CR_st`, `CR_diboson`, `CR_vjets` | 10-bin shape | no AN analogue — check purity, likely coarsen |

## 4. Background treatment

**AN §6 (lines 494–507).** Single top, diboson, Z+jets, W+jets normalisations from MC. **tt
is the only data-driven normalisation**, via an unconstrained `rateParam` fitted
simultaneously across SR+CRs. Our `rate_params: [tt]` matches exactly — keep it.

**Split `higgsbkg` by jet flavour.** AN v10 changelog (lines 66–69) splits `bkg-H` into
`bkg-H+c` / `bkg-H+notc` **"due to shape differences"**, and this split is the prerequisite
for the 2POI fit where `r_bkg-H+c` floats freely.

Measured charm fractions (`cjet_cand_flavour`, already in the parquets — no reprocessing
needed):

| sample | light (0) | charm (4) | bottom (5) |
|---|---:|---:|---:|
| ggH | 83.3% | **14.6%** | 2.1% |
| VBF | 67.4% | **31.1%** | 1.5% |

Our current `higgsbkg` merges H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB into **one**
process spanning ~15–31% charm content. The split buys three things: correctly-scoped
flavour uncertainty (§5), a path to the 2POI fit, and removal of an averaging artifact
that forces one shape onto components the AN shows are distinguishable (Fig. 32).

**On ggH as a control region — no.** A CR requires the process enhanced *and* signal
negligible. ggH is shape-degenerate with H+c (same H→WW decay, differing only in
associated jet flavour), so no such corner exists. The AN's answer is the flavour split
plus a 50% normalisation uncertainty — price the ignorance rather than constrain it.

## 5. Systematics — AN Table 16 (line ~3165) mapped to our card

**Theoretical:** H+c PDF 6% · H+c flavour scheme 30% · **ggH+heavy-flavour 50%** · Higgs
production 1–5% · BR(H→WW) 1% · BR(H→ττ) 1% · Z+jets 2.7% · diboson 3.7% · single top
+1.67/−1.27% · αS+PDF 1–3% · top-pT reweight (shape) · UE&PS (shape) · renorm/fact (shape)

**Experimental:** luminosity (partial corr) · MC stat · L1 prefire (2016/17 only, **not**
2018) · pileup · **HLT efficiencies** · electron ID/Reco · muon ID/ISO/Reco · JES/JER
(partial corr) · **MET unclustered** · **PU Jet ID** · charm tagging (partial corr)

**Gaps against our card — verified in `hww_combine_2dcat.yaml`:**

| AN item | our status |
|---|---|
| **HLT efficiencies** | **`trigger: false` for muons; no electron trigger line.** Trigger SFs are *structurally disabled*, not merely missing a nuisance — a weighting-correctness gap, not bookkeeping. |
| **MET unclustered energy** | **absent** — zero mentions in the yaml |
| **PU Jet ID** | **absent** — zero mentions in the yaml |
| ggH+HF 50% | present but **mis-scoped**: `flavor_composition_ggH: 1.40` sits on the *whole merged* higgsbkg, not on ggH alone. Fixed by the §4 split. |
| JES/JER | collapsed to single `Total`; AN uses **RegroupedV2, 11 sources** (§7.2 lines 596–601) |
| charm tagging | single `CMS_ctag2d_2022` up_Total/down_Total; AN decomposes into Stat/PU/PS/scale/XSec/JES/JER/Interp/Extrap. Deliberate deferral — see [[hww-ctag2d-sf-total-decision]]. |
| L1 prefire | absent; AN applies it only to 2016/17, so plausibly a non-issue for 2022 — but should be a *documented* decision |
| top-pT reweight | not itemised; AN applies to the tt sample only (line 566) |

**Which regions constrain what.** §7.2.1 (lines 636–645): JES/JER and MET-unclustered get
"largely constrained" in the Asimov fit through **bin migration** — an artifact, not
physics — which is why AN v8 (changelog line 55) added smoothing. Separately, tt UE&PS FSR
is constrained by **limited MC statistics**, a different failure mode that smoothing does
*not* fix.

**On `no_theory: [tt]`.** AN v6 (changelog line 44) removed tt theory uncertainties
"since we take the normalization from data" — the rateParam absorbs the normalisation
effect. Our card applies `no_theory: [tt]` to all of ps_isr/ps_fsr/scalevar_*, i.e. shapes
too. The AN does not state this distinction, so treat it as an open decision rather than a
confirmed match.

## 6. Prioritised actions

**1. Diagnose the JES/JER merged-group bug.** *(blocks everything shape-related)*
Systematics inflate the limit 1.7× (1164 full vs 676 stat-only), and this sits in exactly
that machinery. Signature: vjets 1507.7→437 and higgsbkg 131→1.4 for **both** Up and Down
(same sign — impossible for a ±1σ scale shift), while tt and st move a physical ±1.5% and
diboson is **frozen identical to nominal**. The two broken processes are the two *merged
groups*; the healthy ones are single-sample. Strongly suggests constituent datasets missing
their varied trees, so the varied template sums over a subset. **Now testable — 
`hww_combine_2dcat` reached 506/506.** Note the earlier "incomplete `hww_combine_fixed`
tree" theory is dead: that tree was complete.

**2. Split `higgsbkg` to isolate the charm component.** Retires the known-wrong 1.40
placeholder, enables the 2POI fit, removes the shape-averaging artifact.
`cjet_cand_flavour` is already in the parquets — config change, no reprocessing.

**3. Make `CR_tt` yield-only.** AN precedent (line 662), our own purity measurement
(87.9%, 1.56M events) says there's no useful shape there, and it removes a prime source of
the §7.2.1 artificial-constraint pathology. Low effort, low risk.

**4. Close the real experimental gaps.** Enable trigger SFs (currently *disabled*, a
correctness issue), add MET-unclustered and PU-Jet-ID nuisances.

**5. Then apply smoothing.** AN v8 added it specifically to counter migration-induced
constraints. Doing it before action 1 would smooth over a bug rather than a genuine effect.

**6. Do not adopt the 2D-ctag-category variant yet.** It gives a *worse* full limit (1676
vs 1164) despite a *better* stat-only limit (637 vs 676) — it buys separation at the cost
of amplifying systematics that are currently broken (1) and incomplete (4). Revisit after
those are fixed.

## 7. On loosening the charm WP — measured, and the answer is no

| medium → loose | signal | ggH |
|---|---:|---:|
| postEE (offline, untagged tree) | 1.64× | — |
| preEE (`hww_ctag_compare`, processor-level) | 1.64× | **2.67×** |

ggH grows **1.63× faster than signal**, so loosening *erodes* the H+c/ggH enrichment the
charm tag exists to provide (1.46× at medium, heading toward ~0.9×). Two independent eras
and two independent code paths agree on the signal ratio to ~1%.

The kinematic cuts are worth 1.63× on S/√B but empty the CRs. The loose WP recovers 1.64×
signal but inflates the degenerate background. **Neither lever is free.**

## Where the AN is silent

- No per-process scoping for UE&PS / scale shapes beyond top-pT reweight → tt only (line 566).
- **No argmax-style region definition is evaluated at all** — its regions are 100%
  cut-based, so there is no AN baseline for our JES/JER migration exposure.
- Its W+jets smoothing fix (§6.1, lines 515–526) relies on **cross-era averaging** we don't
  have in a single-era setup.
