---
tags: [reference]
status: active
date: 2026-09-29
source: laptop
---

# H+c flavour-scheme (3FS vs 4FS) uncertainty — method, samples, results, next steps

> **Everything here lives OUTSIDE the analysis framework** (user's instruction, 2026-09-29).
> Scripts, file lists, outputs and plots: `/eos/user/c/cgupta/HToWW/fs_unc/`.
> Nothing in higgscharm `outputs/` or any production parquet was modified.

## 1. Method — FS "stitching" (T. Bevilacqua, 23-06-26)
[Slides](https://indico.cern.ch/event/1645713/contributions/7018110/attachments/3301014/5905014/H+c_towards_a_more_precise_simulation_Tiziano_Bevilacqua_260623.pdf) — slide 22:
- **≥1 GEN c-jet → 3FS** (pp→hcc̄, massive charm) · **0 GEN c-jets → 4FS** (pp→h).
- Normalisation of the two regions from the NNLO cross section. Same idea as tt+jets in HIG-24-018.

**Our selection needs ≥1 c-tagged jet → it sits on the 3FS side of the stitch.**
Measured (read-only, 2022postEE signal): the tagged candidate is a true c-jet in **78.4%** of
selected events (SR: 76.9%), light in 20.8%, b in 0.8%. Our nominal is 4FS **FxFx**, so the
flavour-scheme uncertainty *for our phase space* = 3FS vs 4FS in the ≥1 GEN c-jet region.

We measure R = σ(3FS)/σ(4FS) in the ≥1 GEN c-jet region, binned.
GEN c-jet = GenJet hadronFlavour==4, pT>20, |η|<2.4. Scale band = 7-point envelope
(LHEScaleWeight 0,1,3,5,7,8).

Two ways to use it. **DECISION (user, 2026-09-29): option (a), uncertainty only.**
Conditions before it goes in the card: (1) Run-2 GG ≈ WW, (2) the official Run-3 result
confirms the private one, (3) applied at GEN level (R if ≥1 GEN c-jet, else 1).
Reviewer points to pre-empt: why not stitch the nominal (answer: keep the established FxFx
nominal, cover the scheme difference as an uncertainty); the symmetric Down = 2−R is
conservative, since the physics is one-sided (3FS < 4FS in every bin).
- (a) **uncertainty only:** nominal stays 4FS FxFx, `xsec_hplusc_3FS_4FS` Up=R, Down=2−R,
  replacing the flat `xsec_hplusc_4FS_5FS = 1.30` lnN (misnamed — for H+c it is 3FS/4FS).
- (b) **stitched nominal** (the talk's recommendation): ≥1c events → 3FS prediction, 0c → 4FS,
  total normalised to NNLO.

## 2. Samples — all central, no generation needed
Official NanoAOD on DAS (lesson: **check DAS first** — I first generated privately, unnecessarily):
- **Run 3** `/HPlusCharm_{3FS,4FS}_MuRFScaleDynX0p50_HTo2G_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8/Run3Summer22EENanoAODv13-…/NANOAODSIM`
  (3.87M / 3.85M events; also exist for 2022preEE, 2023, 2023BPix; 4FS FxFx nominal too)
- **Run 2** `/HPlusCharm_{3FS,4FS}_MuRFScaleDynX0p50_{HToGG…_13TeV_amcatnlo_pythia8, HToWWTo2L2Nu…_13TeV-amcatnlo-pythia8}/RunIISummer20UL18NanoAODv9-…/NANOAODSIM`
  (GG 2.0M each, WW 5.0M each; all UL eras exist)
- Gridpacks (same cards) on cvmfs: `…/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/`
  and `…/gridpacks/UL/13TeV/madgraph/V5_2.6.5/`.

**Card-level check (done):** Run-2 HToGG ≡ Run-2 HToWW gridpacks — proc/run/param/model cards and
MG patch byte-identical (proc: `p p > h c c~` 3FS, `p p > h` 4FS; **no decay in the gridpack**,
Pythia decays the Higgs). Run 2 ≡ Run 3 except `ebeam 6500→6800`.
⇒ an HToGG-labelled sample is a valid proxy for our H→WW signal at production level.
The numerical Run-2 GG-vs-WW comparison (below) tests this including decay effects on GenJets.

## 3. Results

### ⛔ Run 3, PRIVATE NanoGEN (400k per scheme) — DO NOT USE IN ANY PRESENTATION
> **Never put the numbers or plots in this subsection into slides, the AN, or any talk.**
> They come from events I generated privately from the central gridpacks (a mistake — the
> official samples were on DAS). Kept only as an internal cross-check of the official result.
> For anything shown to others, use the **official-sample** results below only.
> Files affected: `fs_unc/ratio_full.json`, `fs_unc/test_ratio.json`, `fs_unc/out/`,
> `fs_unc/out_r2/`, `fs_unc/test*/`, and `fs_unc/plots/fs_ratio_{cjet1_pt,higgs_pt,stats}.*`.
> (user instruction, 2026-09-29)
| | 3FS | 4FS | R |
|---|---|---|---|
| σ inclusive | 54.9 fb | 83.2 fb | **0.659** |
| σ (≥1 GEN c-jet) | 14.5 fb | 18.3 fb | **0.789 ± 0.012 (stat)** |
| neg-weight fraction | 39.6% | 13.1% | |

R vs leading GEN c-jet pT (20/30/45/60/80/110/150/∞):
0.72, 0.85, 0.86, 0.83, 0.83, 0.77, 0.72 — stat 2.4→17.6%, **scale ~25% in every bin**.

**Statistics:** Neff(≥1c) = 4,623 (3FS; Neff/N = 4.3% because of 40% negative weights) and
58,855 (4FS). Stat on R(≥1c) = **1.5%** vs a **21%** effect → enough for the number used in
the card. The result is **limited by scale uncertainty (~25%), not statistics**. Only c-jet
pT > 110 GeV is stat-limited (12–18%), and the signal barely populates it. pT(H) is noisier
(22 effective 3FS events above 200 GeV) → prefer c-jet pT if binned.
**Physics:** inclusive gap 34% (AN "~30%", its Table 1 → 38%); only **21% in the ≥1c region**.
Shape is mild → mostly a normalisation.

### Official-sample results (2026-09-29) — USE THESE
All from central NanoAOD, read over xrootd, every event (one UL18 GG 4FS file of 77 timed out;
excluded consistently). Script `fs_unc/gen/derive_ratio_nano.py`, outputs `fs_unc/ratio_*.json`.

**Run 3, HTo2G 13.6 TeV — all four eras agree (χ²/ndf ≈ 1 in every variable)**

| era | R incl | **R (≥1 GEN c-jet)** | R (0 GEN c-jets) | σ3FS [fb] | σ4FS [fb] |
|---|---|---|---|---|---|
| 2022postEE | 0.655 | 0.792 | 0.620 | 54.67 | 83.43 |
| 2022preEE | 0.656 | 0.797 | 0.619 | 54.63 | 83.31 |
| 2023 | 0.658 | 0.793 | 0.622 | 54.84 | 83.37 |
| 2023BPix | 0.662 | 0.806 | 0.624 | 55.17 | 83.35 |

→ **R(≥1c) ≈ 0.795** (≈21% effect), sub-percent statistics. Statistics are not the limit: the 7-pt scale
spread on R is ~25% per bin.
2022postEE per bin (c-jet pT 20/30/45/60/80/110/150/∞): 0.728, 0.860, 0.804, 0.776, 0.907, 0.957, 0.868.

**Run 2 UL18, 13 TeV**

| | R incl | R (≥1c) | R (0c) | f3FS | f4FS | f3/f4 | σ3FS | σ4FS |
|---|---|---|---|---|---|---|---|---|
| HToGG | 0.622 | 0.770 | 0.584 | 0.2550 | 0.2060 | **1.2377** | 50.06 | 80.46 |
| HToWW | 0.650 | 0.806 | 0.612 | 0.2403 | 0.1939 | **1.2397** | 50.44 | 77.61 |

(f = σ(≥1c)/σ_incl; R(≥1c) = R_incl × f3/f4 separates normalisation from kinematics.)

**Validation findings**
1. **Energy:** Run 2 → Run 3 (GG) R(≥1c) 0.770 → 0.792 (+3%), c-jet-pT shape differs ≤9%
   ⇒ derive at 13.6 TeV (done), don't borrow Run 2.
2. **Decay (GG vs WW), integrated:** c-jet fraction ratio agrees to 0.2% (1.238 vs 1.240) ✅.
3. **Decay, normalisation:** the WW 4FS central sample has a 3.4% LOWER generator σ.
   **XSDB confirms it** (4FS non-FxFx, 13 TeV): HToGG 80.65 fb, HToZZ 80.65 fb, **HToWW 77.88 fb**;
   ours 80.46 / — / 77.61 → our computation reproduces XSDB to ≤0.5% (also Run 3 3FS: XSDB 54.97 vs
   ours 54.67 fb). The offset belongs to that production, not physics or statistics ⇒ compare GG vs WW
   on shape/fractions only. (XSDB lists identical 49.87 fb for 3FS GG and 3FS WW — copied entries.)
4. **Decay, shape: FAILS for the jet-based variables** (shape-only, R/R_incl): c-jet pT χ² 81/7
   (≤21%), pT(H) ≥1c 37/7, leading jet 0c 150/8; but pT(H) in 0c 8/7 ✅. Cause: GenJets cluster the
   Higgs decay products (photons in GG, leptons in WW). ⇒ **the binned GG c-jet-pT shape must not
   be applied to the WW signal as is.** Fix in progress: decay-cleaned c-jets (below).
5. **0 GEN c-jet region:** R(0c) ≈ 0.62 — 3FS is 38% below 4FS there too. Weighting 0c events by 1
   ignores this; relevant for the ~22% of selected signal with a light-mistag candidate. Decision needed.

### Decay-cleaned c-jets — DONE (2026-09-29)
GenJets within ΔR<0.4 of any stable Higgs decay product (status 1, fromHardProcess or hard-process
τ-decay product, not ν) removed (**overlap removal**, NOT STXS-style reclustering — NanoAOD lacks the
stable particles to recluster; STXS/Rivet `HiggsTemplateCrossSections` clusters jets excluding Higgs
decay products). Removes 16.6% (GG) vs 11.5% (WW) of c-jets in acceptance.
`derive_ratio_nano_clean.py` → `fs_unc/clean_*.json`, plots `fs_unc/plots/official_decayclean/`.

**GG vs WW, shape only (R/R_incl) — uncleaned → cleaned**
| variable | uncleaned | cleaned |
|---|---|---|
| **c-jet pT (≥1c)** | 81/7 ❌ | **7.9/7 ✅** |
| pT(H) ≥1c | 37/7 ❌ | 16.3/7 ⚠️ (≤8%) |
| pT(H) 0c | 8.0/7 ✅ | 9.1/7 ✅ |
| pT(H) inclusive | — | 6.6/7 ✅ |
| leading jet 0c | 150/8 ❌ | 104/8 ❌ (not used for weights) |
⇒ **decay contamination of the jets caused the GG/WW shape difference; the cleaned c-jet-pT shape transfers.**

**Integrated, cleaned:** R(≥1c) Run-2 GG 0.797, Run-2 WW 0.821; **Run-3 four eras 0.813 / 0.820 / 0.815 / 0.824**
(eras agree, χ²/ndf ≈ 1). Fraction ratio GG vs WW now differs 1.4% (1.281 vs 1.263; was 0.2%) — the
overlap-removal artifact (whole c-jets dropped, decay-dependent rate).
**Definition systematic:** Run-3 R(≥1c) 0.792 (uncleaned) → 0.813 (cleaned), ~2.6%.

### Recommendation for the card (updated after cleaning)
Run-3 **R(≥1c) ≈ 0.80–0.82** → an ~18–20% effect on events with a GEN c-jet, with a ~2–3% jet-definition
systematic. The binned cleaned c-jet-pT shape is now transferable GG → WW. Next: a **c-hadron-based**
cross-check (decay-independent without removing jets) to pin the integrated value.

## 4. Plots
Official: [CERNBox `fs_unc/plots/official/`](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/official) — one folder per sample (≥1c, 0c, inclusive; no bands) + `comparisons/`.
Decay-cleaned: `fs_unc/plots/official_decayclean/` (same layout).
> ⛔ The three plots listed below are **private-sample** plots — internal only, never in a ppt.
> Official-sample plots will be added under new names (`*_official*`, `cmp_*`).
`/eos/user/c/cgupta/HToWW/fs_unc/plots/` — [CERNBox](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots)
- `fs_ratio_cjet1_pt.png`, `fs_ratio_higgs_pt.png` — Run-3 3FS vs 4FS + ratio (private 400k)
- `fs_ratio_stats.png` — stat vs scale uncertainty vs effect size, per bin

## 5. Caveats
- R compares **non-FxFx** 4FS with 3FS (AN prescription), while our nominal is 4FS **FxFx**.
- **Reco vs GEN:** the 22% light-mistag events may have **no** GEN c-jet → they belong to the 4FS
  region and must get weight 1, not R. Only a GEN-level pass can tell. A reco-c-jet-pT stand-in
  treats all events as ≥1c and slightly **overstates** the effect.

## 6. Framework to-dos — ONLY after the weights are validated and the user says go
1. GEN columns for the signal: `gen_ncjets`, `gen_cjet1_pt` (method `select_gen_fs` drafted);
   reprocess **H+c only**, all eras (needs the grid proxy, now valid until ~2026-10-07).
2. Store the R table as correctionlib JSON in `analysis/corrections/`; per event
   `R(gen_cjet1_pt)` if `gen_ncjets ≥ 1` else 1 → `weight_xsec_hplusc_3FS_4FS{Up,Down}`.
3. Card: add to `shape_systematics`, remove `xsec_hplusc_4FS_5FS` (no double counting); decide
   Down (2−R vs one-sided) and whether it carries normalisation or shape only.
4. If option (b): change the nominal signal weight; NNLO normalisation.
5. postprocess → inference → card → limit → impacts; compare against 1034.
6. Optional: the H+b analogue (4FS/5FS) for the H+b part of higgsbkg.
7. Other eras: one GEN-level table serves all eras.
8. Update the AN Systematics section and this note.

## 7. Framework footprint left from earlier (to clean up — pending user decision)
- `analysis/selections/object_selections.py`: `select_gen_fs` added (unused). Original backed up at
  `/eos/user/c/cgupta/HToWW/fs_unc/object_selections.py.bak`.
- untracked `analysis/workflows/hww_2dcat_fs{base,unc,gen}.yaml`
- `outputs/hww_2dcat_fsunc/` (symlinks only) + `outputs/hww_2dcat_fsbase` symlink.
- Framework-side card build / chain **stopped** 2026-09-29.

## Superseded in this note
The unattended condor chain described in the first version (cluster 9472750, private Run-2
generation) was **cancelled**: official Run-2 NanoAOD exists on DAS.
