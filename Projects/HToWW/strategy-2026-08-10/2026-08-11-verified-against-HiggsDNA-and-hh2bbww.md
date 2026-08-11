---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# Systematics verified against HiggsDNA and hh2bbww

Two external references checked:

- **HiggsDNA** — `gitlab.cern.ch/cms-analysis/general/HiggsDNA`, `higgs_dna/systematics/`.
  Already the cited source for our `partonshower.py`.
- **hh2bbww** — `github.com/uhh-cms/hh2bbww`, the columnflow analysis framework of the
  **Hamburg group behind AN-24-091**, i.e. the code behind our closest Run 3 reference
  ([[2026-08-11-lessons-from-AN-24-091]]).

---

## 1. ⭐ top-pT reweighting — my first implementation was WRONG, now corrected

**HiggsDNA has no top-pT function at all** (checked every file in `systematics/` and all 40+
functions in `event_weight_systematics.py`). hh2bbww does, and it is authoritative.

### What I wrote first (from memory, unverified)

```python
SF(pT) = exp(a + b*pT),  a = 0.0615, b = -0.0005   # data-based
weight = sqrt(SF(t)*SF(tbar));  nominal = 1.0;  up = w;  down = 2 - w
```

### What hh2bbww actually applies

`hbw/production/top_pt_theory.py` → `top_pt_theory_weight`:

```python
sf_run2 = 0.103 * exp(-0.0118 * pT) - 0.000134 * pT + 0.973
sf      = (0.991 + 0.000075 * pT) * sf_run2      # Run 3 (13.6 TeV) rescaling
weight  = sqrt(prod(sf))                          # over the two gen tops
weight_down = 1.0                                 # "no correction"
weight_up   = 2*(weight - 1.0) + 1.0              # symmetric about nominal
```

**Three substantive differences:**

1. **Different parameterisation.** They use the **theory-based (NNLO/NLO)** form, not the
   data-based exponential. My `a=0.0615, b=-0.0005` values *do* exist in their config as
   `cfg.x.top_pt_weight` — but that is the *other*, data-driven variant. The one that
   actually carries their `top_pt_up/down` shift is `cfg.x.top_pt_theory_weight`
   (`a=0.103, b=-0.0118, c=0.000134, d=0.973`). **So my coefficients were real numbers
   applied to the wrong formula.**
2. **There is an explicit Run 3 rescaling factor** `(0.991 + 0.000075·pT)` on top of the
   Run 2 SF. My version had nothing of the kind — it was a pure Run 2 recipe.
3. **The correction IS applied to the nominal.** I had left nominal at 1.0 and used the
   correction only as an uncertainty. hh2bbww reweights the nominal and makes **down = 1.0**
   ("no correction") the variation. Same *span*, but a different central prediction.

Also: **no pT cap.** My 500 GeV clamp was invented; the theory form is well-behaved at high
pT (they expose `max_top_pt` but leave it `None`).

**FIXED** — `analysis/corrections/toppt.py` rewritten to the hh2bbww parameterisation.
Sanity-checked: SF 1.066 → 0.910 from pT 0 → 800 GeV, giving typical tt event weights of
0.96–0.99 (the expected few-percent softening).

## 2. ⭐ ggH heavy-flavour — ported from HiggsDNA, replaces the broken lnN

`event_weight_systematics.py` → **`Higgs_plus_HF_syst`**:

```python
genJets = get_genJets(events, pt_cut=25, eta_cut=2.5)
num_HF_jets = ak.sum(genJets.hadronFlavour == flav, axis=-1)   # 4=c, 5=b
up   = where(num_HF_jets > 0, 1 + rel_unc, 1.0)                # rel_unc = 0.5 default
down = where(num_HF_jets > 0, 1 - rel_unc, 1.0)
```

**This is strictly better than any flat lnN**, and it dissolves the scoping problem:

- the ±50% applies **only to events that actually contain a heavy-flavour gen jet**
- so it **does not care how processes are grouped** — no need to scale by ggH's 13.1% share
- and it produces the **shape** effect a flat lnN structurally cannot
- `rel_unc=0.5` matches AN-23-102 exactly

**PORTED** → `analysis/corrections/higgs_hf.py`, scoped to `GluGluH*`/`VBFH*` (HiggsDNA's
docstring: *"Make sure you apply it only on ggH or VBF samples"*), flavour pinned to `c`.
Verified `GenJet_hadronFlavour` exists in NanoAODv12.

**The `flavor_composition_ggH` lnN is now retired** (commented out with the full rationale).
The card goes from 10 lnN + 14 shapes → **9 lnN + 15 shapes**, the new one being
`higgs_plus_c`.

## 3. MET unclustered — my fix independently confirmed

HiggsDNA `MET_systematics.py` → `MET_syst_Unclustered` uses **exactly** the branches I found:

```python
events.PuppiMET.ptUnclusteredUp / ptUnclusteredDown
events.PuppiMET.phiUnclusteredUp / phiUnclusteredDown
```

Same source, same up/down ordering. Independent confirmation of both the diagnosis (the
`CorrectedMETFactory` path never runs for Run 3 PuppiMET) and the fix.

## 4. Confirmations of "not applicable"

| item | evidence |
|---|---|
| **muon Reco** | HiggsDNA `muonSFs` exposes only `NUM_*ID_DEN_TrackerMuons` and `NUM_*PFIso_DEN_*ID` — no reco key. hh2bbww registers `mu_id_sf` and `mu_iso_sf` shifts and **no `mu_reco_sf`** (while it *does* have `e_reco_sf` for electrons). Two frameworks, same conclusion. |
| **PU Jet ID** | absent from both frameworks for Run 3. |

## 5. ⚠️ What hh2bbww has that we do NOT — worth reviewing

From `hbw/config/config_run2.py`:

| their shift | our status |
|---|---|
| **`tune_up/down`** (id 1,2) | **we dropped UE.** They carry it as `disjoint_from_nominal` — i.e. **dedicated tune samples**, confirming it cannot be a weight. |
| **`hdamp_up/down`** (id 3,4) | **absent.** ME/PS matching scale for tt — a standard tt modelling uncertainty, also sample-based. |
| **`mtop_up/down`** (id 5,6) | **absent.** Top-mass variation, sample-based. |
| `vjets_up/down` (id 11,12) | **absent.** They apply an EW-correction reweighting to V+jets — relevant given V+jets is our problem process. |
| `dy_correction_up/down` (id 13,14) | **absent.** A dedicated data-driven DY correction. |
| `murf_envelope` | we have separate muR/muF/muRmuF; they also form an **envelope**. |
| `btag_*` per-source | we have a single ctag2d Total (deliberate deferral). |

**`hdamp` and `mtop` are the notable omissions** — both are standard tt modelling
systematics in Run 3 analyses, both need alternative samples, and neither appears in
AN-23-102 Table 16 either. Worth a documented decision rather than silence.

---

## Net effect on the card

| | before | after |
|---|---|---|
| lnN | 10 | **9** (`flavor_composition_ggH` retired) |
| shape | 14 | **15** (`+top_pt`, `+higgs_plus_c`) |
| object shifts | 6 | **7** (`+CMS_met_unclustered`, pending reprocess) |

All three additions need the **reprocessing campaign** before they appear in a limit. The
MET-unclustered one additionally needs `run_inference.py` over its two new shift dirs.

## Files touched (backed up, uncommitted)

- `analysis/corrections/toppt.py` — **rewritten** to the hh2bbww theory parameterisation
- `analysis/corrections/higgs_hf.py` — **NEW**, ported from HiggsDNA
- `analysis/corrections/correction_manager.py` — both hooks
- `analysis/corrections/jerc.py` — MET unclustered attach
- `analysis/workflows/hww_combine_2dcat.yaml` — weights on, lnN retired, shapes added

Verified: config loads, **9 lnN + 15 shapes**.
