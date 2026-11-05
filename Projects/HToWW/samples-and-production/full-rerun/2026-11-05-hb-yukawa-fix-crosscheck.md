---
tags: [reference, validation]
status: active
date: 2026-11-05
source: laptop
evidence: agent-reported
---

# H+b running-Yukawa fix: cross-check on 2022 central NanoAOD (P0-16)

Task HTOWW-HB-YUKAWA-XCHECK, asked for by Chirayu on 2026-11-05. It cross-checks the per-event scale-weight fix (`lhe_yukawa_fix.py`) for the central `HPlusBottom_5FS_MuRFScaleDynX0p50-HToWWTo2L2Nu` FxFx sample, with the same tests that validated H+c. The consumer is the FULLFIX worker ([thread](t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:0a085f5f6123e902dae945a412fbaac27624ff7a2dd345a25861a529c4e14fb5)). Background is in [[Projects/HToWW/samples-and-production/2026-10-13-central-signal-lhe-and-fxfx-issue]] and [[Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings]].

Every number here is agent-reported. Chirayu has not reviewed it.

## Verdict

- **Scale-weight fix for H+b: VALIDATED** (agent check), at the same level as H+c.
  - The table is exact.
  - The scale inversion closes to 0.04%.
  - μF agrees with clean H+b to 0.2%.
  - At equal scale the per-event weights agree with two clean H+b samples to ≤0.5% (median).
  - In the analysis-like region (≥1 gen b-jet) every entry is within ≤2.3% of clean Run 3 γγ H+b. That is inside the γγ–UL18 spread.
- **Caveat, inclusive only:** the μR-down family is 4–7% below the clean samples (μR0.5 0.966 vs 1.012). Inclusively, μR Up and Down are then both < 1 (0.995 / 0.966).
  - This is **not** the fix. Our MG 2.9.18 sample has fewer low-scale one-jet events and fewer 1 GeV floor events: NpNLO=1 is 29% of the weight vs 39% (γγ) and 38% (UL18). H+c has the same composition difference.
  - Reweighting cannot correct it. Inside the b-jet region it disappears.
- **Separate finding, NOT part of the scale fix: the H+b PDF/αs path is biased.** `lhe_norm.py` normalises each PDF member by its global Runs-tree mean, and `lhepdf.py` then centres on the replica mean. Together they remove the inclusive normalisation part of each member:
  - lhe_pdf Up/nom: **1.0145** vs clean **1.0217** (γγ) / 1.0216 (UL18).
  - lhe_alphaS Up/nom: **1.000** vs clean **1.030**.
  - Dividing the members by the per-event r instead gives PDF 1.0205–1.0208 (close to the clean value) and αs 1.044. αs is not exact this way, because the clean Fortran weights also run m_b with the varied α_s.
  - Whether this matters depends on how the signal PDF/αs normalisation enters the cards. If it comes from lnN on the cross section, only the shape is used. **Decision for Chirayu / the FULLFIX worker.**
  - **Later context (keeper, 2026-11-05):** the [[Projects/HToWW/2026-11-05-sol-review-unpushed-work|independent review, 9aa71d5]] finds the H+c sample has no αS members at all (LHA 325500–325600, PDF-only symmetric Hessian), so no per-event repair can supply H+c αS; the Hessian sum correctly has no `/99`. The PDF/αS choice stays open for Chirayu.

## What was run

Nothing was submitted and nothing in the analysis repo was edited. The repo stays read-only; the FULLFIX worker owns its edits.

- The fix modules were copied from the working tree to node-local `/tmp/cgupta_hbx/repo` on lxplus921: `lhe_yukawa_fix.py`, `lhescale.py`, `lhe_norm.py`, `lhepdf.py` and `analysis/data/lhe_yukawa/`.
- The md5 sums of the copy are recorded in `SNAPSHOT.txt`. The repo HEAD is `b7f67ef` plus uncommitted edits. `hplusbottom_5fs_table.txt` md5 is `426c6ae5…`.
- Container: `coffea-base-almalinux9:0.7.30-py3.10`.
- Scripts and logs: `/eos/user/c/cgupta/higgscharm/runall/hb_xcheck_20261105/` (`hb_xcheck.py`, `hb_xcheck2.py`, `hb_xcheck3.py`, `run*.log`).
- Results JSON and plots: `/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/hb_xcheck_20261105/`.

The input files were copied with xrdcp to `/tmp/cgupta_hbx/files`:

| label | dataset | file | events used |
|---|---|---|---|
| HB_22EE | Run3Summer22EENanoAODv12 H+b 5FS WW (broken) | `…/120000/3c787671-63b2-4888-bbd7-2752e622b8e4.root` (eoscms) | 29,700 |
| HB_22 | Run3Summer22NanoAODv12 H+b 5FS WW (broken) | `…/2560000/248c65ec-5738-4863-a134-edbfabccd6a5.root` (global redirector) | 176,622 |
| HC_22EE | Run3Summer22EENanoAODv12 H+c 4FS WW (broken), comparison | `…/2520000/27982ec7-6713-495c-b35c-4058f99feadc.root` | 85,732 |
| REF_HBgg_22EE | Run3Summer22EENanoAODv13 `HPlusBottom_5FS_…_HTo2G_…amcatnloFXFX` (clean) | `…/2560000/d65fc54a-efac-4980-93dd-de2a938244a9.root` | 200,000 |
| REF_HB_UL18 | RunIISummer20UL18NanoAODv9 H+b 5FS WW FxFx (clean, 13 TeV) | `…/40000/57D2984A-0301-0244-882E-51DF66B0CBBC.root` | 132,102 |

## 1. Yukawa table vs the H+b patch

- **The gridpack the sample used** (from fragment HIG-Run3Summer22EEwmLHEGS-02645 / -02697): `/cvmfs/cms-griddata.cern.ch/phys_generator/gridpacks_tarball/pp/13p6TeV/madgraph/HPlusBottom/HPlusBottom_5FS_MuRFScaleDynX0p50_M125_TuneCP5_13p6TeV_amcatnloFXFX_pythia8_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`.
  - It is MG **2.9.18**, our own build.
  - `runcmsgrid.sh` runs the python `systematics` module (line 149).
  - The run_card has `reweight_scale/PDF = False` and `store_rwgt_info = True`.
  - So the cause is the same as for H+c.
  - The cvmfs directory also holds a `…_original_before_lhe_weight_checker_patch` tarball (Apr 2026). The patch it refers to only adds an LHE weight-count check (runcmsgrid.sh l.208).
- **Cards.** The gridpack `InputCards/` `_mg5amc.patch`, param_card and run_card are byte-identical (`cmp`) to `/eos/home-c/cgupta/HToWW/mcm_grid/genproductions_scripts/bin/MadGraph5_aMCatNLO/HPlusB/`.
  - The build log shows the patch applied cleanly to `extra_weights.f`, `reweight_xsec.f` and `fks_singular.f` (fks_singular offset 119).
- **The patch for H+b.**
  - `mbmb = MDL_YB*vev/√2`, with ymb = **4.18** (param card).
  - The reference scale is `mbmb` itself, i.e. m̄_b(m̄_b).
  - **nf = 5**, 4-loop running to μ0 and 2-loop for the variation step.
  - `cpower = 2`, `runfac = 1`.
  - α_s(MZ) comes from the PDF; lhaid **325300** gives **0.1180021** (LHAPDF).
- **The table matches the patch.**
  - `tab.f` takes stdin `4.18 0.0 5.0 α_s`; refscale 0 means "use mbmb", which is the patch's choice.
  - It uses the same MZ = 91.188, aEWM1 = 132.507 and Gf = 1.16639e-5 as the param card.
- **Bit-exact rebuild from the real H+b build.**
  - Source: the patched `reweight_xsec.f` of the actual H+b build area (`…/HPlusBottom_…_gridpack/work/HPlusBottom_…/SubProcesses/reweight_xsec.f`, MG 2.9.18).
  - Its `runalpha`/`runmass` block is identical to the repo's `rundec.f` (taken from 2.9.10).
  - Compiling `tab.f` against it and running `4.18 0.0 5.0 0.1180020801` reproduces `hplusbottom_5fs_table.txt` with **max relative difference 0.0** (6001 rows). The H+c table rebuilds bit-exactly too.
  - Rebuilt table: `runall/hb_xcheck_20261105/hplusbottom_5fs_table_rebuilt_from_2918_build.txt`.
- **Table values:**
  - F(1 GeV) = 2.160, F(m_b) = 1.000, F(62.5 GeV) = 0.502.
  - At 1 GeV: F(0.5·μ0) / F(2·μ0) = 4.533 / 1.419.

## 2. Per-event r = mean(PDF 1–100) / member 0

| sample | median r | 1 / 16 / 50 / 84 / 99 % | frac r < 1.2 |
|---|---|---|---|
| HB_22EE | 1.993 | 1.221 / 1.566 / 1.993 / 1.994 / 2.088 | 0.91% |
| HB_22 | 1.993 | 1.201 / 1.566 / 1.993 / 1.994 / 2.080 | 1.00% |
| HC_22EE | 2.261 | 1.425 / 1.814 / 2.261 / 2.264 / 2.329 | 0.53% |
| REF_HBgg_22EE | 1.0001 | 0.9994 – 1.0003 | 100% |
| REF_HB_UL18 | 1.0001 | 0.9994 – 1.0003 | 100% |

- The H+b peak at 1.993 = 1/F(62.5 GeV) is the zero-jet Born at μ0 = mT(H)/2.
- The Runs-tree replica mean is 1.874 (22EE) / 1.877 (22). This matches the 1.88 noted on 2026-10-01.
- **After the fix**, the scale weights carry F(k·μ0; μ0). For every event inside the table range the PDF centre equals the replica mean, so r = 1 by construction.
- **Scale closure** (independent of the PDF): μ0 inverted from r, divided by 0.5·mT(H) of the LHE Higgs, for NpNLO=0 S-events.
  - H+b: median **1.0004** (16–84%: 0.9985–1.0009), both files.
  - H+c: 0.9962, the known 0.4% offset.
  - So the H+b table inverts to the right scale even more precisely than H+c.

## 3. Scale variations (sum w_var / sum w_nom)

The per-event fix uses the H+b table; the references use their stored (clean) weights. The order is (μR, μF) = (0.5,0.5) (0.5,1) (0.5,2) (1,0.5) (1,1) (1,2) (2,0.5) (2,1) (2,2).

**Inclusive:**

| sample | (0.5,0.5) | μR0.5 | (0.5,2) | μF0.5 | μF2 | (2,0.5) | μR2 | (2,2) |
|---|---|---|---|---|---|---|---|---|
| HB_22EE raw | 1.536 | 1.510 | 1.326 | 1.701 | 1.905 | 1.820 | 2.143 | 2.338 |
| HB_22EE fixed | 0.974 | 0.961 | 0.856 | 0.908 | 1.019 | 0.849 | 0.998 | 1.089 |
| HB_22 fixed | 0.975 | 0.966 | 0.864 | 0.907 | 1.020 | 0.845 | 0.995 | 1.086 |
| γγ H+b 22EE (clean) | 1.017 | 1.012 | 0.916 | 0.910 | 1.019 | 0.838 | 0.981 | 1.068 |
| UL18 H+b WW (clean) | 1.018 | 1.019 | 0.930 | 0.909 | 1.023 | 0.836 | 0.979 | 1.067 |
| HC_22EE fixed | 1.006 | 1.016 | 0.985 | 0.942 | 1.026 | 0.885 | 0.971 | 1.027 |

**≥1 gen b-jet** (hadronFlavour 5, pT > 20, |η| < 2.4; c-jet for H+c). This is about 33% of the events.

| sample | (0.5,0.5) | μR0.5 | (0.5,2) | μF0.5 | μF2 | (2,0.5) | μR2 | (2,2) |
|---|---|---|---|---|---|---|---|---|
| HB_22EE fixed | 1.054 | 1.110 | 1.141 | 0.893 | 1.081 | 0.769 | 0.893 | 0.992 |
| HB_22 fixed | 1.065 | 1.109 | 1.127 | 0.902 | 1.071 | 0.775 | 0.892 | 0.983 |
| γγ H+b 22EE (clean) | 1.079 | 1.122 | 1.138 | 0.904 | 1.068 | 0.776 | 0.892 | 0.982 |
| UL18 H+b WW (clean) | 1.096 | 1.142 | 1.161 | 0.906 | 1.067 | 0.772 | 0.884 | 0.971 |

The γγ GenJets include the photons, so the b-jet region of the γγ reference is only approximate.

**Framework path:** `lhescale.add_scalevar_weight` with `yukawa_table`, coffea `Weights`, first 50k events. The values are Up / Down:

| | muR | muF | muRmuF |
|---|---|---|---|
| HB_22EE fixed | 0.998 / 0.961 | 1.019 / 0.908 | 1.089 / 0.974 |
| HB_22 fixed | 0.994 / 0.968 | 1.026 / 0.905 | 1.089 / 0.973 |
| HC_22EE fixed (same script) | 0.969 / 1.020 | 1.025 / 0.943 | 1.024 / 1.010 |
| HB_22EE raw (no fix) | 2.14 / 1.51 | 1.91 / 1.70 | 2.34 / 1.54 |

- H+b fixed spans **0.905–1.089**, inside the H+c envelope of 0.91–1.10 quoted in the brief.
- On this H+c file the same script gives 0.94–1.03.
- Up/Down are now Up = ×2 and Down = ×0.5 (the 2026-10-29 swap fix), and they match the array-level numbers.

**Where the inclusive μR-down gap comes from.** These are classes by NpNLO and S/H (parton count from LHEPart), with `hb_xcheck2/3.py`:

- **NpNLO=0 S** (43% of the weight): fixed vs γγ ≤0.5% on every entry (μR0.5 0.655 vs 0.657).
- **Same scale bins** (0.5·pT of the hardest LHE parton), median μR0.5:
  - NpNLO=1 S: WW vs γγ vs UL18 within ≤0.5% for 0.5·pT < 60 GeV (e.g. 1.567 / 1.573 / 1.557 at 15–20 GeV).
  - NpNLO=1 H: ≤0.4% in every bin (e.g. 1.634 / 1.641 / 1.640).
  - The weighted means per bin scatter by ±5% between the two clean references themselves, because of the 30% negative weights.
- **1 GeV floor events** (μR clamped by MG):
  - The clean H+b samples have constant ratios μR0.5 = **4.233** and μR2 = **0.3276** (1.3% of NpNLO=1 H events, 4.8% of the class weight, in both γγ and UL18).
  - The fix gives **4.232 / 0.3276** for our floor events (165 events in HB_22, raw 0.934), i.e. exact.
  - H+c gives 6.199 / 0.308, also exact.
- **Composition (nominal, not weights):**
  - NpNLO=1 weight share: 29% (WW) vs 39% (γγ) / 38% (UL18).
  - Low-scale one-jet events (0.5·pT < 20 GeV) are rarer.
  - Floor events: 0.25% of NpNLO=1 vs 1.3% of NpNLO=1 H in the clean samples.
  - This is the MG 2.9.18 vs 2.9.9 / 2.6.5 difference already seen for H+c (2026-10-13).
  - It is the whole inclusive μR-down gap.

## 4. Guard (median r < 1.2 is refused)

- **H+b broken: accepted.** The median is 1.993, a 0.79 margin over the threshold. It is also accepted chunk by chunk (as the framework calls it) for chunks of 1000 / 10000 / 50000 events: 0 refusals in 30+3+1 (22EE) and 177+18+4 (22) chunks.
- **Clean γγ H+b and UL18 H+b: refused** ("median replicas/member0 = 1.000 …"). So the fix cannot be misapplied to a clean H+b sample or a future re-production.
- The H+b events with r < 1.2 (about 1%) are floor events (r = 1/F(1 GeV) = 0.463) and low-scale or two-scale events. They do not move the median.
- `correction_manager` only passes the table when the Runs tree has `LHEScaleSumw`. Both H+b files have it.

## 5. Fallback events

| sample | n | off-table (measured factor only) | fallback (ratio 1) | fallback per mille |
|---|---|---|---|---|
| HB_22EE | 29,700 | 2 | 3 | 0.10 |
| HB_22 | 176,622 | 7 | 21 | 0.12 |
| HC_22EE | 85,732 | 4 | 5 | 0.06 |

- The `lhescale` hard limit is n_fallback > max(10, 0.1%). It was **never hit**, in any chunk size.

## 6. PDF / αs (side finding)

These are framework sums Up/nom over the whole file. The members are normalised the `lhe_norm` way (each member divided by its Runs mean, member 0 replaced by the replica mean):

| sample | raw | framework fix | per-event r instead | clean γγ / UL18 |
|---|---|---|---|---|
| H+b lhe_pdf | 1.499 | **1.0145** | 1.0205 | 1.0217 / 1.0216 |
| H+b lhe_alphaS | 1.081 | **1.000** | 1.044 | 1.0295 / 1.0298 |
| H+c lhe_pdf (325500, 101 members) | 1.500 | 1.0749 | 1.0929 | (no clean ref in this run) |

- Dividing every member by its own global mean takes out the overall normalisation part of each member.
- For αs, which in these sums is essentially a normalisation effect, it removes the variation entirely.
- The per-event r recovers the PDF value, but overshoots for αs. In the clean Fortran weights the varied α_s also changes the m_b running inside F.
- The analysis effect depends on whether the signal PDF/αs normalisation is taken from these weights or from lnN. Not fixed here; **needs a decision**.

## Plots

These are linked from [[Projects/HToWW/plots|plots]].

- `hb_xcheck_r_and_mu0.png`: per-event r for H+b 22/22EE, H+c and the two clean H+b references. Also μ0 / (0.5·mT(H)) for the NpNLO=0 S-events.
- `hb_xcheck_scale_means.png`: the nine scale means, inclusive and in the b-jet region. It shows fixed H+b (with the raw values faded), the clean references and H+c.
- Path: `/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/hb_xcheck_20261105`
- Link: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/higgscharm/outputs/hww_lhe_fix/hb_xcheck_20261105

## Next / needs you

- [ ] P0-16 can be closed for the **scale** weights, as agent-validated. Chirayu should confirm.
- [ ] Decide on the H+b (and H+c) PDF/αs normalisation in `lhe_norm.py`/`lhepdf.py`. Options: keep it (shape only, normalisation from lnN), or switch to per-event r for the PDF members and take αs from the clean γγ H+b sample. Owner: the FULLFIX worker, who is the edit owner.
- [ ] Optional: inclusive μR-down for H+b is one-sided (0.995 / 0.966) because of the sample's composition. That is not a weight problem, but the GEN re-production request covers it.
- Deck: Chirayu asked for this in the existing full-rerun deck. The keeper owns it (`make slides` in the commit).
