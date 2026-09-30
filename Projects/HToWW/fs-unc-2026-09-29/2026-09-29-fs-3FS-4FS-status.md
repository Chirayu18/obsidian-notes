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

**QUEUED NEXT STEP — exact decay treatment on MiniAOD (user, 2026-09-29):** keep the **official GenJets
and their official hadronFlavour**; no reclustering, and no approximate NanoAOD subtraction (both dropped
by the user). The current NanoAOD "cleaning" removes whole GenJets near decay products (overlap removal):
it loses c-jets (16.6% γγ vs 11.5% WW) and causes the 1.4% γγ/WW fraction offset.
- **Method:** in MiniAOD, `slimmedGenJets` keep references to their constituents in `packedGenParticles`.
  Trace each constituent to the Higgs (mother chain via `prunedGenParticles`), subtract exactly the
  Higgs-descendant constituents from the jet 4-momentum, then apply pT>10, |η|<2.4 and keep the official
  `hadronFlavour`. Exact, no approximation, no reclustering.
- **What "Higgs descendant" covers:** every stable constituent whose ancestry reaches the H — not just the W
  (W's are unstable and never jet constituents). For H→WW→2ℓ2ν: charged leptons, τ decay products (π±, K±,
  π⁰ photons), and FSR photons off those leptons (ν are already excluded from GenJets). For H→γγ: the photons
  + their FSR. Kept: charm hadronisation products, ISR, underlying event.
- **Implementation caveat:** `packedGenParticles` → `prunedGenParticles` gives only the first mother; walk up
  the pruned chain until the Higgs is reached (pruned keeps H, W, τ, leptons, so the chain is intact).
  Hadronic W decays would be subtracted by the same logic (not present in WW→2ℓ2ν).
- **Tools:** FWLite / CMSSW (python), reading MiniAOD over xrootd; standalone in `fs_unc/`, outside the framework.
- **Samples (MiniAOD confirmed on DAS 2026-09-29):** Run-3 `Run3Summer22EEMiniAODv4` 3FS + 4FS-FxFx HTo2G;
  Run-2 `RunIISummer20UL18MiniAODv2` 3FS + 4FS-FxFx for HToGG and HToWWTo2L2Nu.
- **Pass criteria:** Run-3 eras agree; γγ vs WW c-jet-pT shape χ²/ndf ≈ 1; γγ/WW fraction ratio agrees at
  the ~0.2% level seen for uncleaned jets.
- **Open point to decide then:** how the weights get applied to our H→WW signal with the *same* definition —
  our signal is NanoAOD-level in the framework, so the per-event GEN c-jet quantity must come from MiniAOD
  (or an equivalent stored in the signal ntuples).

### ✅ FIXED (2026-09-30) — BUG in the stitch derivation: FxFx normalisation
> Fixed with the Run-3 XSDB value from the user (**4FS FxFx HTo2G 13.6 TeV = 97.62 fb**, 22postEE entry; same process name/gridpack used for all eras) and independently **validated from `GenLumiInfoProduct`**: pre-veto σ × accepted/tried (event counts) = 262.6×0.3458 = 90.8 fb (XSDB 90.67), 263.7×0.3438 = 90.7 (XSDB 90.50), 281.7×0.3464 = 97.6 (XSDB 97.62). Corrected NanoAOD-overlap-removal JSONs: `fs_unc/stitch/clean_<sample>_fxfxfixed.json` (script `gen/fix_fxfx_norm.py`). The `run_stitch.sh` tmux session died at 18:51 on 29 Sep (2023BPix + the whole uncleaned batch never finished) — **not rerun: superseded by the MiniAOD result in §3d.**

`run_stitch.sh` gives R(≥1c) ≈ 0.23 — WRONG. Cause: for **FxFx** samples, Σ genWeight / genEventCount is
the σ **before** the FxFx merging veto (~2/3 of LHE events are vetoed in Pythia; survivors keep their LHE
weight; NanoAOD `genEventCount` counts only survivors). Measured 4FS-FxFx σ: 262.6 fb (Run-2 γγ) vs
**XSDB 90.67 fb** (ratio 0.345); Run-3 281.7 fb. Non-FxFx samples are unaffected (they matched XSDB).
**Region fractions and all binned shapes are fine** (single constant factor) → **no rerun needed**; fix:
σ₄(region) = σ_XSDB(FxFx) × Σw_region/Σw_all. Run-2 γγ: R(≥1c) = 0.232/0.345 ≈ **0.67** (paper's γ+c: ~0.62).
**Needed from the user:** XSDB σ for the Run-3 4FS FxFx HTo2G samples (13.6 TeV, all eras). XSDB 13 TeV
FxFx: HToGG 90.67 fb, HToWWTo2L2Nu 90.50 fb (UL18). `SUMMARY_STITCH.md` will carry the WRONG absolute R —
apply the correction before quoting anything.

### MiniAOD exact-subtraction job — ✅ segfault fixed, RAN on condor 2026-09-29/30 → results in §3d
> Segfault cause: `pr.first.key()` on the `RefToBase` inside `slimmedGenJetsFlavourInfos` crashes FWLite for some entries. Fix: the AssociationVector is 1:1 in order with `slimmedGenJets`, so use `finfo.value(j).getHadronFlavour()` by index (size equality checked, 0 mismatches). CMSSW_13_0_17 reads UL18 MiniAOD fine — no 10_6 needed. The original notes below are kept for history.
- Collections confirmed in both Run-2 UL18 MiniAODv2 and Run-3 22EE MiniAODv4: `slimmedGenJets`,
  `slimmedGenJetsFlavourInfos` (official hadron flavour), `packedGenParticles`, `prunedGenParticles`,
  `GenEventInfoProduct`, `LHEEventProduct`, and **`GenLumiInfoProduct` in the lumi tree** → the FxFx
  matching efficiency (and correct normalisation) can be computed natively, like GenXSecAnalyzer.
- Code: `fs_unc/gen/mini_fs.py` (FWLite: per jet, subtract constituents whose pruned mother chain reaches the
  H; writes raw sums per file + lumi accepted/tried counts) and `fs_unc/gen/mini_job.sh` (CMSSW_13_0_17,
  el8_amd64_gcc11, run inside `cmssw-el8`). Planned: one condor job per MiniAOD file + an aggregator
  (`mini_agg.py`, not written) → same JSON format → existing `plot_ratio.py` / `compare_ratios.py`.
- **Status: the 300-event test on a Run-2 UL18 WW 3FS file SEGFAULTS inside FWLite** (log
  `fs_unc/logs/test_mini.log`; test file in `fs_unc/test_mini_file.txt`). Suspects, in order: (1) reading a
  10_6 UL MiniAOD with CMSSW_13_0 — try CMSSW_10_6_X (slc7) for Run-2, 13_0_X for Run-3; (2) `jet.daughter(d)`
  on slimmedGenJets returning a bad/null ref; (3) the `GenLumiInfoProduct` loop. Debug by bisecting the script.
- The three comparisons to run once it works: Run-3 era consistency, Run-2 γγ vs WW (decay transfer),
  Run-2 vs Run-3 γγ (energy) — 3FS vs **4FS FxFx**, c-jets pT>10.


## 3d. RESULTS — MiniAOD exact Higgs-constituent subtraction (2026-09-30) — CURRENT
**Method:** official `slimmedGenJets` + official `hadronFlavour` (`slimmedGenJetsFlavourInfos`). For every jet,
constituents whose ancestry reaches the H are subtracted from the jet momentum (no reclustering, no jet
removal). c-jet = hadronFlavour 4, **subtracted** pT > 10, |η| < 2.4. 3FS vs **4FS FxFx**. Normalisation: 4FS FxFx
= XSDB (cross-checked with `GenLumiInfoProduct`, above); 3FS = lumi `lheXSec` (= XSDB 49.87 / 54.97 fb exactly).
**Jobs:** condor cluster 9472853, 1776 jobs (one per MiniAOD file), submit dir `~/fs_mini_condor/` (AFS),
per-file output `fs_unc/mini/<sample>/<i>.json`, aggregator `fs_unc/gen/mini_agg.py`, results
`fs_unc/mini_results/mini_<sample>.json`, weight table `fs_unc/mini_results/weight_table.md`.
**Statistics:** 100% of files processed for 5 of 6 samples (e.g. Run-3 22postEE: 3.9M 3FS + 7.6M 4FS FxFx events;
Run-2 WW 4FS FxFx: 19.8M events).

**⚠️ 2022preEE is missing:** its MiniAOD (3FS and 4FS FxFx) sits only on **tape** (T1_US_FNAL_Tape /
T1_FR_CCIN2P3_Tape) + two unreachable T3s; all 159 jobs failed to open the files. Needs a Rucio disk-replica
request (user decision). Three Run-3 eras are available; they agree (below).

| sample | R_incl | **R(≥1c)** | R(0c) | f3/f4 | σ3FS [fb] | σ4FS FxFx [fb] |
|---|---|---|---|---|---|---|
| Run 3 2022postEE | 0.563 | **0.659** | 0.502 | 1.171 | 54.97 | 97.62 |
| Run 3 2023 | 0.563 | **0.663** | 0.500 | 1.177 | 54.97 | 97.62 |
| Run 3 2023BPix | 0.563 | **0.659** | 0.502 | 1.170 | 54.97 | 97.62 |
| Run 2 UL18 γγ | 0.550 | **0.660** | 0.481 | 1.200 | 49.87 | 90.67 |
| Run 2 UL18 WW | 0.551 | **0.657** | 0.486 | 1.192 | 49.87 | 90.50 |

**3FS/4FS-FxFx difference in the ≥1c region: ~34%** (R ≈ 0.66) — the paper's γ+c number is ~0.62 (38%).

**The three comparisons (per-bin pulls, χ²/ndf on absolute R):**
| comparison | c-jet pT (≥1c) | pT(H) (≥1c) | pT(H) (0c) | lead jet pT (0c) | pT(H) (incl) |
|---|---|---|---|---|---|
| Run-3 eras (2023, 2023BPix vs 22postEE) | 10.1/8, 9.5/8 | 2.0/7, 2.6/7 | 8.3/7, 3.3/7 | 3.7/8, 7.4/8 | 4.9/7, 2.1/7 |
| Run-2 γγ vs WW (decay transfer) | **14.1/8** | 8.7/7 | 6.6/7 | **486/8** ⚠️ | 6.6/7 |
| Run-2 vs Run-3 γγ (energy) | 11.3/8 | 10.3/7 | **92/7** | **57/8** | **95/7** |

Reading:
1. **Era consistency: passes** (all χ²/ndf ≈ 1).
2. **γγ → WW transfer in the ≥1c region: passes.** R(≥1c) agrees to 0.4% (0.660 vs 0.657); f3/f4 to 0.6%. c-jet
   pT χ²=14.1/8 (p≈0.08, driven by the 30–45 GeV bin, −2.3σ) — acceptable. With the old NanoAOD uncleaned jets
   this was 81/7 → **the exact subtraction fixes the decay contamination.** ⚠️ The 0c leading-jet pT disagrees
   strongly (486/8, WW higher at low pT); the ≥1c weights do not use it, but the cause is **not yet understood**.
3. **Energy (13 → 13.6 TeV): the ≥1c region transfers** (11.3/8, 10.3/7). The 0c/inclusive pT(H) differ only in
   the first bin (0–15 GeV, +9.5σ) — an energy/tune effect in the 0c region, which gets weight 1 anyway.
4. NanoAOD overlap-removal (FxFx-fixed) gave R(≥1c) = 0.664–0.673 → removing whole jets moves R by ~1–2% vs exact
   subtraction; exact subtraction barely changes the number of c-jets above 10 GeV (0.03%) but shifts their pT.

**Weights w(pT) = R — Run-3 era-combined (22postEE+2023+2023BPix), applied to 4FS-FxFx events with ≥1 GEN c-jet:**
| leading GEN c-jet pT [GeV] | Run 3 combined | Run 2 γγ | Run 2 WW |
|---|---|---|---|
| 10–20 | 0.761 ± 0.003 | 0.757 ± 0.006 | 0.746 ± 0.004 |
| 20–30 | 0.620 ± 0.003 | 0.623 ± 0.007 | 0.615 ± 0.004 |
| 30–45 | 0.583 ± 0.004 | 0.601 ± 0.008 | 0.580 ± 0.005 |
| 45–60 | 0.571 ± 0.005 | 0.563 ± 0.010 | 0.562 ± 0.007 |
| 60–80 | 0.580 ± 0.006 | 0.564 ± 0.012 | 0.585 ± 0.009 |
| 80–110 | 0.584 ± 0.009 | 0.570 ± 0.018 | 0.581 ± 0.013 |
| 110–150 | 0.647 ± 0.015 | 0.600 ± 0.030 | 0.645 ± 0.020 |
| 150–∞ | 0.630 ± 0.021 | 0.678 ± 0.043 | 0.605 ± 0.028 |
(uncertainties = MC stat only; no scale envelopes in the MiniAOD pass.)

**Plots:** [CERNBox `fs_unc/plots/stitch_mini/`](https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/fs_unc/plots/stitch_mini) — one folder per sample + `comparisons/` (`run3_eras_*`, `run2_GG_vs_WW_*`, `run2_vs_run3_GG_*`, with `.txt` tables).

**Still open:** (a) 2022preEE tape recall; (b) the 0c lead-jet γγ/WW discrepancy; (c) scale envelopes (need
LHE weights in `mini_fs.py`); (d) how to get the same subtracted GEN c-jet into the framework signal (NanoAOD
has no constituents — options: a MiniAOD-side friend column, or accept NanoAOD overlap removal, ~1–2% on R);
(e) framework steps, only when the user says go.


## 3e. C-HADRON definition — CURRENT APPROACH (2026-09-30)
**Why:** the MiniAOD c-jet study is not usable in the framework (no MiniAOD there). User proposed using the
GEN **c-hadron** instead of the c-jet: it is stored in NanoAOD `GenPart` (Run 2 v9 and Run 3 v13, status 2), so the
derivation and the framework can use the identical definition, and the Higgs decay cannot touch it.
**Definition:** leading weakly-decaying open-charm hadron (|pdgId| 4xx/4xxx, charmonium 44x excluded, no c-hadron
daughter so D*→D counts once), not from a b-hadron, |η|<2.5, pT > T. **T = 5 GeV primary, 10 GeV variation**
(c-hadron carries ~60% of the c-jet pT; the paper's c-jet pT>10 split ≈ hadron 5–7 GeV). Regions: ≥1 c-hadron →
weight w(pT) = σ(3FS)/σ(4FS FxFx); 0 → weight 1. 4FS FxFx normalised to XSDB.
Script `fs_unc/gen/derive_chad.py`, driver `gen/run_chad.sh` (tmux `chad`, lxplus971), outputs
`fs_unc/chad/<sample>_T{5,10}.json`, logs `logs/chad_*.log`.

**Run-2 γγ vs WW (the decisive check) — PASSES** (all 192 γγ and 72 WW files, 0 skips):
| | R(≥1 c-had) γγ | WW | c-hadron pT χ²/ndf | pT(H) ≥1c χ²/ndf |
|---|---|---|---|---|
| T = 5 GeV | 0.700 | 0.701 | 13.1/9 | 6.6/7 |
| T = 10 GeV | 0.645 | 0.642 | 12.1/8 | 5.1/7 |
Per-bin weights (T=5): 0.78 (5–10), 0.71 (10–15), 0.62 (15–20), 0.58–0.62 (20–110), ~0.6–0.7 above; γγ and WW agree
bin by bin within ≤2.3σ (one bin, 20–30 GeV). Table: `fs_unc/chad/run2_GG_vs_WW_weights.md`; plots
`fs_unc/plots/stitch_chad/comparisons/`. The 0c/inclusive pT(H) show a ~1.5σ coherent offset from the 0.8%
3FS Σw/N difference between the two 3FS samples (50.06 vs 50.44 fb) — irrelevant for the ≥1c weights.
**Pending:** Run-3 eras (incl. 2022preEE, NanoAOD is on disk) and Run-2 vs Run-3; then the card bracket.


### 3e-bis. Uncertainty budget: reweighting vs true stitching vs Run-2 recipe (2026-09-30)
From the stored 7-point envelopes (`fs_unc/chad/unc_budget.md`, script `gen/unc_budget.py`), ≥1 c-hadron (T=5), H→WW Run 2:
| source | per bin | integrated ≥1c |
|---|---|---|
| 4FS-FxFx scale (what the signal carries today) | +8…+20 / −6…−13% | +14/−9% |
| **3FS scale (what true stitching carries)** | ±14…22% | **+21/−19%** (Run 3 postEE: +20/−19%) |
| weight MC stat | 0.4–1% below 30 GeV, 2–7% above | 0.2% |
| γγ→WW transfer | ≤4.5% (21% in 110–∞, 1.6σ, stat-limited) | 0.3% |
| definition T=5 vs 10 GeV | identical weights above 10 GeV; only events with leading c-hadron 5–10 GeV change (41% of 4FS ≥1c GEN events, weight 0.78 vs 1) | stitched total −4.5%; reco-level impact ≤ this, to be measured |
**Key implementation point:** propagate the scale uncertainty with scale-varied weights w_k(pT) = σ3FS_k/σ4FS_nom, which
reproduces the 3FS envelope exactly (as true stitching would). Do NOT use 4FS LHEScaleWeight × w — that gives the 4FS
envelope (+14/−9%) and underestimates. Totals in ≥1c: Run-2 recipe ≈ 4FS scale ⊕ 30% ≈ ±31–33%; true stitching ≈ ±20%
(+ poor 3FS MC stat); reweighting ≈ ±20% ⊕ ≤4.5% ≈ ±20.5%.

**Framework steps (ONLY after user says go):**
1. GEN columns on the H+c signal: `gen_ncjets`, `gen_cjet1_pt` with the **SAME definition as the
   derivation** — pT>10, |η|<2.4, hadronFlavour==4, and **excluding GenJets within ΔR<0.4 of the H→WW
   decay products** (leptons, τ products; not ν) — **to be replaced by the exact MiniAOD definition above**. `select_gen_fs` is drafted (threshold 20, no cleaning) →
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
