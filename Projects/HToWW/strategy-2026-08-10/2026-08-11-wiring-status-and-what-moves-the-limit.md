---
tags: [reference]
status: active
date: 2026-08-11
source: lxplus
---

# Wiring status — what is now in the framework, and what moves the limit when

Companion to [[2026-08-11-TODO-and-implementation-map]]. All edits are in the **higgscharm
repo** (not the vault); every touched file has a `.bak_*` backup and is **uncommitted** —
repo commits are the user's call.

---

## PART 1 — Reflected in a NEW LIMIT with only a CARD REBUILD (~30 min, no reprocessing)

These use data already on EOS. Rebuild `make_combine_inputs.py` → `run_combine.sh` and the
number moves.

| item | change | expected |
|---|---|---|
| **`flavor_composition_ggH` 1.40 → 1.066** | already patched in yaml | **1185 → 1164** (measured) |
| **#21 `higgsbkg` split** | process_map change; applies the real 1.50 to ggH alone | not yet measured |
| **`BR_Htautau` 1% lnN** | pure card row | negligible, closes an AN gap |
| **#22 `CR_tt` → 1 bin** | card binning | not yet measured; removes the migration artifact |
| **#23 impacts-loop fix** | doesn't change the limit — makes 13 shape systs *measurable* | — |

**Why the `higgsbkg` split needs no retraining:** the six channels are argmax-defined by the
frozen 6-class score, but the *processes within* a channel come from `combine.process_map` at
card-build time. Splitting ggH out changes only how rows are grouped in the datacard.

## PART 2 — Requires the REPROCESSING CAMPAIGN (no effect until it runs)

Wired and verified to load, but the weights/shifts do not exist in the current parquets.

| item | status | what it needs |
|---|---|---|
| **#18 top-pT** ✅ wired | new `analysis/corrections/toppt.py`, hooked into `correction_manager.py`, `toppTWeight: true`, `top_pt` in shape list | reprocess → new `weight_top_pt*` columns |
| **#16 MET unclustered** ✅ wired | `jerc.py` patched — see root cause below | reprocess → **2 new shift dirs** → **`run_inference.py` on them** → card |

⚠️ **#16 has an extra step.** It creates `CMS_met_unclustered_2022Up/Down` shift dirs, which
must then be scored by `run_inference.py` *before* the card build. **Skipping that is exactly
the bug that produced the 19/57-sample JES/JER failure.**

### Root cause found for #16 (worth recording)

The shift loop in `jerc.py` (~line 528) gates on `"MET_UnclusteredEnergy" in met.fields` — the
`CorrectedMETFactory`/PF-MET convention. But **Run 3 takes the PuppiMET branch** (~line 196),
which builds MET by hand via `corrected_polar_met` and **never calls the factory**, so that
field is never attached and the shift could never fire.

Fix: NanoAODv12 ships the variation directly — verified `PuppiMET_ptUnclusteredUp/Down` and
`PuppiMET_phiUnclusteredUp/Down` exist in the files. `jerc.py` now attaches
`met["MET_UnclusteredEnergy"]` from those branches, and the existing loop fires unchanged.

## PART 3 — RESOLVED AS NOT APPLICABLE (no code, document in the AN)

Two of the five "missing" systematics turned out not to be gaps at all.

**#17 PU Jet ID — N/A.** The analysis is NanoAODv12 with **PUPPI** jets and PuppiMET. PU Jet ID
is a **CHS** mitigation, superseded by PUPPI's own pileup subtraction; the JME POG provides no
Run 3 PUPPI recommendation. AN-23-102 lists it because it is a full Run 2 CHS analysis.

**#20 muon Reco — N/A.** Verified directly against the MUO POG json for 2022preEE and
2022postEE: **no reco SF exists** (searched every key for Reco/genTracks/Track-numerator →
empty). ID keys use `DEN_TrackerMuons`, i.e. already relative to tracker muons. By contrast
`correction_files` has a dedicated **`electron_reco`** entry — the POG ships one for electrons
and not muons because Run 3 muon reco efficiency is ~99.9% and flat.

**Both need a sentence in the AN, not a nuisance.**

## PART 4 — BLOCKED

**#19 Underlying event — not wireable as a weight.** No tune/UE weight columns exist in the
parquets and no standard UE weight exists in NanoAOD. CMS evaluates UE with dedicated
**`TuneCP5Up/Down` samples**. AN-23-102 combines "Underlying events & parton showering" into
one entry and we already have the PS half (`ps_isr`/`ps_fsr`).

**Decision needed:** (a) request/locate TuneCP5 up-down samples for the Run 3 campaigns — a
significant production ask — or (b) document that only the PS component is applied and justify
the omission.

## PART 5 — CLOSED BY USER DECISION

**Trigger SFs — NOT enabled** (user, 2026-08-11). Reverted to `trigger: false` for muon and
electron; the `muon_trigger`/`electron_trigger` shape rows were removed. The yaml comment now
records this as a deliberate accepted decision rather than an oversight.

**Consequence to state in the AN:** the nominal weights carry **no trigger correction**, so
this is both a missing nuisance (AN-23-102 Table 16 "HLT efficiencies") *and* an un-applied
correction. It remains a known gap.

---

## Files touched (all backed up, none committed)

| file | change |
|---|---|
| `analysis/corrections/toppt.py` | **NEW** — top-pT reweighting module |
| `analysis/corrections/correction_manager.py` | import + `toppTWeight` hook |
| `analysis/corrections/jerc.py` | attach `MET_UnclusteredEnergy` from PuppiMET branches |
| `analysis/workflows/hww_combine_2dcat.yaml` | `toppTWeight: true`; `top_pt` shape; ggH 1.066; trigger comment |

Verified: `WorkflowConfigBuilder` loads, `toppTWeight True`, trigger `False`, 14 shape systematics.

## ⚠️ Prerequisite before any campaign — EOS quota

Quota was at **~95%** (954.6 GB / 1 TB) after the `nocjet_kin` cleanup. A reprocessing campaign
writes a full new parquet set **plus two new shift dirs**. **User decision needed:**

- **overwrite `hww_combine_2dcat` in place** — no extra space, but destroys the tree behind the
  current 1185 result *during* the campaign, or
- **write to a new workflow name** — keeps 1185 reproducible, needs headroom that may not exist.

## Recommended order

1. **Card-rebuild items first** (Part 1) — cheap, and they bank a better number (≈1164+) before
   anything is disturbed.
2. **Fix the impacts loop** (#23) — so the campaign's new systematics can actually be judged.
3. **Resolve the EOS decision**, then run **one** campaign covering #16 + #18 (+ trigger SFs if
   that decision is ever revisited).
4. **`run_inference.py` on the two new MET shift dirs** — do not skip.
5. Rebuild, refit, compare.

**Expect the limit to get slightly WORSE** after Part 2. You are currently missing real
uncertainties, so 1185 is optimistic. That is honesty, not regression.
