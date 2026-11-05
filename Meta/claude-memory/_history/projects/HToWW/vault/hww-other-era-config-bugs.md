---
name: hww-other-era-config-bugs
description: Two config bugs blocking HToWW 2023preBPix and 2022preEE H+b runs - stale JER version tags and a broken EDM-format tvanlaer NanoAOD
metadata: 
  node_type: memory
  type: project
  originSessionId: f8da6695-10e4-4546-93f9-e2fae00a093e
  modified: 2026-07-29T10:36:28.902Z
---

Hit both while running `hww_combine_2dcat` for eras beyond 2022postEE (2026-07-28).
Neither is related to the ctag2d/negrw work — both are pre-existing config/sample defects.

## 1. Stale JER version tags -> every 2023 job dies

**Symptom:** all 2023preBPix jobs fail, zero output, `IndexError: map::at` raised from
`analysis/corrections/jerc.py:337 get_corrected_jets_correctionlib`. (`map::at` = correctionlib
C++ key lookup miss.)

**Cause:** `analysis/corrections/jec_params_correctionlib.yaml` pinned JEC/JER tags that no
longer exist in the JME JSON (`correction_files["jerc"]`, /cvmfs .../jet_jerc.json.gz):
- 2023preBPix:  JER `Summer23Prompt23_RunCv1234_JRV2` -> JSON only has **JRV3**
- 2023postBPix: JER `Summer23BPixPrompt23_RunD_JRV1` -> **JRV3**, AND
                JEC `Summer23BPixPrompt23_V3` -> **V4**
(2023preBPix's JEC `Summer23Prompt23_V4` was already fine — only its JER token was stale.)

**Validator:** `/tmp/check_jerc.py` (also in the job tmp dir) checks all four eras at once —
run it after ANY jec_params edit. All four verified OK as of 2026-07-29.

**Fix applied:** sed JRV2->JRV3 and JRV1->JRV3 in that yaml (backup
`.bak_pre_jrv3`). Verify keys resolve before submitting:
`{jr}_MC_ScaleFactor_AK4PFPuppi` and `{jr}_MC_PtResolution_AK4PFPuppi` must be in the
JSON's `corrections`, and `{jec}_MC_L1L2L3Res_AK4PFPuppi` in `compound_corrections`.

## 2. tvanlaer preEE H+b v1 is a broken (unflattened) NanoAOD -> use v2

**Symptom:** 2022preEE `HplusBottom_HtoWW` jobs fail
`ValueError: invalid C++ type name syntax at char 15` (uproot branch-type parser).

**Cause:** the **v1** tvanlaer dataset
(`tvanlaer-Run3Summer22NanoAODv13-...ForNanov13_v1-v1-8653679c...`, the one listed in
Projects/HToWW/2026-07-08-hplusc-hplusb-crab-status.md) is **EDM format, not flat NanoAOD**:
1365/1390 branches are raw `nanoaodFlatTable_*` objects with `vector<signed char>` types;
**no Jet_pt / Muon_pt / Electron_pt at all**. Unreadable by any columnar framework.

**Fix:** use **v2** (`...ForNanov13_v1-v2-8653679c...`) — verified 1840 branches WITH
Jet_pt/Muon_pt/Electron_pt. Same 276 files. Updated 2022preEE yaml to v2.
**The vault CRAB-status note still lists v1 — it should be corrected to v2.**

Always sanity-check a new private sample before submitting:
`uproot.open(f)["Events"]` -> assert `Jet_pt` in keys.

## 3. runner.py submits EVERY dataset - never use it to add just data

`runner.py --workflow W --year Y --submit` submits **all** datasets in the workflow. To add
collision data to an already-processed era it re-runs all ~20 MC datasets too (~256 wasted
jobs on 2023postBPix, whose MC was already 242/242). It does NOT skip existing output.

**Use `submit_condor.py --dataset <name>` per dataset instead.** Enumerate the data samples
from the fileset yaml by `key` in {muon, electron, muon_electron} (names differ per era:
`MuonRun2022E/F/G`, `EGammaRun2022*`, `MuonEGRun2022*` for 2022; `Muon0/1Run2023Dv1/v2`,
`EGamma0/1Run2023Dv*`, `MuonEGRun2023Dv*` for 2023).

To clean up an accidental mass-submit: map ClusterId->dataset via `condor_q -af ClusterId
UserLog`, then `condor_rm` only the MC clusters.

Note `hww_combine_2dcat` was deliberately MC-only (`datasets:` had no `data:` key) because
the limit is Asimov/blind; a `data:` block was added 2026-07-29 for the data/MC closure.

## 4. "missing jobs" = MISSING .coffea MARKER, not missing parquets

`jobs_status.py` counts a job done **only** if `<output>/<dataset>/<dataset>_<n>.coffea`
exists. `submit.py` writes that marker *after* `run_uproot_job` fully completes, so it is a
true end-marker (a killed job that wrote some parquet shards leaves none; a job selecting
zero events still writes one). **Do not dismiss "missing" as a bookkeeping artifact by
checking parquet counts** — I wrongly did that for `TTto2L2Nu`, whose `_1.._10` dirs were
full of parquets while `TTto2L2Nu/` had ZERO .coffea markers = the jobs really never finished.

**Real cause there (2026-07-29): Condor WALLTIME.** `submit_condor.py --jobflavor` defaults to
**`longlunch` = 2h**, and TTto2L2Nu partitions (14 files each) ran ~114 min -> killed with
`Job removed by SYSTEM_PERIODIC_REMOVE due to wall time exceeded allowed max` (plus some
`XRootD error: [ERROR] Operation expired`). Memory was fine (~2.3 GB).

**Fix:** resubmit big samples with more walltime AND smaller partitions:
`submit_condor.py ... --dataset TTto2L2Nu --nfiles 7 --jobflavor workday`  (8h, 20 jobs).
Check `.log` for `wall time exceeded` / `MemoryUsage` before assuming an xrootd cause.

**Durable fix applied 2026-07-29:** `submit_condor.py --jobflavor` default changed
`longlunch` -> `workday` (backup `submit_condor.py.bak_pre_workday`). This matters because
**`jobs_status.py` resubmits without passing `--jobflavor`**, so it would otherwise silently
revert big samples to the 2h cap and they'd keep dying. It also reuses the stored `nfiles`
from `condor/<wf>/<year>/<ds>/args.json`, so partition size persists per dataset.

See [[Meta/claude-memory/_history/projects/HToWW/vault/hww-signal-private-fetch-iihe|hww-signal-private-fetch-iihe]] for the per-era redirector rules.
