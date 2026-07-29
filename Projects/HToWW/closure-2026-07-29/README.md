---
tags: [reference, plot]
status: active
date: 2026-07-29
source: lxplus
---

# Data/MC closure — hww_combine_2dcat (Run 3, all eras)

Closure check run **before** building combine templates, on the native
`hww_combine_2dcat` production (Jul-15 negrw + 2D-cat MVA + native 2D c-tag SF).

## Why this needed new processing

`hww_combine_2dcat` was deliberately **MC-only** — its `datasets:` block had no `data:`
key, because the limit is Asimov/blind. A `data:` block
(`[muon, electron, muon_electron]`) was added 2026-07-29 and the collision data
processed per era: **postEE 9, preEE 8, 2023preBPix 20, 2023postBPix 10** datasets.

## Status

| era | jobs (exp/fin/miss) | closure plots |
|---|---|---|
| **2023postBPix** | 252 / 252 / **0** ✅ | ✅ 53 plots, rc=0, 0 errors |
| 2022postEE | in progress | pending |
| 2022preEE | in progress | pending |
| 2023preBPix | in progress | pending |

## Plots

`2023postBPix/` — 53 PDFs, `base` category, produced by
`run_postprocess.py --workflow hww_combine_2dcat --year 2023postBPix --postprocess --plot --log`.

Variables cover:
- **c-tagging discriminants** — `cjet_cand_cvsl_pnet`, `cjet_cand_cvsb_pnet`, `cjet_cand_flavour`
  (these directly probe the 2D-category inputs the new SF calibrates)
- **kinematics** — `cjet_cand_pt`, leading/subleading/third jet pT & flavour, jet multiplicity
- **event-level** — Δφ(l1,MET), Δφ(l2,MET), Δφ(ll,MET), Δφ(l1+MET, jets)

Source on lxplus:
`/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/outputs/hww_combine_2dcat/<era>/base/`

## Related fixes found while producing this

See [[2026-07-24-systematics-master-list]] and the memory notes:
- **JEC/JER version tags were stale** — 2023preBPix JER `JRV2`→`JRV3`, 2023postBPix JEC
  `V3`→`V4` + JER `JRV1`→`JRV3`. Before the fix *every* 2023 job died with
  `IndexError: map::at` and produced zero output.
- **Condor walltime** — `submit_condor.py --jobflavor` defaulted to `longlunch` (2 h);
  `TTto2L2Nu` partitions ran ~114 min and were killed by `SYSTEM_PERIODIC_REMOVE`,
  leaving parquets but **no `.coffea` end-marker** (which is what `jobs_status.py`
  actually counts). Default changed to `workday` (8 h) + `--nfiles 7`.
- **Private signal redirectors are per-era** — 2022postEE reads only via IIHE
  (`root://maite.iihe.ac.be:1094`); preEE/2023 via `cms-xrd-global`.
- **preEE H+b v1 is a broken unflattened EDM file** — use **v2**.
