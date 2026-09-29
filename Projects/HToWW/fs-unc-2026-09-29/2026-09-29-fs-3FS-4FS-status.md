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

Two ways to use it. ~~DECISION (user, 2026-09-29): option (a)~~ → **superseded the same day by §3c: stitching via reweighting, following LHCHWG-2026-007.**
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

## 3b. LHCHWG-2026-007 (arXiv:2608.26863) changes the approach — READ THIS FIRST
Official LHC Higgs WG report (Bevilacqua et al., 27 Aug 2026), the written version of the talk.
Saved: `References/HToWW/2026-LHCHWG-2026-007_Hc_flavour_schemes_arXiv2608.26863.pdf`.

**Its recommendation:** without NNLO at analysis level, use a **stitched signal**. This *"mitigates the need
for the flavour-scheme uncertainty obtained from a plain yield comparison of the massive and massless
samples, as used in Ref. [47] and resulting in O(30%)"*; the residual is covered by the **scale
uncertainty of the stitched sample**. ⇒ option (a) (flat 3FS/4FS nuisance) is what the paper moves away
from. **The user's decision was revisited: we now do the stitching via REWEIGHTING (below).**

**Stitching per the paper (Sec. 4.4):**
- split on N(GEN c-jets, **pT > 10 GeV**) (footnote 4: lower than the usual 25 GeV to resolve the soft-charm
  region); **0 → 4FS FxFx**, **≥1 → 3FS**.
- normalise each region to its own fiducial σ × a flat NNLO/NLO K-factor (3FS K taken from bb̄H), then
  rescale the total to the NNLO MiNNLOPS cc̄H σ (Table 3: 0.1664 fb × BR(γγ) ⇒ ≈ 73 fb at 13.6 TeV,
  ~25% below NLO 4FS).
- c-jet: "highest-pT jet containing at least one charm quark among those clustered with anti-kT"
  (Sec 5.3) / "jet containing a D or B hadron" (5.1). **Says nothing about excluding the Higgs decay
  products** — every study in the paper is H→γγ, so decay transfer never arises for them.
- **Denominator is 4FS FxFx (our nominal), not 4FS non-FxFx.** Table 3: 3FS 0.1248 fb/BR ≈ 55.0 fb
  (= ours), 4FS 0.2216 fb/BR ≈ 97.6 fb (FxFx). With γ+c cuts the 3FS/4FS ratio is 0.62 (~38%). ⇒ the
  earlier non-FxFx R ≈ 0.80 **understates** the difference relevant to our FxFx signal.

**Limit implications (qualitative, not yet computed):** stitching removes the flat FS nuisance
(`xsec_hplusc_4FS_5FS` costs 1034→921 today, 10.9%) and replaces it with the stitched scale variations.
NNLO normalisation is a SEPARATE choice that lowers σ_SM by ~25% ⇒ r-limit worse by ~25%, but it is the
more accurate prediction; compare options at equal normalisation. Limit is 62% stat-dominated.
Cheap bracket not yet run: copy the card to fs_unc/, set the FS lnN to 0 / 20% / 38%.

## 3c. Stitching via REWEIGHTING — the chosen path (2026-09-29)
**No new samples needed.** Literal stitching needs full-sim **3FS H→WW** for every era (does not exist
in Run 3: only 3FS H→γγ centrally; 3FS has 40% neg. weights ⇒ millions of events per era). Instead:
keep the **4FS FxFx** H→WW signal; events with **≥1 GEN c-jet (pT>10)** get weight **w(pT) = R(pT) =
σ(3FS)/σ(4FS FxFx)**, binned in leading GEN c-jet pT; 0c events keep weight 1 (= 4FS FxFx, as in
stitching). Captures stitching in the binned variable, not the full 3FS kinematics.

**Derivation — RUNNING (started 2026-09-29 18:00, tmux `stitch` on lxplus966, standalone):**
- script `fs_unc/gen/derive_stitch.py` (pT>10 split, bins 10/20/30/45/60/80/110/150/∞), driver
  `fs_unc/gen/run_stitch.sh`. Batch 1 = **decay-cleaned** (primary), batch 2 = **uncleaned** (paper-literal;
  definition systematic).
- samples: official 3FS + **4FS FxFx** HTo2G for all four Run-3 eras; Run-2 UL18 HToGG and HToWW
  (3FS + 4FS FxFx) for the decay-transfer validation. File lists `fs_unc/filelists/*_4FSFXFX.txt`.
- outputs: `fs_unc/stitch/{clean,noclean}_<sample>.json`; plots `fs_unc/plots/stitch_fxfx/`;
  **self-written summary `/eos/user/c/cgupta/HToWW/fs_unc/SUMMARY_STITCH.md`** — weight tables per era,
  era-combined weight table w(pT), GG-vs-WW shape-only χ². Driver log `fs_unc/logs/run_stitch.log`
  ends with `STITCH_DONE`.
- **Resume after a break:** `cat /eos/user/c/cgupta/HToWW/fs_unc/SUMMARY_STITCH.md`. If it is missing, check
  `tmux ls` on lxplus966 and `logs/stitch_*.log` (a `SKIP` line = xrootd timeout on one file, tolerated).
  Rerun with `bash fs_unc/gen/run_stitch.sh` (idempotent).

**Acceptance criteria before any framework work:** (1) the Run-3 eras agree (χ²/ndf ≈ 1);
(2) Run-2 GG vs WW, shape-only, c-jet pT χ²/ndf ≈ 1 for the **cleaned** definition;
(3) the cleaned-vs-uncleaned difference is quoted as the definition systematic.

**NEXT STEP — better decay treatment WITHOUT reclustering (user, 2026-09-29):** the user wants to keep the
**official GenJets and their official hadronFlavour**; STXS-style reclustering is **dropped**. The current
"cleaning" removes whole GenJets near decay products (overlap removal): it loses c-jets (16.6% γγ vs
11.5% WW) and causes the 1.4% γγ/WW fraction offset. Replace it with **subtraction**:
- **A (primary, NanoAOD, approximate):** for each official GenJet, subtract the 4-momentum of every Higgs
  decay product within ΔR<0.4 (status-1, fromHardProcess or hard-process τ product, not ν); then apply
  pT>10 to the corrected jet. Keeps official jets + hadronFlavour, keeps overlapping c-jets, and a jet
  that *was* a decay product falls to ~0. **Same definition can be applied to our H→WW signal NanoAOD**
  → derivation and application exactly consistent. Implement as a variant of `derive_stitch.py`.
- **B (exact cross-check, MiniAOD):** `slimmedGenJets` constituents → `packedGenParticles` traced to the
  Higgs; subtract exactly those. FWLite/CMSSW, heavier; run on a subset to validate A.
  MiniAOD confirmed on DAS (2026-09-29): Run-3 Run3Summer22EEMiniAODv4 3FS + 4FS-FxFx HTo2G; Run-2
  RunIISummer20UL18MiniAODv2 3FS + 4FS-FxFx for HToGG and HToWWTo2L2Nu.
- Pass criteria as before (eras agree; γγ vs WW c-jet-pT shape χ²/ndf ≈ 1) **plus** the γγ/WW fraction
  ratio agreeing at the ~0.2% level seen for uncleaned jets.

**Framework steps (ONLY after user says go):**
1. GEN columns on the H+c signal: `gen_ncjets`, `gen_cjet1_pt` with the **SAME definition as the
   derivation** — pT>10, |η|<2.4, hadronFlavour==4, and **excluding GenJets within ΔR<0.4 of the H→WW
   decay products** (leptons, τ products; not ν) — **to be replaced by the subtraction definition (A) above**. `select_gen_fs` is drafted (threshold 20, no cleaning) →
   update. Reprocess signal only, all eras (proxy valid until ~2026-10-07).
2. Weight: `w = R(gen_cjet1_pt)` if `gen_ncjets ≥ 1` else 1, from the era-combined table (correctionlib).
3. Normalisation per the paper (per-region K-factors, total to NNLO ~73 fb) — decide with the user.
4. Card: remove `xsec_hplusc_4FS_5FS`; signal `scalevar_*` shapes now evaluated on the stitched signal.
5. Limit vs 1034, impacts, and the AN Systematics section.

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
