---
tags: [reference]
status: active
date: 2026-11-03
source: lxplus
---

# DY NanoAODv12 replacements for the 10 INVALID datasets

Follow-up to the 2026-10-29 blocker (all central DY NanoAODv12 datasets in the era yamls are INVALID in DBS; see `full-rerun-2026-10-01/2026-10-01-full-rerun-plan-and-findings.md`, section "ports from Saranya's HcZZ branch").

**Result:** each of the 10 has a VALID re-processing of the **same** sample: same generator, same campaign, same NanoAODv12 / 130X processing, only the processing version (`-vN`) changes. The one exception is the two 2023 `4Jets_MLL-50` entries. Those used a JMENano12p5 processing that has no valid copy, so their replacement is the standard `130X` NanoAODv12 processing. The other 73 or 74 MC entries in those yamls already use that processing. No private production is needed.

Nothing was edited in the analysis repo. Nothing was submitted.

## Where the entries live

Live repo: `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` (branch `hww-analysis`), `analysis/filesets/`:

| yaml | key | line |
|---|---|---|
| `2022preEE_nanov12.yaml` | `DYto2L_2Jets_50`, `DYto2L_2Jets_10to50` | 51, 57 |
| `2022postEE_nanov12.yaml` | `DYto2L_2Jets_50`, `DYto2L_2Jets_10to50` | 57, 63 |
| `2023preBPix_nanov12.yaml` | `DYto2L_4Jets_50` (key `dy_lo`), `DYto2L_2Jets_50`, `DYto2L_2Jets_10to50` | 123, 129, 135 |
| `2023postBPix_nanov12.yaml` | `DYto2L_4Jets_50` (key `dy_lo`), `DYto2L_2Jets_50`, `DYto2L_2Jets_10to50` | 63, 69, 75 |

The same two INVALID 2022postEE queries also appear in `2022postEE_nanov12_withWH.yaml` and `2022postEE_nanov12_withoutWH.yaml` (lines 57 and 63). Fix them there too if those variants are still used.

The four main yamls already have uncommitted edits in the working tree (about 360 added lines). Fold the query swap into those edits; do not overwrite them.

Other repo copies contain the same INVALID strings: `~/higgscharm` (`NewWorkflows`, which also has 48 HT-binned `4Jets` entries not checked here) and `~/higgscharm_thomas/higgscharm` (`since20251219`).

## Mapping (old → new)

Generator suffixes (`_TuneCP5_13p6TeV_amcatnloFXFX-pythia8` for 2Jets, `_TuneCP5_13p6TeV_madgraphMLM-pythia8` for 4Jets) and `/NANOAODSIM` are unchanged and omitted from the table. DBS reports 0 events and 0 files for every old dataset.

| # | era | sample | old processing (INVALID) | new processing (VALID) | nevents | nfiles | caveat |
|---|---|---|---|---|---|---|---|
| 1 | 2022preEE | 2Jets MLL-50 | `Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2` | `…_v5-v5` | 93,826,598 | 525 | none |
| 2 | 2022preEE | 2Jets MLL-10to50 | `Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2` | `…_v5-v4` | 97,571,898 | 448 | none |
| 3 | 2022postEE | 2Jets MLL-50 | `Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2` | `…_postEE_v6-v5` | 335,560,148 | 1682 | none |
| 4 | 2022postEE | 2Jets MLL-10to50 | `Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2` | `…_postEE_v6-v5` | 355,091,803 | 1573 | none |
| 5 | 2023preBPix | 4Jets MLL-50 (LO) | `Run3Summer23NanoAODv12-JMENano12p5_132X_mcRun3_2023_realistic_v5-v2` | `Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2` | 127,376,178 | 457 | JMENano → standard Nano (see below) |
| 6 | 2023preBPix | 2Jets MLL-50 | `Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v1` | `…_v14-v2` | 200,038,891 | 506 | none |
| 7 | 2023preBPix | 2Jets MLL-10to50 | `Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14_ext1-v3` | `…_v14_ext1-v4` | 200,240,144 | 657 | only an ext1 exists (old entry was ext1 too) |
| 8 | 2023postBPix | 4Jets MLL-50 (LO) | `Run3Summer23BPixNanoAODv12-JMENano12p5_132X_mcRun3_2023_realistic_postBPix_v4-v1` | `Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v4` | 70,167,286 | 301 | JMENano → standard Nano (see below) |
| 9 | 2023postBPix | 2Jets MLL-50 | `Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3` | `…_postBPix_v2-v4` | 94,876,537 | 312 | none |
| 10 | 2023postBPix | 2Jets MLL-10to50 | `Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2_ext1-v3` | `…_postBPix_v2_ext1-v4` | 100,410,583 | 342 | only an ext1 exists (old entry was ext1 too) |

All 10 new datasets have `dataset_access_type = VALID` and have disk replicas at T2_CH_CERN or several T1/T2 sites (`site dataset=` queried, tape excluded).

Full `query:` strings, ready to paste:

```
DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v5/NANOAODSIM
DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v4/NANOAODSIM
DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v5/NANOAODSIM
DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v5/NANOAODSIM
DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM
DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM
DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14_ext1-v4/NANOAODSIM
DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v4/NANOAODSIM
DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v4/NANOAODSIM
DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2_ext1-v4/NANOAODSIM
```

## Caveats

- **2023 `4Jets_MLL-50` (rows 5 and 8): different NanoAOD flavour.** The old entries were JMENano12p5 (132X), and every JMENano copy is INVALID. The replacement is standard NanoAODv12 (130X, `v14` / `postBPix_v2`), the same processing as every other MC entry in those yamls, so it is if anything more consistent. JMENano carries extra jet content and lower jet thresholds; check that nothing in the selection relies on JMENano-only branches for this one sample. Generator and gridpack are the same (madgraphMLM, same dataset name).
- **New nevents cannot be compared with the old ones from DBS**, because DBS reports 0 for the invalidated ones. If the old sumw sidecar jsons still exist on EOS, compare against them as a sanity check. Normalization must come from the new sidecar sumw anyway; see the memory note on the sumw trap.
- **Optional extra statistics (not in the current yamls):** VALID ext1 samples exist for 2022 2Jets:
  - preEE MLL-50 `…_v5_ext1-v2`: 92.7M events
  - preEE MLL-10to50 `…_v5_ext1-v2`: 48.9M events
  - postEE MLL-50 `…_postEE_v6_ext1-v2`: 353.6M events
  - postEE MLL-10to50 `…_postEE_v6_ext1-v4`: 178.9M events

  Adding them doubles the preEE MLL-50 statistics, but only if both parts share one sumw. As separate keys with the same xsec they would double-count. Not recommended for this rerun unless the framework already merges extensions.
- **Newer NanoAOD versions exist** (v13 and v15 are VALID for most of these). Staying on v12 keeps the processing and corrections consistent with the rest of the yamls, so v12 is the recommendation.
- No era is missing: every era/sample has a VALID v12 replacement.

## How this was checked

- Proxy `~/private/x509up_u151861` (valid, about 79 h left); `dasgoclient` queries run sequentially with `</dev/null`, following the 2026-10-29 note that parallel and `-json` loops returned empty results.
- `dataset dataset=/<sample>/Run3Summer2{2,3}*/NANOAODSIM status=* | grep dataset.name, dataset.dataset_access_type` lists every processing with its status. Then `dataset.nevents, dataset.nfiles` and `site dataset=` for each old and new dataset.
- Scripts and raw output are on lxplus in `~/private/dy_das_20261103/` (`list.sh`, `list.out`, `info.sh`, `info.out`).
