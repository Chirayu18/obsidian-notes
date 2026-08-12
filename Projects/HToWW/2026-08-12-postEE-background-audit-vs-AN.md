---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# postEE background audit vs AN-23-102 (Run 2)

Audit of `analysis/filesets/2022postEE_nanov12.yaml` against AN-23-102 Table 3
(Run 2 background samples), plus a check that everything in the fileset is
actually consumed by `hww_combine_2dcat.yaml`.

Reference: `References/HToWW/AN-23-102.pdf`, Table 3 (p.8) and §2.3.

## Method

`get_datasets_to_run_over` (`analysis/filesets/utils.py:185`) does a **strict
key lookup** against the workflow's `datasets.mc` list — no substring matching,
no `-ext` expansion. A fileset entry whose `key` is not in that list is never
processed. Audit compared:

1. fileset `key` -> workflow `datasets.mc` (is it processed?)
2. fileset `process` -> `combine.process_map` (does it reach the datacard?)
3. process groups -> AN-23-102 Table 3 (is the background modelled at all?)

## Result 1 — everything the workflow requests exists

No workflow `mc:` key is missing from the postEE fileset. All 20 keys resolve.

## Result 2 — the `-ext` samples are NOT processed, and that is CORRECT

`tt-ext` (3 samples) and `singletop-ext` (6 samples) are in the fileset but not
in the workflow's `mc:` list, so they never run.

This is **not** a missing-background bug. The parent samples alone already carry
the full cross section:

| | parent sum | +ext sum | NNLO 13.6 TeV |
|---|---|---|---|
| tt | **923.41 pb** | 1393.08 pb | **923.6 pb** |

Parent-only reproduces NNLO to 0.02%. The `-ext` xsecs are a **proportional
split of the same total** across parent+ext by event count, so `read_scale =
lumi * xsec / sumw` normalises consistently on whichever subset runs.

**Adding `-ext` to the workflow without re-splitting the parent xsecs would
inflate tt by 1.5x.** Wiring them in is a two-part change (add keys AND
re-split xsecs), not a one-line edit. The stats gain is real (~34% more tt/ST
events) but it is not free.

## Result 3 — dead fileset entries (never processed, never in process_map)

These carry a `process` that `combine.process_map` does not cover, so even if
they were processed they would not reach the datacard:

| key | samples | process | note |
|---|---|---|---|
| `ggToZZ` | 7 | `ggToZZ`, `qqToZZ` | gg->ZZ continuum + ZZto4L |
| `electroweak` | 6 | `EW` | ZZZ WZZ WWZ TTWW TTZZ **TTZ** |
| `higgs` | 7 | `H(125)` | H->ZZ->4L set |
| `wz-excl` | 1 | `WZ` | WZto3LNu (exclusive) |

`process_groups` (labels) lists `qqToZZ`, `ggToZZ` and `H(125)`, but
`combine.process_map` does not — so these are MVA-trainable but datacard-invisible.

**TTZ (1.39 pb) is the one worth a second look**: ttV is a genuine irreducible
background in a top-rich eμ final state and AN-24-091 models it. AN-23-102
Table 3 does *not* list ttV, so this is not a Run 2 gap — but it is a real
physics question for a Run 3 analysis.

## Result 4 — comparison to AN-23-102 Table 3

| group | AN-23-102 (Run 2) | ours (postEE) | verdict |
|---|---|---|---|
| tt | 2 samples (2L2Nu, SemiLep) 454.8 pb | 3 samples (2L2Nu, LNu2Q, 4Q) 923.4 pb | **ours better** — we add the fully-hadronic mode |
| Single top | 5 samples 297.2 pb | 12 samples 323.9 pb | **ours better** — decay-split tW + t-ch + s-ch |
| Diboson | 12 exclusive samples | 3 inclusive (WW/WZ/ZZ) 193.3 pb | **AN better** — see below |
| W+gamma | 1 (WGToLNuG 01J) 192.3 pb | 5 PTG-binned 664.7 pb | **ours better** — binned in photon pT |
| V+jets | 3 NLO jet-binned + 4 pT-binned + 9 HT-binned + sherpa | **1 inclusive** 67710 pb | **AN much better** — known gap |
| Z+jets | **1** ττ→eμ-filtered, 117.08 pb | 2 inclusive DY, 27638 pb | **AN better** — see below |

### Diboson is the notable structural difference

AN-23-102 uses **12 exclusive diboson samples** split by decay
(ZZTo2L2Nu, ZZTo2Nu2Q, ZZTo2Q2L, ZZTo4Q, ZZTo4L, WZTo3LNu, WZTo2Q2L,
WZTo1L1Nu2Q, WZTo1L3Nu, WWTo1L1Nu2Q, WWTo4Q, WWTo2L2Nu).

We use **3 inclusive samples** (WW 122.3, WZ 54.3, ZZ 16.7). Inclusive is not
wrong — it covers the same phase space — but the exclusive set gives far more
effective statistics in the leptonic corners that actually enter an eμ SR,
because the hadronic modes do not eat the event budget. Given that diboson is a
real SR background (599 events in SR_hplusc) and our MC stat penalty is the
single largest systematic contribution, this is worth considering alongside the
V+jets replacement.

Note we DO have `WZto3LNu` (4.924 pb) in the fileset under key `wz-excl` — the
one exclusive diboson sample — but it is **not requested by the workflow**.

### Z+jets — the AN uses ONLY Z->tautau, and that is a deliberate stats argument

AN-23-102 §2.3 (lines 164-166), verbatim:

> "For Z+jets we consider only Z -> tautau -> e nu mu nu, which dominates our
> selection, since tau decays can generate e-mu final state, while Z -> mumu(ee)
> can't."

Their single Z+jets sample is `DYJetsToTauTau_TauToMuEle_M-50` (117.08 pb) — a
**generator-filtered** ττ→eμ sample. The reasoning is exact for an eμ final
state: Z→ee and Z→μμ cannot produce eμ, so simulating them is wasted budget.
Only Z→ττ with τ→e and τ→μ reaches the selection.

We use **inclusive** DY (`DYto2L_2Jets_10to50` + `DYto2L_2Jets_50`, 27638 pb
total) — 236x their cross section, where the large majority of generated events
are Z→ee/μμ that fail the eμ requirement immediately.

**MEASURED 2026-08-12** from `base/cutflow_base_DY+Jets.csv` (postEE, weighted):

| cut | events | fraction |
|---|---|---|
| initial | 9,582,982,303 | — |
| `one_ll_pair` | 12,023,064 | 0.126% of initial |
| `one_muon_one_electron` | **189,453** | **1.58% of ll pairs** |
| `atleast_one_cjet` | 68,638 | 0.00072% of initial |

**The eμ requirement alone discards 98.4% of DY events that already had a
lepton pair.** Overall SR survival is 1 in ~139,600 generated events.

That 98.4% is precisely the Z→ee/μμ contamination the AN's ττ→eμ generator
filter removes at source. We are paying full simulation and processing cost for
events that cannot enter the selection.

**Run 3 replacements EXIST** in `Run3Summer22EENanoAODv12` (verified via
`dasgoclient`) — the `_Filtered` variants are the direct analogue of the AN's
`TauToMuEle` sample:

| sample | events |
|---|---|
| `DYto2Tau-2Jets_M-50_0J_Filtered_TuneCP5_13p6TeV_amcatnloFXFX-pythia8` | 43,864,206 |
| `DYto2Tau-2Jets_M-50_1J_Filtered_...` | 65,170,238 |
| `DYto2Tau-2Jets_M-50_2J_Filtered_...` | 110,138,041 |
| **total filtered** | **219,172,485** |

Unfiltered `DYto2Tau-2Jets_MLL-50_{0,1,2}J` also exist (657M total) if an
unfiltered ττ sample is preferred.

Note these are also **jet-binned (0J/1J/2J)**, so switching solves the same
binning problem as the W+jets replacement and should probably be done in the
same pass. DY is a smaller SR background than V+jets, so priority is lower —
but the fix is the same shape and the phase-space waste is even more extreme
(98.4% vs the W+jets negative-weight issue).

Cross sections would be needed for whichever DY samples are adopted.

### V+jets — already known, already being worked

Confirms the earlier finding. AN-23-102 §2.3 explicitly rejects the inclusive
NLO aMCatNLO sample we use ("not used in this study since it has 5 times smaller
size than LO and with large fraction of negative weights") and instead stitches
jet-binned NLO + pT-binned + HT-binned LO samples. This is the root cause of the
MC-stat gap. Replacement is the active next task.

## Result 5 — WH was incomplete in postEE, absent elsewhere

All four W-decay/charge combinations exist in `Run3Summer22EENanoAODv12`
(verified via `dasgoclient`). The config had only two, an arbitrary pairing:

| sample | was in config | nevents |
|---|---|---|
| `WplusH_WtoLNu` | yes | — |
| `WminusH_Wto2Q` | yes | — |
| `WminusH_WtoLNu` | **no** | 696,034 |
| `WplusH_Wto2Q` | **no** | 686,547 |

`WminusH_WtoLNu` matters most: leptonic W-H is the 3-lepton final state, the WH
mode most likely to enter an eμ selection, and by charge symmetry it should
contribute comparably to the `WplusH_WtoLNu` already included.

**Both entries have been ADDED to the postEE fileset with `xsec: 0.0`**
(the existing convention for "present but contributes nothing", same as the
disabled TBbarQ/TbarBQ). They contribute zero yield until real cross sections
are supplied — see "Cross sections needed" below.

`whtoww` is also **entirely absent from 2022preEE, 2023preBPix, 2023postBPix**
— those eras have ZH and ggZH but no WH at all.

## Cross sections needed (for the user to supply)

| sample | status |
|---|---|
| `WminusH_WtoLNu_Hto2Wto2L2Nu` | placeholder `0.0` — needs real value |
| `WplusH_Wto2Q_Hto2Wto2L2Nu` | placeholder `0.0` — needs real value |

For reference, the two values already in the config are
`WplusH_WtoLNu = 0.006625105011` and `WminusH_Wto2Q = 0.008719124529`.

Optional, only if the corresponding samples are wired in:
- `WZto3LNu` already has 4.924 pb in the fileset (would need the inclusive WZ
  rescaled to avoid double counting, exactly like the `-ext` trap).
- TTZ already has 1.39 pb (needs a `process_map` entry, not a new xsec).
- **DY ττ-filtered replacement**: `DYto2Tau-2Jets_M-50_{0J,1J,2J}_Filtered`
  — 3 cross sections, if we adopt the AN's Z→ττ-only strategy.
- **W+jets replacement** (already-open task): `WtoLNu-2Jets_{0J,1J,2J}`.

## Files touched

- `analysis/filesets/2022postEE_nanov12.yaml` — added two WH entries with
  `xsec: 0.0` and a provenance comment. Backup:
  `2022postEE_nanov12.yaml.bak_pre_WH_20260812_134345`.
  Verified by YAML round-trip: 81 -> 83 entries, only the two added, no existing
  entry modified.

## Correction recorded

An earlier pass in this session derived the two missing WH cross sections
arithmetically (backing out sigma(W±H) via PDG W branching fractions from the two
existing entries, ratio W+/W- = 1.572) and wrote them into the config. That was
**self-consistency, not provenance** — the numbers were computed, not sourced.
They have been replaced with `0.0` placeholders. Do not reinstate them without a
real source.
