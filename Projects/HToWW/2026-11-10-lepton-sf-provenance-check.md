---
tags: [reference, review]
status: active
date: 2026-11-10
source: laptop
evidence: agent-reported
---

# Lepton SF provenance check and c-tag status (2026-11-10)

**Chirayu (2026-11-10, verbatim):** "grid proxy is done, lepton SF check yourself and ctag is wrong anyways for now (livio will give an update on this). Explain 3 more"

This answers open item #2 of [[Projects/HToWW/2026-11-05-status-audit-retraining]], the lepton-SF factorisation for both flavours. **Status: agent-reported.** It is a check of provenance and consistency only. No SF was re-measured and no analysis code was edited.

## Result: the factorisation matches how the producers apply the same files

**Source.** The SF producer is the latinos HWW framework, `github.com/latinos/mkShapesRDF`. A shallow clone at HEAD `92f8cf4fce03c158979cada56ab18bc623eb4b34` (commit date 2026-10-29) was read only.

### Same files
All 8 analysis SF JSONs are **byte-identical (md5)** to the latinos copies for the matching era. Analysis files: `analysis/data/muon_HWW/<era>_muonSF_latinos_HWW.json` and `analysis/data/electron_HWW/<era>_electron.json`. Latinos files: `processor/data/scale_factor/Full{2022v12,2022EEv12,2023v12,2023BPixv12}/`. Era mapping:

| analysis era | latinos folder |
|---|---|
| 2022preEE | Full2022v12 |
| 2022postEE | Full2022EEv12 |
| 2023preBPix | Full2023v12 |
| 2023postBPix | Full2023BPixv12 |

### Muons
- Latinos working point `cut_TightID_pfIsoTight_HWW_tthmva_67` (`processor/data/LeptonSel_cfg.py` ≈ l.1934+, per era) takes three SFs:
  - `idSF` = `NUM_TightID_HWW_DEN_TrackerMuons`;
  - `isoSF` = `NUM_TightPFIso_DEN_TightID_HWW`;
  - `tthMvaSF` = `NUM_TightID_HWW_TightIso_tthMVA_DEN_TightPFIso`.
- `processor/modules/LeptonSF.py` ≈ l.850 multiplies them: `sf = sf_id * sf_iso * sf_tth`.
- The analysis applies the same three names (`muon.py:115, 189, 221`), each as a separate weight, so the nominal product is the same.
- **Selection matches:**

| cut | latinos | analysis |
|---|---|---|
| ID | `Muon_tightId`, \|dz\| < 0.1, \|dxy\| < 0.01 / 0.02 below / above 20 GeV | `working_points.py:100+` (`tight_HWW`), same cuts |
| isolation | `pfIsoId >= 4` | `pfRelIso04_all < 0.15` (the same Tight PF isolation) |
| ttH-MVA | `tthMVA > 0.67` | `tthMVA > 0.67` |

  Negligible difference: the |dxy| boundary at exactly pT = 20 GeV (`<=` vs `<`).

### Electrons
- Latinos working point `cutBased_MediumID_tthMVA_Run3` (`LeptonSel_cfg.py` ≈ l.230–258) uses three SFs:
  - `tkSF` (reco);
  - `wpSF` = POG `Medium` from `/cvmfs/cms-griddata.cern.ch/cat/metadata/EGM/<era>/2025-12-15/electron.json.gz`;
  - `tthMvaSF` = `cut_MediumID_tthMVA_Run3`.
- `LeptonSF.py` ≈ l.590 combines them as `sf_tot = sf * sf_tth`, with reco applied separately.
- The analysis workflow (`hww_allfix_4fs.yaml` ≈ l.230) applies `id: Medium`, `promptMVA: ttHMVA_Run3` and `reco: true`. That is the same structure.
- **Selection matches:** cut-based Medium (≥ 3), `tthMVA > 0.9`, and the barrel/endcap dxy/dz cuts (`working_points.py:157–162`).
- **POG file version:** the analysis uses EGM `2025-10-22`; latinos uses `2025-12-15`. The `Electron-ID-SF` values are **identical** for `Medium`, `RecoBelow20`, `Reco20to75` and `RecoAbove75` on a sampled grid in all four eras: 13 η × up to 6 pT points, and × 3 φ for 2023, where the inputs include φ. The maximum relative difference is 0. That is a sampled check, not a bin-by-bin proof. Script: `lxplus977:/tmp/cg_egm_cmp.py` (node-local).

### What this does and does not establish
- It establishes that the analysis applies the producers' own files with the producers' own combination: muon ID × iso × ttH-MVA, and electron Medium × ttH-MVA × reco.
- So the double-counting concern of audit #2 is **not supported**. The producers define the ttH-MVA SF to be multiplied on top of the ID (and iso) SFs.
- Not established: the tag-and-probe definitions behind each JSON. The JSON metadata gives only names, and the muon file description is generic Muon POG text. A measurement-level confirmation would still need the producers (Thomas or latinos) or their documentation.
- **Uncertainties differ from latinos.** Latinos combine the id/iso/tth stat and syst in quadrature into one total. The analysis keeps separate nuisances (`CMS_eff_m_id/iso/promptMVA`, `CMS_eff_e_id/promptMVA`). Both are a choice, not an error. Their correlation treatment differs.
- **Muon trigger SFs** remain disabled by the earlier explicit decision (2026-08-11); this check left that unchanged.

## c-tag
Chirayu states that the current c-tag SF/calibration "is wrong anyways for now". Livio will give an update. For the Run A pipeline this means:
- c-tag-dependent results are **provisional** until Livio's update;
- the c-tag SF and edges stay as configured, with no guessed edit;
- this is a known gate on any final result, not a blocker for running the TRAIN/RUN plumbing.

## Grid proxy
Chirayu reports that the proxy is done. At 2026-11-10 ~16:00 CET, `voms-proxy-info` on lxplus977 (the node this session uses) found no valid proxy. A default proxy lives in node-local `/tmp`, so it is probably on another lxplus node. `submit_condor.py:12–28` requires a valid proxy on the submitting node (`voms-proxy-info -exists -valid 0:20`). It then copies the proxy to `~/private/`. The copies there are from 29 Oct and 5 Nov, not new.

Nothing was submitted, edited or pushed.
