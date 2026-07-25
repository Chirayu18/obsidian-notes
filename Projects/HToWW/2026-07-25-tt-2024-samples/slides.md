---
marp: true
theme: default
paginate: true
math: katex
size: 16:9
style: |
  section { font-size: 24px; }
  h1 { color: #2166ac; font-size: 40px; }
  h2 { color: #2166ac; font-size: 32px; }
  table { font-size: 18px; margin: 0 auto; }
  section.lead { text-align: center; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; align-items: center; }
  .small { font-size: 19px; }
  .hl { color: #b2182b; font-weight: bold; }
  code { font-size: 0.85em; }
---

<!-- _class: lead -->

# $t\bar{t}$ Samples — 2024 (Run 3)

### RunIII2024Summer24 NanoAODv15

Dataset survey for the H+c → WW analysis

Chirayu Gupta · 2026-07-25

---

## Scope & method

Queried DAS on lxplus with `dasgoclient`:

```bash
dasgoclient -query="dataset dataset=/TTto*/RunIII2024Summer24NanoAODv15*/NANOAODSIM"
dasgoclient -query="summary dataset=<ds>"     # nevents / nfiles / size
```

**Campaign:** `RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2`

<span class="hl">Caution:</span> a bare `/TT*/` wildcard returns **hundreds** of BSM
samples (`TTALPto2Mu`, `TTtoUEMu-LFV`, …). All listings here are filtered to
**SM $t\bar{t}$** production only.

<span class="small">Tier: NANOAODSIM. Several alternative NanoAOD flavours also exist per dataset
(`BTVNanoV15`, `JMENanoV15`, `FS` FastSim) — the plain `150X_..._v2` reco is the analysis default.</span>

---

## Nominal $t\bar{t}$ — inclusive decay channels

POWHEG + Pythia8, `TuneCP5`, 13.6 TeV

| dataset | events | files | size |
|---|---:|---:|---:|
| `TTto2L2Nu` | 470,123,263 | 780 | 1.49 TB |
| `TTtoLNu2Q` | 484,475,057 | 790 | 1.55 TB |
| `TTto4Q` | 472,535,695 | 773 | 1.49 TB |
| **total** | **1.43 B** | **2,343** | **4.53 TB** |

Full names follow the pattern:

<span class="small">`/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM`</span>

<span class="hl">Note the version suffix differs:</span> `2L2Nu` is `-v3`, the other two are `-v2`.

---

## HT-binned $t\bar{t}$ (MadGraph MLM)

`TT-3Jets_Bin-HT-*_TuneCP5_13p6TeV_madgraphMLM-pythia8`

| HT bin (GeV) | events | files | size |
|---|---:|---:|---:|
| 100–400 | 155,239,759 | 1,730 | 0.62 TB |
| 400–800 | 102,074,220 | 1,195 | 0.54 TB |
| 800–1500 | 52,531,094 | 549 | 0.32 TB |
| 1500–2500 | 33,843,305 | 613 | 0.23 TB |
| > 2500 | 32,720,384 | 517 | 0.23 TB |
| **total** | **376 M** | **4,604** | **1.95 TB** |

Useful if the analysis needs enhanced statistics at high hadronic activity —
complementary to, **not stackable with**, the inclusive POWHEG set.

---

## $t\bar{t}$ + heavy flavour

| dataset | events | files | size |
|---|---:|---:|---:|
| `TT4B` (madgraph) | 9,898,300 | 34 | 0.043 TB |
| `TTBBto2L2Nu` (powheg) | 12,499,196 | 203 | 0.045 TB |
| `TTBBtoLNu2Q` (powheg) | 22,473,402 | 283 | 0.081 TB |
| `TTBBto4Q` (powheg) | 14,990,580 | 189 | 0.053 TB |
| **total** | **59.9 M** | **709** | **0.22 TB** |

$t\bar{t}b\bar{b}$ matters for **c-tagging mis-ID** studies — the dominant
heavy-flavour background to a charm-tagged signal.

<span class="small">$t\bar{t}+V$ ( `TTZ-ZtoQQ`, `TTW-WtoQQ`, `TTWW`, `TTWZ`, `TTZZ`, `TTZH`, `TTWH` )
also exist in this campaign; small cross sections, listed in the companion note.</span>

---

## Systematic-variation samples (all available)

<div class="cols">
<div>

**Top mass** — `TTto2L2Nu_Par-MT-*`
`166p5`, `169p5`, `171p5`,
`173p5`, `175p5`, `178p5`

6 points, ±5 GeV around nominal

**$h_{damp}$** — `Par-Hdamp-*`
`158`, `418`
(nominal ≈ 243)

</div>
<div>

**Tune / colour reconnection**
`TuneCP5Up`, `TuneCP5Down`
`TuneCP5CR1`, `TuneCP5CR2`

**Alternative generators**
`amcatnloFXFX` (2-Jets)
`madgraphMLM` (3-Jets)
`sherpaMEPS` (4-Jets, 1NLO3LO)

</div>
</div>

The same `Par-MT` / `Par-Hdamp` / `Tune*` variations exist for **`TTtoLNu2Q`** as well
— so the standard modelling-uncertainty suite is fully covered for 2024.

---

## Comparison to the 2022postEE set in use

| | 2022postEE (current) | 2024 (this survey) |
|---|---|---|
| campaign | `RunIII2022EE…NanoAODv12` | `RunIII2024Summer24…v15` |
| nominal $t\bar{t}$ | `TTto2L2Nu`, `TTtoLNu2Q`, `TTto4Q` | same 3, **NanoAODv15** |
| inclusive events | — | **1.43 B** |
| HT-binned | not used | **available**, 376 M |
| $t\bar{t}b\bar{b}$ | not used | **available**, 60 M |

<span class="hl">NanoAOD version changes v12 → v15.</span> Branch content and
c-tagger columns differ; the `higgscharm` processor's expected branches must be
checked before any 2024 processing.

---

## Caveats before using these

1. **NanoAODv15 ≠ v12.** Verify branch names (`Jet_btagPNet*`, c-tagger WPs, `LHE*`) against
   the processor. The negrw training features (`lhe_*`, `genparton_*`) must all still exist.

2. **Do not mix** inclusive POWHEG with HT-binned MadGraph without a stitching prescription
   — they overlap in phase space.

3. **Multiple NanoAOD flavours** per dataset (`BTVNanoV15`, `JMENanoV15`, `FS`).
   Pick one deliberately; `150X_mcRun3_2024_realistic_v2` is the standard reco.

4. **Luminosity / golden JSON** for 2024 must be sorted before any data comparison.
   `Run2024A–I` exist with both `PromptReco` and `2024CDEReprocessing`.

5. **Cross sections** for 13.6 TeV 2024 — use the TOP PAG recommendation, not the 2022 values.

---

<!-- _class: lead -->

## Summary

**Nominal $t\bar{t}$: 1.43 B events / 4.53 TB** across 3 decay channels

**+ 376 M** HT-binned · **+ 60 M** $t\bar{t}b\bar{b}$

Full systematic suite available (mass, $h_{damp}$, tune, CR, alt. generators)

<br>

<span class="hl">Blocking question before use:</span>
does the `higgscharm` processor read NanoAOD**v15** branches?

<span class="small">Dataset lists + DAS commands: `Projects/HToWW/2026-07-25-tt-2024-samples/`</span>
