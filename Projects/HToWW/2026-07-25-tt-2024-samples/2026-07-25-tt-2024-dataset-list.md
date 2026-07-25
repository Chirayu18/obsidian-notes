---
tags: [reference]
status: active
date: 2026-07-25
source: lxplus
---

# $t\bar{t}$ 2024 datasets — RunIII2024Summer24 NanoAODv15

Companion to [[slides]]. Queried via `dasgoclient` on lxplus, 2026-07-25.
Campaign: `RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2`.

## How this was queried

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
C='RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2*'
dasgoclient -query="dataset dataset=/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/${C}/NANOAODSIM"
dasgoclient -query="summary dataset=<full-dataset-path>"   # nevents, nfiles, file_size
```

⚠️ A bare `/TT*/` wildcard pulls in **hundreds** of BSM samples (`TTALPto2Mu_*`,
`TTtoUEMu-LFV-*`, `TTtoUETau-*`, …). Always filter to the SM production modes below.

## Nominal inclusive (POWHEG+Pythia8) — use these

| events | files | size | dataset |
|---:|---:|---:|---|
| 470,123,263 | 780 | 1.492 TB | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM` |
| 484,475,057 | 790 | 1.551 TB | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 472,535,695 | 773 | 1.490 TB | `/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |

**Total 1,427,134,015 events / 2,343 files / 4.53 TB.**
Note `TTto2L2Nu` is `-v3`; the other two are `-v2`.

## HT-binned (MadGraph MLM)

`/TT-3Jets_Bin-HT-<bin>_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM`

| HT bin | events | files | size |
|---|---:|---:|---:|
| `100to400` | 155,239,759 | 1,730 | 0.620 TB |
| `400to800` | 102,074,220 | 1,195 | 0.541 TB |
| `800to1500` | 52,531,094 | 549 | 0.322 TB |
| `1500to2500` | 33,843,305 | 613 | 0.229 TB |
| `2500` | 32,720,384 | 517 | 0.234 TB |

**Total 376,408,762 events / 4,604 files / 1.95 TB.**
Do **not** stack with the inclusive POWHEG set without a stitching prescription.

## $t\bar{t}$ + heavy flavour

| events | files | size | dataset |
|---:|---:|---:|---|
| 9,898,300 | 34 | 0.043 TB | `/TT4B_TuneCP5_13p6TeV_madgraph-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM` |
| 12,499,196 | 203 | 0.045 TB | `/TTBBto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 22,473,402 | 283 | 0.081 TB | `/TTBBtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 14,990,580 | 189 | 0.053 TB | `/TTBBto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |

**Total 59,861,478 events / 709 files / 0.22 TB.**

## $t\bar{t}$ + V (present, counts not pulled)

`TTZ-ZtoQQ-1J` (madgraphMLM), `TTZ-ZtoQQ-1Jets` (amcatnloFXFXold), `TTW-WtoQQ-1Jets`,
`TTWW`, `TTWZ`, `TTZZ`, `TTZZ-ZZto4B`, `TTZH-ZHto4B`, `TTWH` — all
`_TuneCP5_13p6TeV_madgraph-pythia8` in the same campaign.

## Systematic variations (exist for both `TTto2L2Nu` and `TTtoLNu2Q`)

- **Top mass:** `Par-MT-166p5`, `169p5`, `171p5`, `173p5`, `175p5`, `178p5`
- **$h_{damp}$:** `Par-Hdamp-158`, `Par-Hdamp-418`
- **Tune / CR:** `TuneCP5Up`, `TuneCP5Down`, `TuneCP5CR1`, `TuneCP5CR2`
- **Alt. generators:** `TTtoL{plus,minus}Nu2Q-2Jets` (amcatnloFXFX),
  `-3Jets` (madgraphMLM), `-4Jets-1NLO3LO` (sherpaMEPS, `TuneAHADIC` / `TuneSherpaDef`)
- Also present: `TTtoLNuCB` (CKM-suppressed $t \to b/s/d$ decays)

Note some datasets have `FSMiniv6_FSNanov15` (FastSim) and `ext1` extensions.

## Other NanoAOD flavours per dataset

Beyond the standard `150X_mcRun3_2024_realistic_v2` reco, `TTtoLNu2Q` also exists as
`BTVNanoV15`, `JMENanoV15`, and `FS` (FastSim). Choose deliberately — the plain
reco is the analysis default.

## ⚠️ Before using any of this

1. **NanoAODv12 → v15.** The current analysis runs `RunIII2022EE…NanoAODv12`. Branch
   content differs. The negrw model needs `lhe_*` and `genparton_*` features
   (see [[hww-negweight-reweight-fix]]) — confirm they survive in v15 before assuming
   the reweighting transfers.
2. **c-tagger columns.** PNet/UParT WPs and naming changed across Nano versions; the
   `higgscharm` processor's expected branches must be checked.
3. **Cross sections.** Use TOP PAG 13.6 TeV recommendations, not the 2022 numbers.
4. **Golden JSON / lumi** for 2024 (`Run2024A–I`, both `PromptReco` and
   `2024CDEReprocessing`) needed before any data/MC comparison.

## Status

This is a **survey only** — nothing fetched, no fileset written, no processing run.
The 2022postEE workflow is untouched.

Related: [[RESUME-condor-retrain]], [[2026-07-18-v32-optimization-negative-results]]
