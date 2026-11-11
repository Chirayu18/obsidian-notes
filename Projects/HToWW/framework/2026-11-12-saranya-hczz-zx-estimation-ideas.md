---
tags: [reference]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---
# Saranya's HcZZ `HcZZ-zx-estimation` branch: what is worth taking for HToWW

Chirayu asked on 2026-11-12 for ideas from https://github.com/Saranya-Nandakumar/higgscharm/tree/HcZZ-zx-estimation. His rule from 2026-11-05 applies: take only what is useful for us, nothing HZZ-specific.

- **Commit read:** `f508f59af34a36579c13c883c840d64c29203324` (2026-11-06, Saranya Nandakumar, "Parquet-mode postprocess: fix merge, cutflow and plotting").
- **How it was read:** a read-only shallow clone in `/tmp/hczz-zx-clone/repo` (depth 300). Only source and README were read. None of her scripts were run.
- **Our side:** lxplus `~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`, branch `hww-analysis`, HEAD `f84d311` plus uncommitted work (39 entries in `git status --short`). This was read-only too; workflow `hww_allfix_4fs.yaml`.
- **Earlier comparison:** [[2026-11-05-saranya-hczz-branch-comparison]]. Since commit `7962523` (the one we ported from), the only new commit is `f508f59`. Everything else below was on the branch before, but the 11-05 survey did not assess it for a fake-lepton estimate.
- **Related:** [[Projects/HToWW/analysis-strategy/2026-11-10-run3-central-hww-code-comparison|2026-11-10 central HWW comparison]], rows "Fake/nonprompt background" and "Background constraints", and plan item 2. [[Projects/HToWW/selection-and-mva/2026-08-12-lepton-mva-nonprompt-diagnostic|2026-08-12 nonprompt diagnostic]].

Nothing here was implemented or tested. These are recommendations from reading the code.

## What the branch adds (Z+X = reducible 4ℓ background)

The Z+X pipeline is in `scripts/README.md`, stages 0 to 5. It is the HZZ fake-rate ("matrix") method from AN-18-340 / HIG-24-013.

| stage | file | what it does |
|---|---|---|
| FR measurement region | `analysis/workflows/zplusl_ss.yaml`, `zplusl_os.yaml` | Z(tight, tight) plus exactly one extra "relaxed" lepton, with `PuppiMET < 25`. Histogram axes: probe pT (bins 5, 7, 10, 20, 30, 40, 50, 80), \|η\| (50 bins, later rebinned to 5), lost hits, barrel flag, pass-tight flag. |
| FR computation | `scripts/compute_fake_rates.py` | f = N_tight / N_loose in data, per flavour, on a pT × \|η\| grid. Uncertainty is binomial. A "corrected" version subtracts WZ MC (data − WZ). The default `safe_corrected` silently falls back to the uncorrected rate in bins where the subtraction goes negative. Output is a pickle. A correctionlib JSON version exists in `analysis/data/fake_rates/<era>_os_fr_weight.json.gz` (pT × barrel × flavour). |
| application regions | `analysis/workflows/hplusc_mva_4class_CR_merged.yaml` | Same processing pass with categories `CR_3P1F` (one Z2 lepton loose-not-tight), `CR_2P2F` (both fail) and `CR_SS`. Per-lepton `is_tight` columns are written to parquet. |
| estimate | `scripts/estimate_zx_background.py` | Per-event weight f/(1−f) for 3P1F and −f1f2/((1−f1)(1−f2)) for 2P2F. Prompt ZZ in 3P1F is removed by one global scalar, (1 − N_ZZ^MC / N_3P1F). CR stat uncertainty is sqrt(Σw²). Output is weighted parquets with `zx_weight`. |
| scoring | `scripts/run_zx_inference.py` | Runs the SR classifier on the weighted application-region events to get Z+X templates. |
| validation | `validate_zx_mc_shape.py`, `validate_zx_reducible_features.py`, `validate_zx_sideband_features.py` | Score shapes of data-driven vs FR-weighted MC reducible; feature distributions in CR vs SR vs sideband. |
| fit | `combine/scripts/create_datacards_ctag2d_100150.py` | Z+X is one process with `ZX_norm` 30% lnN. The free `ZX_rate` rateParam was **removed** in commit `fac4bf1`. |

**Production state.** Her headline with-ZX cards use pkatris's OS fake rates, not her own `compute_fake_rates.py` output (`README_HcZZ.md` line 109). Her SS cross-check `estimate_zx_ss_crosscheck()` is recorded as broken: about 500× the OS yield (README "Update 2026-09-14").

## Candidates for HToWW, ranked

### 1. Adopt now (a rule, no code change): no free rateParam without a constraining CR, and no silent fallbacks
- **What:** commit `fac4bf1`. Her free `ZX_rate [0.1,10]` had no Z+X control region in the fit, so only the SR Asimov constrained it (−42%/+55%). It double-counted `ZX_norm` and inflated the Z+X impact. The same commit makes `estimate_zx_background.py` raise when sumw or xsec is missing. Before that, a deleted input directory had silently set the ZZ correction to 1.0 in every era.
- **Why it helps us:** our card has `rate_params: [tt]`, which is constrained by `CR_tt`, and `vjets` has no rateParam. That is already correct. The rule matters when we add a data-driven Fake process, or revisit the V+jets rateParam the 11-10 note mentions. Give Fake an lnN plus FR shape nuisances. Let it float only if a fake-enriched CR, such as same-sign eμ, is in the fit.
- **Effort, risk:** none to adopt as a rule. Auditing `make_combine_inputs.py` for silent 0/1 fallbacks (missing sumw, xsec or files) would take about an hour, read-only.
- **Physics, reprocessing:** none.

### 2. Adopt now (diagnostic): check freeze-proxy impacts against real profile-likelihood impacts before quoting a ranking
- **What:** `README_HcZZ.md`, "Update 2026-08-30 — `--real` flag". On her card, the freeze-one-nuisance proxy put two nuisances in a near-tie for #1 and gave `CMS_eff_m_id` exactly 0. Real `combineTool.py -M Impacts --robustFit 1` put `CMS_ctag2d` clearly first (about 3.2× the #2) and gave `CMS_eff_m_id` a nonzero impact. Two more points from the same section:
  - CombineHarvester's default r range of [0, 20] is far too narrow for r of order 100 to 1000.
  - A nuisance whose limit *improves* when frozen usually points to degeneracy with a free rateParam.
- **Why it helps us:** our config has `impacts: {method: freeze_per_nuisance}` (`hww_allfix_4fs.yaml` `combine.run`). Our deck rankings come from that same proxy, which her analysis found can reorder the ranking.
- **Effort, risk:** small; one Impacts run on an existing card on lxplus, with a wide `--setParameterRanges r=…`. The script she used, `impact_ranking.py`, is in her separate b-hive_ttcc area and **not** on this branch. Use the standard CombineHarvester commands instead.
- **Physics, reprocessing:** none. Fit diagnostic only.

### 3. Later, as the template for our fake-lepton study (11-10 plan item 2): the tight-to-loose structure, not her code
For eμ, W+jets and semileptonic tt with one fake lepton are the analogue of her Z+X. Today they come from MC (V+jets with negrw, xsec lnN 2.7%), and negrw does not measure fake rates in data. Three pieces of her structure carry over to eμ:
- **Application region in the same processing pass.** Add a loose-not-tight lepton category with per-lepton `is_tight` columns, as in `hplusc_mva_4class_CR_merged.yaml` categories `CR_3P1F`/`CR_2P2F`. The eμ analogue is 1T1F (weight f/(1−f)) and 0T2F (subtract f1f2/((1−f1)(1−f2))).
- **Score the application-region events with the same classifier** (`run_zx_inference.py` pattern) to get the Fake templates in every SR/CR channel. Our `scripts/mva/run_inference.py` would do this job; her script is not needed.
- **Ship the FR map as correctionlib JSON** per era (`analysis/data/fake_rates/*.json.gz`), not as pickles.

Where our study must differ (be candid: copying her shortcuts would be wrong for us):
- **Measurement region.** Hers is Z+1ℓ with MET < 25. The central HWW code uses QCD-enriched single-lepton data with fakeW (11-10 note). Either can work, but our SR is c-tagged, so fakes come largely from heavy-flavour jets. The FR, or a composition systematic, must account for jet flavour. Hers ignores this, since 4ℓ has no c-tag in the FR.
- **Prompt subtraction in the application region.** She uses one global scalar for ZZ. In eμ, dilepton tt with a real lepton failing tight is a large prompt component. It must be subtracted **per event** with MC weighted by the same f/(1−f), or the Fake estimate double-counts tt, which is already in the fit with `rate_tt`.
- **Measurement-region subtraction.** She subtracts WZ only. Her `compute_fake_rates.py` adds `.coffea` histograms directly (`load_zplusl_histograms`) and applies no visible xs × lumi / sumw scaling before `data − WZ`. I did not check whether those histograms are already normalised, so the corrected FR may be mis-normalised (unverified). In any case the `safe_corrected` silent fallback is the kind of thing rule 1 forbids.
- **Loose WP.** We would need a loose lepton definition below our tight ttH-MVA WP (`hww_allfix_4fs.yaml` muons/electrons). Thomas's ttH-MVA WPs and SFs are tied to tight, so this needs his input.
- **Closure.** She has shape comparisons only (validate_zx_*). We need a normalisation closure as well: apply the MC-measured FR to the MC application region and compare with genPartFlav-nonprompt MC in the SR (our 08-12 diagnostic already classifies prompt vs nonprompt by `genPartFlav`).
- **Systematics.** Her treatment is a flat `ZX_norm` 30% lnN, cited to HIG-24-013's 25 to 46% range, which combines CR stat, FR ±1σ and composition. For us, the central HWW nuisances (`D/nuisances.py:482–536`: e/μ FR stat and syst) are the better model. Her pieces worth keeping are the per-event `zx_weight_sq` for CR stat and a `zx_weight_up` FR variation column.

**Effort:** large, several weeks. It needs a new loose-lepton output (a TRAIN/RUN **reprocessing** of data and MC with loose-not-tight leptons kept), a measurement-region workflow, prompt subtraction, closure and new nuisances.
**Changes physics:** yes. It replaces the MC V+jets/fake component with a new process. The classifier need not be retrained to apply it, but if Fake replaces the `vjets` class's training sample the class definition would change.
**Risk:** double counting with tt and V+jets MC if prompt matching and subtraction are not consistent.
**Recommendation:** later. Start with the cheap gate from the 08-12 diagnostic and the 11-10 note: measure the nonprompt fraction per channel (SR_hplusc_1cj/2cj, CR_vjets) in MC with `genPartFlav`. If it is small, an MC estimate with an inflated uncertainty may be enough (Gerrit's remark in `negative-weights/ProposedFix-Automcstats.md`).

### 4. Not needed unless the error appears: list vs large_list parquet merge (`f508f59`, `analysis/postprocess/utils.py::concat_tables_schema_safe`)
- **What:** it casts jagged columns written as `list` in some shards and `large_list` in others to `large_list` before merging. Without it the merge fails with "ArrowInvalid: Unable to merge".
- **Us:** `merge_parquet_files` in our `analysis/postprocess/utils.py` (about line 156) uses `pa.concat_tables(..., promote_options="default")`. HWW parquets are mostly flat scalar columns. I did not check whether we write any jagged column or whether "default" promotion unifies these types.
- **Recommendation:** not now. Port the 12-line cast only if we hit that ArrowInvalid. The other two parts of `f508f59` (cutflow `errors="ignore"`, plotting every layout axis from parquet) are about her own plotting path. We have not seen those failures.

### 5. Not useful for HToWW (HZZ-specific or already covered)
- **4ℓ-specific pieces:** Z1/Z2 pairing, FSR photons, the ZZ-in-3P1F scalar correction, the 4e/4μ/2e2μ final-state split, the AN-18-340 Eq. 11 SS cross-check (also broken), and the m4l-window logic (`load_zx_parquets` windowing fix).
- **Her 4-class MLP inference and studies:** `run_zx_inference.py` as code, `compute_roc.py`, `compute_feature_importance.py`, `compare_inference_sensitivity.py`. We have our own b-hive/`run_inference.py` chain.
- **Her `compute_fake_rates.py` / `estimate_zx_background.py` as code:** hard-coded `/eos/user/s/snandaku` paths, row-by-row pandas loops, pickles, the WZ-only subtraction and the silent fallback. Rewrite for our selection instead of porting.
- **c-tag items** (`_decorr` builders, per-era edges): already listed on 11-05 and parked ("no ctag", 10-29; c-tag results provisional pending Livio).
- **Job and fileset infrastructure:** nothing new. Her `bookkeeping.py` job check became our `scripts/check_train_outputs.py`. Our `jobs_status.py` already covers what her branch has, with resubmission, fileset regeneration/merge and xrootd-error grouping by site. Her README trap "2022postEE ZZto4L only 7/14 coffea, silent xrdcp failures" is the case our completeness check exists for.
- **Already ported or recorded on 11-05:** `eos_io` listing, alphaS sign, scale-label swap, correctionlib pins, xrdcp retry, the DY-invalid finding, and the 25-character nuisance-name trap.

## Not checked
- Whether her zplusl `.coffea` histograms are lumi-normalised before the WZ subtraction (item 3).
- Whether our parquets contain jagged columns (item 4).
- No number in this note was recomputed. Yields and limits quoted from her README (e.g. 35.9 ± 4.5 Z+X events; limit 353.0 → 352.5) are hers, unverified.
