---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# TODO list + implementation map — where each systematic actually has to be added

**Session-continuity note (2026-08-11):** this is the working TODO. Companion notes:
[[2026-08-11-provenance-audit]] (source validity), [[2026-08-11-action-items-to-finish]]
(verified/missing audit), [[2026-08-11-route-to-a-better-limit]] (sensitivity),
[[2026-08-11-lessons-from-AN-24-091]] (Run 3 precedent).

State: **r < 1185** (2022postEE `hww_combine_2dcat`), stat-only 637, baseline 1164.
Card: 30 named nuisances (10 lnN + 20 shape) + autoMCStats(10) on 6 channels + `rate_tt`.

---

## ⚠️ CRITICAL CORRECTION — items 3–7 are NOT card-only changes

An earlier framing in this session called these "mechanical: find the recipe, add a row."
**That was wrong.** Verified against the repo and the parquets 2026-08-11:

**The parquets contain weight columns ONLY for systematics already in the card.** Present:
`weight_CMS_eff_e_*`, `weight_CMS_eff_m_id/iso`, `weight_CMS_pileup`, `weight_ps_isr/fsr`,
`weight_scalevar_*`, `weight_lhe_pdf/alphaS`, `weight_genweight`, `weight_nominal`.

**Absent:** `weight_top_pt`, any UE/tune weight, `weight_CMS_eff_m_reco`.

`grep` over `analysis/corrections/`: **no** `top_pt`, **no** `puid`/`pu_jet`, **no** muon
`reco`, **no** UE/tune module. `muon.py` implements `add_id_weights`, `add_iso_weights`,
`add_trigger_weights` — **no reco**.

**So 4 of the 5 require framework code + full reprocessing**, not a yaml edit. Classify before
scheduling:

| # | item | where it lives | reprocess? |
|---|---|---|---|
| 3 | **MET unclustered** | **object shift** | ⚠️ **code EXISTS, shifts never produced** — see below |
| 4 | **PU Jet ID** | weight (or N/A) | 🔴 no module; **check PUPPI first — may be legitimately N/A** |
| 5 | **top-pT reweight** | weight (tt only) | 🔴 no module, no weight column → **new correction + reprocess** |
| 6 | **underlying event** | weight (tune var) | 🔴 no module, no weight column → **new correction + reprocess** |
| 7 | **muon Reco** | weight | 🔴 `muon.py` has id/iso/trigger only → **extend module + reprocess** |

### Item 3 is the cheap one — the code is already written

`analysis/corrections/jerc.py` **lines 528–540** already emit the shift:

```python
if "MET_UnclusteredEnergy" in met.fields:
    shifts += [
        ({"Jet": jets, "MET": met.MET_UnclusteredEnergy.up},
         f"CMS_met_unclustered_{year[:4]}Up"),
        ({"Jet": jets, "MET": met.MET_UnclusteredEnergy.down}, ...
```

and the JEC name map already declares `UnClusteredEnergyDeltaX/Y` (lines 169–170).

**But EOS has only 12 shift dirs** — `CMS_{scale,res}_{j,e,m}_2022{Up,Down}`. **No
`CMS_met_unclustered_*`.** So the branch is either gated off or `MET_UnclusteredEnergy` is
absent from the NanoAOD fields at runtime. **Diagnose this first** — if it just needs enabling,
item 3 costs one reprocessing pass that can be shared with 5/6/7.

### Consequence for scheduling

**Batch 5, 6, 7 (+3 if it needs a rerun) into ONE reprocessing campaign.** Reprocessing is the
expensive step; doing it once for four systematics instead of four times is the difference
between one campaign and four. **And trigger SFs (`trigger: false`) need the same reprocessing
— fold that in too.** That turns "the long pole" into a single pass that closes five items.

---

## THE TODO LIST

### Phase 1 — config-only, no reprocessing (do now)

**#21 · Split `higgsbkg`, fix ggH scoping** 🔴 highest value
- Currently merges **7** samples; ggH is only **13.1%** of the merged SR yield
  (VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%, rest 4.6%).
- The AN's 50% is on **ggH alone**; our scaled 1.066 (fixed today from a wrong 1.40) still
  moves all 7 together and cannot reproduce the shape effect.
- Min: `ggH` / `other-H`. Better: `bkg-H+c` / `bkg-H+notc` by jet flavour (AN v10) → enables **2POI**.
- `cjet_cand_flavour` already in the parquets → **config only**.
- Also add missing **`BR_Htautau` 1%** (AN Table 16; we have H→ττ samples, no nuisance).

**#22 · `CR_tt` → single bin (yield-only)**
- Precedents: AN-23-102 line 662; AN-24-091 Table 10 (**all** CRs are literally 1 bin).
- CR_tt is 87.9% pure / 1.56M events → no useful shape; kills the §7.2.1 artificial-constraint
  mode and the migration artifact in that channel.
- Measure extending to all five CRs.

**#23 · Fix the impacts loop** 🔴 gates judging everything else
- 13 of 23 nuisances (**every shape one**) return a degenerate single-quantile 3984.4 while
  combine exits 0 → JES/JER and ctag2d impacts **unmeasured**.
- Cause likely `-t -1 --run blind --noFitAsimov` + `--freezeParameters` on a shape nuisance
  (`drive_combine.py` lines 90–92).
- **Also assert 5 quantiles** instead of trusting the exit code — the silent failure is the bug.

**#24 · Provenance write-up** (rolling)
- Document: lumi 1.4% source (2022 LumiPOG; **2023 differs** → per-era for multi-era);
  `xsec_vjets` 2.7% is the AN's **Z+jets** value but our group has W+jets too;
  `CMS_negrw_vjets` justification (ours, arXiv:2510.16217, not in the AN);
  range-maximum convention for `xsec_higgsbkg` / `alphaS_PDF`.

**Rebuild the card** to pick up `flavor_composition_ggH: 1.066` (config already patched today,
backup `.bak_ggh_scoping_*`). Expected **1185 → 1164**.

### Phase 2 — ONE reprocessing campaign (batch these)

- **#16 MET unclustered** — diagnose the gate in `jerc.py` first; may only need enabling
- **#18 top-pT** — new correction module, tt only. AN-23-102 line 566; AN-24-091 applies the
  **full** correction as the ±1σ (decide + document the convention)
- **#19 UE** — CP5 tune up/down; confirm the weights can be produced
- **#20 muon Reco** — extend `muon.py`; mirror the `electron_reco_*` pT-binned pattern
- **#17 PU Jet ID** — ⚠️ **check the jet collection first.** If PUPPI, PU Jet ID is likely
  superseded in Run 3 and the right answer is a **documented non-application**, not a nuisance.
- **TRIGGER SFs** — `trigger: false`; a **weighting-correctness bug**, not just a missing
  nuisance. Same campaign.

### Phase 3 — user-owned, in parallel

- **3FS/4FS samples.** User is generating these to derive the honest flavour-scheme
  uncertainty. ⚠️ The AN's prescription compares **non-FXFX 4FS vs non-FXFX 3FS** (Table 1:
  1.83 vs 1.13 fb → **38.3%**, not the quoted "order of 30%"). **Generate the matching 4FS
  non-FXFX sample too**, or the comparison won't follow the AN.
  Also **rename** the nuisance `xsec_hplusc_4FS_5FS` → `xsec_hplusc_3FS_4FS` (for H+c the AN
  compares 4FS vs 3FS; 5FS-vs-4FS is the **H+b** prescription).

### Phase 4 — where the limit actually moves

- **Multi-era V+jets MC.** MC stats is the **largest single systematic: 252 units**
  (1185 → 933 frozen), 223 of it in the SR. Measured: 2× → **1077**, 3× → **1037**.
  Conservative — a real multi-era fit also adds **data**, lowering the 637 floor.
- **Split `vjets` HF/LF** with separate floating rates (AN-24-091 floats DY+HF and DY+LF).
- **Nc-j SR split** — blocked until the MC exists (Nc-j>1 has only 147 raw V+jets events).
- **Adaptive binning** — logit transform, signal-flat, `σ_bkg < N_bkg/3`, per-category bin
  counts. Test **finer** as well as coarser (AN-24-091 Table 15: 20×4 beat 10×4, 30 → 28).

---

## "Are we done after this, except trigger SFs?" — no, three things remain

1. **V+jets MC statistics** — the dominant systematic; no card change fixes it.
2. **`vjets` and `st` grouping** — the same merged-group bug class as `higgsbkg`
   (`xsec_vjets` is a Z+jets number on a group with W+jets; `st` is one lnN over ~17 samples).
3. **Provenance for inherited values** — only **`BR_HtoWW`** and the `scalevar_*` shapes are
   sourced-and-valid without qualification. Everything else is a 13 TeV Run 2 number without a
   Run 3 argument, a range maximum, or scoped to a group the source never intended.

**After Phases 1–3:** card structurally complete and AN-defensible on methodology, but the
**sensitivity story still hinges on multi-era V+jets MC.**

## Standing constraints

No new production code without asking · **no EOS deletions** · **no retraining** ·
never `kinit`/passwords (reconnect via `python3 ~/bin/lxplus-connect.py`) ·
proxy is `/afs/cern.ch/user/c/cgupta/private/x509up_u151861` (**not** `cms.proxy`, expired).

## Open loose end

preEE `hww_ctag_compare` finished at **186/191**; `DYto2L_2Jets_50` and `TTto2L2Nu` are partial
(XRootD timeouts, stalled I/O). Deck notes this. **Headline numbers unaffected** — H+c 7/7 and
ggH 4/4 are complete, so signal 1.70× / ggH 2.67× / enrichment 0.64× stand.
