---
tags:
  - reference
status: active
date: 2026-07-11
source: lxplus
pinned: false
---

# Neg-weight reweighting — training region & selection logic

How we chose the **training region** for the negative-weight reweighting fix
(arXiv:2510.16217) and *why*. This is the region on which we learn
`g(x⃗) = 2·P₊(x⃗) − 1`, where `P₊(x⃗) = P(genWeight>0 | gen kinematics x⃗)`.

**Context:** [[2026-06-23-automcstats-rootcause]] (why the fix is needed),
[[ProposedFix-Automcstats]] (fix decision). Full pipeline plan lives outside the
vault at `~/.claude/plans/for-the-fix-of-logical-wadler.md`.

---

## TL;DR — the decision

- **Features `x⃗` = generator/parton-level only** (`lhe_*`, `genparton_*`), NOT reco.
- **Train on a looser region than the SR, but DISJOINT from it by construction:**
  all base cuts + a veto that removes **only the eμ signal-region topology**
  (`veto_emu_sr`). Keeps the no-dilepton-pair bulk + same-flavor (ee/μμ) pairs.
- **Infer** `g(x⃗)` on the tight eμ SR (`hww_combine_fixed`) later.
- Workflow: `analysis/workflows/hww_genrw_train.yaml` (category `train`).

The SR selection (eμ dileptonic + MET≥45 + ≥1 c-jet) starves vjets by ~10⁴×
(N_eff≈10/SR bin — the whole reason autoMCStats blows up). Training there is
impossible. So we train elsewhere and infer on the SR.

---

## Why generator-level features (not the analysis cuts)

`P₊(x⃗)` is a property of the **generator** (the amc@NLO FxFx NLO subtraction),
defined for *every generated event* regardless of which analysis box it lands in.
The paper (§V.2) explicitly rejects reco-level variables:

> *"Using reconstruction-level variables … will not guarantee closure on
> generator-level variables … Including all kinematic information … sampled during
> MC generation should be sufficient."*

Its 56 features (Table 4) are all gen/parton-level: parton pT/η/φ (up to 5),
kT merging scales, PS scales, `numPartons/Pt20/100/200`, `numB/numC`,
incoming-flavor flags. Our YAML dumps the matching set: `lhe_njets/nb/nc/nuds/nglu/
npnlo/ht/htincoming/vpt/alphas`, `genparton_multiplicity/n_pt20/100/200`,
`genparton_incoming1/2_pdgId`, `genparton1/2_pt/eta`, label `genweight_sign`.

**Consequence:** we do NOT apply the SR cuts before training. They would (a) throw
away ~99.99% of vjets and (b) add no gen information the classifier can use. Paper
§V.3 confirms they train on the full generated sample (a flat `event ≡ 1 mod 100`
subset) *before* analysis cuts.

## Why the training region must be event-DISJOINT from the SR

Paper §V.4: the SR evaluation **excludes the events used to train** the reweighting
classifier. If you reweight the same events whose weight-sign the classifier
memorized, `g(x⃗)` is optimistically biased and the measured variance reduction is
partly overfitting, not real. The paper enforces this with the `event mod 100`
hold-out.

**Our design gap it exposed:** naive train-loose / infer-tight is NOT disjoint — a
tight-SR event is a *subset* of a loose-training event (same underlying NanoAOD),
so they overlap. We needed an explicit disjointness mechanism.

## Why DISJOINT EVENTS, but NOT an orthogonal phase space

Two different things, easy to conflate:

| | required? | why |
|---|---|---|
| disjoint **events** | **yes** | else overfitting bias (above) |
| disjoint / orthogonal **phase space** | **NO — harmful** | `g(x⃗)` must be *interpolated* over the SR's x⃗ support, never *extrapolated*. Training in an anti-SR (e.g. c-depleted) region leaves the c-enriched SR corner unlearned → closure fails exactly where it matters |

So the goal is: **same phase space (spanning the SR), disjoint events.**

## The chosen mechanism: veto only the eμ SR topology

The SR requires `one_ll_pair AND one_muon_one_electron` (exactly one eμ pair) + MET≥45
+ ≥1 c-jet. We build the training region by taking the base cuts and vetoing **only**
the exactly-one-eμ-pair topology:

```
train = atleast_one_goodvertex AND lumimask AND met_filters AND trigger AND veto_emu_sr
veto_emu_sr = NOT( (num ll_pair == 1) AND (that pair is eμ) )
```

This gives, all at once:
- **Disjointness by construction** — an event that is not "exactly-one-eμ-pair"
  can never be an eμ SR event. No event-id bookkeeping needed.
- **Coverage of the SR's hard tail** — keeps the huge **no-dilepton-pair** population
  (≈88% of events have ≤1 lepton), which carries the hard Vpt/HT/parton-pT tail the
  SR probes. Also keeps **same-flavor (ee/μμ)** pairs (DY-rich).
- **Kinematic proximity** — lepton flavor (an EW decay choice) is ~orthogonal to the
  gen-parton `x⃗` that drives the negative weights, so the surviving region's x⃗
  distribution matches the eμ SR.

### Alternatives we rejected (and why)

- **Invert `met_45` (low-MET sideband)** — disjoint, but data-verified **kinematically
  softer** than the SR: `lhe_vpt` 20 vs 28, `lhe_ht` 32 vs 42, `genparton1_pt` 48 vs 59
  (MET<45 vs ≥45). Under-covers the SR hard tail → extrapolation. Rejected.
- **Invert `atleast_one_cjet` (c-depleted)** — the trap: flips into the *opposite* of the
  SR's c-enriched gen corner. Extrapolation where it matters most. Rejected.
- **Blind `event mod N` k-fold (paper's exact method)** — valid, but the veto scheme is
  more physically interpretable and keeps identical reco cuts. Kept as fallback.

---

## Selection coverage vs the SR (from the 2022postEE cutflow)

Why the SR itself is untrainable — vjets collapse across the SR cuts
([[2026-07-07-cutflow-2022postEE]], weighted events):

| cut | V+Jets | DY+Jets |
|---|---:|---:|
| trigger | 3.84e8 | 6.45e7 |
| + met_45 | 1.45e8 | 8.63e6 |
| + one_ll_pair | **2.06e4** | 9.01e5 |
| + one_mu_one_e | **1.09e4** | 1.21e4 |

V+Jets: 3.8e8 → ~1e4 (~35,000×). The `train` region sits at the **trigger** level
(minus the eμ sliver) — full stats, spanning x⃗.

---

## Verified numbers (small test run, 4 chunks of one WtoLNu file)

- **Efficiency ≈ 22.7%** raw (18,130 rows / 80,000 entries).
- Veto integrity: **0 eμ pairs leaked**; 18,128 no-pair + 2 same-flavor.
- Gen features clean & physical: `lhe_vpt` mean 23 (p95 89, **max 914** → hard tail
  present), `lhe_nc≥1` = 8.5% (the c-enriched corner), `frac(genWeight>0)` = 0.846.

**Production estimate** (3 vjets datasets, ~600M raw across 989 files):

| scope | raw in | training rows (~22.7%) | c-enriched (~8.5%) |
|---|---:|---:|---:|
| ~35 files | ~23M | ~5M | ~430k |
| ~160 files | ~105M | ~24M | ~2M |
| full 989 | ~600M | ~136M (overkill) | ~12M |

~5M rows is ample for a 20× classifier ensemble; full production is unnecessary.

---

## The veto bug we hit (documented so it never recurs)

`select_hww_ll_pair` (`analysis/selections/object_selections.py:519`) uses
**`ak.mask`**, so events with <2 leptons get `ll_pair = None` (option-type/masked),
**NOT** an empty list `[]`. Then `ak.num(None) == 1` → `None`, and the selection
manager treats `None` as **False** → a naive veto **drops every pairless event**
(~1000× over-veto; efficiency 22.7% → 0.009%, 18k rows → 7).

**Fix:** wrap the full eμ mask in `ak.fill_none(..., False)` *before* negating, so
pairless/same-flavor → not-SR → survive:

```python
veto_emu_sr: ~ak.fill_none(
    (ak.num(objects['ll_pair']) == 1) &
    ak.firsts(  # eμ test on the (masked) pair
        ((abs(objects['ll_pair'].l1.pdgId)==11) & (abs(objects['ll_pair'].l2.pdgId)==13)) |
        ((abs(objects['ll_pair'].l1.pdgId)==13) & (abs(objects['ll_pair'].l2.pdgId)==11))
    ), False)
```

Unit-tested on `[no-lep, eμ-pair, same-flavor-pair, single-lep]` →
`[keep, veto, keep, keep]`. General lesson: **any selection touching `ll_pair`
must be None-safe**, because pairless events are masked, not empty.

---

## Training-parquet stripping (gen-level classifier only)

The classifier only needs gen features + `sign(genWeight)`, so for the `train`
workflow we stripped everything else:
- `object_shifts: false` — reco shifts duplicate gen features + label.
- `add_syst_axis: false` — no systematics needed.
- `event_weights: {genWeight}` only — dropped pileup/PS/PDF/scale/nnlops + lepton-SF.
- Added `lepton1/2_pdgId` axes so the coverage check can split eμ vs same-flavor.

The reco/jet-topology axes are `None`-filled for no-pair events (harmless — the
writer's `ak.firsts` yields None per missing object), so they don't drop rows; but
they're irrelevant to training and could be pruned in a later cleanup.

---

## Next step

Phase-1 production: submit the `hww_genrw_train` Condor jobs over ~35 files across the
3 vjets datasets (`DYto2L_2Jets_50`, `_10to50`, `WtoLNu_2Jets`) → ~5M rows, then run
the **coverage check** (training `x⃗` vs eμ-SR `x⃗` on `lhe_vpt`/`ht`/`nc≥1`) before
Phase-2 classifier training.

Related: [[2026-06-23-automcstats-rootcause]] · [[ProposedFix-Automcstats]] ·
[[2026-07-07-cutflow-2022postEE]] · [[Analysis QUICKSTART]]
