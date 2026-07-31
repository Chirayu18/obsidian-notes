---
tags: [reference]
status: active
date: 2026-07-24
source: lxplus
---

# HToWW H+c — master systematics list + remaining work

Authoritative inventory of every nuisance in the live `hww_combine_2dcat` datacard,
what's **missing**, where each is **picked up from**, and the **references**. The
machine-readable version is [[HToWW-systematics-inventory.xlsx]] (also `.csv`).

Companion to [[2026-07-19-ctag2d-full-documentation]] and the run steps in
[[2026-07-24-run-analysis-steps]].

## 1. Systematics IN the card (live)

### 1a. Weight-based shape nuisances (`shape_systematics:` in workflow)
Emitted by the processor `Weights` container as `weight_<name>Up/Down`; combine morphs
nominal↔Up/Down.

| Nuisance | Processes | Picked up from | Reference |
|---|---|---|---|
| `pileup` | all MC | `pileup.py` (PileupWeights), LUM POG PU json | LUM POG; AN-23-102 §7 |
| `ps_isr`, `ps_fsr` | all MC exc. tt | `partonshower.py`, LHE PS weights | AN-23-102 §7.1 |
| `scalevar_muR`, `_muF`, `_muR_muF` | all MC exc. tt | `lhescale.py`, LHEScaleWeight | AN-23-102 §7.1 (QCD scale) |
| `muon_id`, `muon_iso` | all MC | `muon.py`, MUO POG SF json | MUO POG; AN-23-102 §6 |
| `electron_id` | all MC | `electron.py`, EGM POG SF | EGM POG |
| `electron_reco_{RecoBelow20,Reco20to75,RecoAbove75}` | all MC | `electron.py`, EGM reco SF (pt-binned) | EGM POG |
| **`CMS_ctag2d_2022`** | all MC | **`ctag2d.py` (CTag2DCorrector) — NATIVE as of 2026-07-24**; `ParticleNetAK4_pseudocontinuous` in `flavTaggingSF_2022postEE.json.gz` (cmshgg ingredients), `up_Total`/`down_Total` | cmshgg 2D_HF_Tagging; PNet AK4 pseudo-continuous |
| **`CMS_negrw_vjets`** | vjets | `base.py::_score_negrw` + `make_combine_inputs.py`; `negrw_models.joblib` (20× HistGradientBoostingClassifier), std-band | **arXiv:2510.16217** |

### 1b. Object-shift shape nuisances (separate shifted parquet trees, `object_shifts: true`)
| Nuisance | Picked up from | Reference |
|---|---|---|
| `CMS_scale_j_2022` (JES **Total**) | `jerc.py`, JME POG JEC | JME POG; AN-23-102 §7.2 |
| `CMS_res_j_2022` (JER) | `jerc.py`, JME POG JER | JME POG |
| `CMS_scale_e_2022`, `CMS_res_e_2022` | `electron_ss.py`, EGM SS | EGM POG |
| `CMS_scale_m_2022`, `CMS_res_m_2022` | `muon_ss.py`, MUO scale/res | MUO POG |

### 1c. Rate (lnN) + rateParam + MC-stat
| Nuisance | Value | Processes | Reference |
|---|---|---|---|
| `lumi_13p6TeV` | 1.014 | all exc. tt | CMS LUM POG (Run3 2022) |
| `xsec_st` | 0.9873/1.0167 | st | AN-23-102 Table 16 |
| `xsec_diboson` | 1.037 | diboson | AN-23-102 Table 16 |
| `xsec_vjets` | 1.027 | vjets | AN-23-102 Table 16 |
| `xsec_higgsbkg` | 1.05 | higgsbkg | AN-23-102 §7.1 |
| `flavor_composition_ggH` | 1.40 ⚠ | higgsbkg | AN-23-102 §7.1 — **PLACEHOLDER** (0.5·0.8; apply full 1.50 to ggH once split out) |
| `BR_HtoWW` | 1.01 | hplusc,higgsbkg | LHCHWG YR4 |
| `xsec_hplusc_PDF` | 1.06 | hplusc | AN-23-102 §7.1 |
| `xsec_hplusc_4FS_5FS` | 1.30 | hplusc | AN-23-102 §7.1 |
| `alphaS_PDF` | 1.03 | all exc. tt | PDF4LHC / AN-23-102 |
| `tt` **rateParam** | free | tt | data-driven, CR_tt→SR shared (AN-23-102) |
| `autoMCStats 10` | per-bin BB | all | combine Barlow-Beeston |

## 2. MISSING / TODO — what's remaining, with expected impact

**Impact column = AN-23-102 Table 17, `1POI r_H+c` column** — i.e. how much that source moved
the *published* analysis' total uncertainty. It is the best available prior for what adding it
will cost us. ⚠️ Our own MC-stat is ~8× the AN's, so every one of these lands on top of a much
larger stat term and will matter **less** for us in relative terms, not more.

| Item | Status | AN 1POI impact | Effort | What to do |
|---|---|---|---|---|
| **Trigger SFs (muon + electron)** | 🟢 **CODED, not enabled** | **0.0%** | **config only** | `Electron-HLT-SF` is **already fully implemented** in `electron.py` (`HLT_SF_Ele30_MVAiso80ID` for our `wp80iso`), json path resolved, and a `muon_hlt` efficiency json sits alongside. Flip `trigger: false` → enable, add the nuisance row. **See §2e.** <br>**Genuinely negligible in the AN (0.0%)** — do it for correctness, not for the limit. |
| **MET unclustered energy** | 🔴 MISSING | **0.4%** | **medium** | Needs a new *object-shift* parquet tree (`CMS_scale_met_unclustered_*`), i.e. a reprocessing pass. AN §7.2 varies each particle type by its resolution. |
| **top-pT reweighting** | 🔴 MISSING | *(in tt-norm 0.7%)* | low | `weight_toppt*` on tt. **Partly moot for us:** tt is data-driven via the `rate_tt` rateParam, which already absorbs the normalisation part. |
| **PDF *shape* nuisance** | 🔴 MISSING | *(≤1–3%, in cH/bH 8.5%)* | **low** | `LHEPdfWeight` IS already computed (`lhepdf.py` wired); only the `xsec_hplusc_PDF` lnN is used. Swap/add the Hessian-envelope **shape** rows — cheapest real upgrade on this list. |
| **PU jet ID** | 🔴 MISSING | *(not broken out)* | low | JME POG SF; AN §7.2 "Jet ID / jet PU ID". |
| **BR(H→ττ)** | 🔴 MISSING | *(in Bkg-Higgs 7.6%)* | trivial | 1% lnN on the H→ττ component of `higgsbkg`. |
| **`flavor_composition_ggH` placeholder** | 🟠 TODO | *(in Bkg-Higgs 7.6%)* | medium | Split ggH out of `higgsbkg`, then apply the full 1.50 to ggH only (currently 1.40 effective on merged higgsbkg). |
| **Decorrelate all systematics** | 🟠 TODO (deferred) | JES/JER **1.1%**, charm-tag **1.1%** | high | Whole-card pass: JES Total→RegroupedV2 (11 sources, AN §7.2); `CMS_ctag2d_2022` Total→Stat + per-source, mapping the SF's own JES/PU/lepton/theory components onto our **existing** nuisance names so they correlate rather than double-count (HiggsDNA `bTagShapeSF` model). Decision 2026-07-24: single `Total` for now. <br>⚠️ Decorrelating usually **loosens** artificial constraints → can *improve* the limit. |
| **L1 prefiring** | 🟡 N/A | — | — | 2016/2017 only per AN §7.2. Run-3 ECAL prefiring ≈ 0. |
| Year combination (2022pre + 2023) | 🟡 scope | — | high | Card is 2022postEE only; set the correlation scheme across campaigns when combining. |

### Priority reading

1. **PDF shape** — the weights already exist, so this is nearly free and touches the signal.
2. **Trigger SFs** — the last missing POG correction, and it turns out to be **already coded**
   (§2e), so it is a config flip rather than development. AN Table 17 puts its impact at
   **0.0%**: add it for correctness, expect no limit change.
3. **Decorrelation** — the only item that might *improve* the limit rather than cost.
4. Everything else is sub-percent in the AN and dominated by our MC-stat term.

## 2b. Coverage vs AN-23-102 Table 16 (verified 2026-07-31)

Line-by-line against the AN's own inventory. <span>**We now have every AN source except four**,
and all four are ≤0.4% in the AN's 1POI impact table.</span>

| AN Table 16 source | ours | note |
|---|---|---|
| signal(H+c) PDF | ✅ `xsec_hplusc_PDF` | as lnN; shape version is the TODO above |
| signal flavour scheme (4FS/5FS) | ✅ `xsec_hplusc_4FS_5FS` | 30%, matches AN |
| ggH+HF jets | ⚠️ `flavor_composition_ggH` | placeholder 1.40 vs AN 1.50-on-ggH |
| Higgs production | ✅ `xsec_higgsbkg` | |
| BR H→WW | ✅ `BR_HtoWW` | |
| BR H→ττ | ❌ | 1% lnN, trivial to add |
| Z+jets / diboson / single-top xsec | ✅ `xsec_vjets`, `xsec_diboson`, `xsec_st` | exact AN values |
| αS + PDF | ✅ `alphaS_PDF` | |
| top pT reweight | ❌ | largely absorbed by the `rate_tt` rateParam |
| UE & parton showering | ✅ `ps_isr`, `ps_fsr` | |
| Renormalisation & factorisation | ✅ `scalevar_muR`, `_muF`, `_muR_muF` | |
| Luminosity | ✅ `lumi_13p6TeV` | |
| MC statistical | ✅ `autoMCStats 10` | **our dominant term** |
| L1 prefire | n/a | 2016/2017 only |
| Pileup | ✅ `pileup` | |
| **HLT efficiencies** | ❌ | the gap you flagged — AN impact **0.0%** |
| Electron ID/Reco | ✅ `electron_id`, `electron_reco_*` (3 pt bins) | |
| Muon ID/ISO/Reco | ✅ `muon_id`, `muon_iso` | |
| Jet energy scale/resolution | ✅ `CMS_scale_j_2022`, `CMS_res_j_2022` | single Total vs AN's RegroupedV2 ×11 |
| MET unclustered energy | ❌ | AN impact 0.4%; needs a new shift tree |
| PU jet ID | ❌ | |
| charm tagging | ✅ **`CMS_ctag2d_2022`** | added 2026-07-22 |

**AN-23-102 Table 17, `1POI r_H+c` — the correct reference column:**

| source | AN 1POI |
|---|---|
| Statistical | 73.8% |
| cH/bH (signal theory) | 8.5% |
| Bkg-Higgs | 7.6% |
| Other background | 1.4% |
| **MC statistical (bin-by-bin)** | **5.4%** |
| Pileup | 0.4% |
| Lepton efficiencies | 0.4% |
| **Trigger efficiencies** | **0.0%** |
| Jet energy scale & resolution | 1.1% |
| Charm tagging | 1.1% |
| Missing energy scale | 0.4% |
| tt normalization | 0.7% |

> ⚠️ **Correction to earlier notes.** The AN has **no Table 18**. Several older notes and the
> June `breakdown_vs_AN.png` plot quote AN values (charm-tag 5.9%, MC-stat 6.2%, JES 6.0%,
> lepton 4.6%) that **do not appear in Table 17's 1POI column**. Only MC-stat is even close
> (6.2 vs 5.4). Treat those older grey bars as unverified.

## 2d. OUR breakdown — freeze scan, 2026-07-31 (AN-comparable)

Measured on the **current** `v11_hplusc_v4` card: negrw + c-tag SF + `sumw_records`
normalisation + **no** LOWESS smoothing. Full limit **1164**, σ(68% half-width) = 509.5.

Computed the **AN's way** — the change in the 1σ uncertainty when a group is frozen,
$|\Delta r|/r = \sqrt{\sigma_\text{full}^2-\sigma_\text{frozen}^2}\,/\,r$ — so these are directly
comparable to Table 17. Script: `decks-2026-07-31/scripts/freeze_scan.sh`.

| source | frozen limit | **ours** | AN 1POI | ratio |
|---|---|---|---|---|
| Statistical | 676 | **39.1%** | 73.8% | 0.5× |
| **MC statistical** | 930 | **28.7%** | **5.4%** | **5.3×** |
| **Signal theory (cH/bH)** | 1032 | **31.1%** | 8.5% | **3.7×** |
| tt normalization | 1123 | **11.5%** | 0.7% | 16× |
| Charm tagging | 1127 | **10.2%** | 1.1% | 9× |
| Bkg-Higgs | 1143 | 8.3% | 7.6% | **1.1× ✅** |
| JES/JER | 1153 | 7.3% | 1.1% | 7× |
| Other background | 1161 | 5.2% | 1.4% | 3.7× |
| Lepton | 1163 | 1.8% | 0.4% | 4.5× |
| Pileup | 1164 | 0.0% | 0.4% | — |
| Lumi | 1164 | 0.0% | — | — |
| `CMS_negrw_vjets` (method) | 1164 | **0.0%** | n/a | negligible ✅ |
| *(theory shapes `scalevar_*`+`ps_*`)* | 1097 | *15.2%* | — | overlaps the groups above |

### Reading it

1. <span>**MC-stat 28.7% vs 5.4% — still ~5× the AN.**</span> This is the real gap. Note the old
   "41%" was `(full−freeze)/full` on $r_{95}$, a *different metric*; on the AN's definition the
   current value is 28.7%. **Quote 28.7% and say which definition.**
2. <span>**Signal theory 31.1% is now our #2 term**</span> (AN: 8.5%). This is
   `xsec_hplusc_4FS_5FS = 1.30` — a 30% flat lnN on an already statistics-starved signal.
   → re-deriving it (§2c) is a **top** lever, not a tidy-up.
3. **tt normalization 11.5% vs 0.7%.** Ours is a free `rateParam` in a fit whose SR is ~72% tt
   and MC-starved, so it absorbs far more than the AN's treatment. Worth revisiting.
4. **Bkg-Higgs 8.3% vs 7.6% is the one group that genuinely matches.**
5. **Pileup / lumi / negrw are exactly 0.0%** — fully profiled away. Confirms independently that
   the negrw *method* uncertainty is negligible.

### ⚠️ Caveats on these numbers

- **Not orthogonal — do not add them.** Components sum in quadrature to 709 vs σ_full 510
  (ratio 1.39): freezing one group lets the fit re-profile the others. The AN's own rows behave
  the same way (their 1POI column sums to 100.8%).
- σ is taken as the **68% band half-width** from `AsymptoticLimits`, a proxy for the AN's
  likelihood-based 1σ. Cross-analysis comparison is indicative at the ±few-% level, not exact.

### Priority, by measured impact

| # | lever | ours | note |
|---|---|---|---|
| 1 | **Signal theory (4FS/3FS)** | 31.1% | ~20k gen-level events, §2c |
| 2 | **MC statistics** | 28.7% | more vjets/tt at high $D$; negrw already bought ~2× here |
| 3 | tt normalization | 11.5% | is the free rateParam right? |
| 4 | Charm-tag decorrelation | 10.2% | `Total`→per-source should **loosen** it |
| 5 | JES RegroupedV2 | 7.3% | |
| … | **Trigger SFs** | **0.0% expected** | add for correctness, not for the limit |

## 2c. `xsec_hplusc_4FS_5FS` (30%) — checked 2026-07-31

**Is it double-counting against our reference cross-section? NO.**

Our dataset config uses `xsec = 0.0022141 pb` (2.214 fb) for `HplusCharm_HtoWW`, from
`HPlusCharm_HToWW_M-125_TuneCP5_13p6TeV_`**`amcatnloFXFX`**`-pythia8`.

| | ours (13.6 TeV) | AN (13 TeV) | ratio |
|---|---|---|---|
| H+c | 2.214 fb | 2.040 fb (4FS **FXFX**) | 1.085 |
| H+b | 0.01697 pb | 0.0158 pb (5FS **FXFX**) | 1.074 |

Both sit 7–9% above the AN's — the size expected from 13 → 13.6 TeV alone. So `r` is
normalised to the **4FS-FXFX-merged** prediction, which is exactly the nominal that the AN's
30% flavour-scheme uncertainty sits *on top of*. The 1.30 lnN is correctly placed.

### ⚠️ But the 30% itself does not reproduce from the AN's own Table 1

AN §7.1: *"Obtain the flavor scheme uncertainties (4FS vs. 3FS) using the samples **without
FXFX merging**. The differences between the two predictions are used as uncertainty and added
to the nominal FXFX merging sample. The discrepancy is in order of 30%."*

AN Table 1 signal samples:

| sample | σ×Br |
|---|---|
| H+c 4FS amcatnloFXFX ← **nominal** | 2.04 fb |
| H+c 4FS amcatnlo (no FXFX) | 1.83 fb |
| H+c 3FS amcatnlo (no FXFX) | 1.13 fb |

1.83 / 1.13 = **1.62**, i.e. a **62% spread**, not 30%. Possibly a half-spread, a symmetrised
value, or compared after selection — the AN text doesn't say. We **inherit** their convention
along with the number.

### To re-derive at 13.6 TeV — what to generate

- **Gen-level / LHE is sufficient.** The AN treats this as pure *normalization* (Table 16:
  "normalization, 100% correlated, 30%"), so only the inclusive cross-section ratio is needed.
- <span>**You need BOTH non-FXFX variants — 3FS *and* 4FS — not just 3FS.**</span> The AN compares
  the two *unmerged* predictions against each other, not 3FS against the FXFX nominal.
- **How many events:** the target is $R=\sigma(4FS)/\sigma(3FS)$ to ~2–3%, which is far finer
  than a number quoted as "order of 30%". The binding constraint is negative weights — measured
  on our own H+c sample: **neg fraction 0.262, $N_\text{eff}/N \approx 0.185$.**

| target $dR/R$ | $N_\text{eff}$ each | **generated events each** |
|---|---|---|
| 5% | 800 | ~4,300 |
| **3%** | 2,200 | **~12,000** |
| **2%** | 5,000 | **~27,000** |
| 1% | 20,000 | ~108,000 |

**Recommendation: ~20k events each (~40k total)** → $dR/R \approx 2.3$%, i.e. the 30% known to
±0.7% absolute. For scale, the nominal H+c production is **277,345** events, so this is ~7% of
it per sample. Generate 3FS first and **re-measure its negative fraction** — an unmerged 3FS
NLO sample can be more pathological than the 4FS nominal, and if it reaches ~35% the required
count roughly doubles.

**Not needed unless flatness is in doubt:** a *shape* check would require these through reco at
SR statistics (selection efficiency ≈ 1925/277345 ≈ 0.7% → millions of events).

### Per-era? No. Through selection? No.

**One generation total, not one per era.** The FS uncertainty is a generator-level
matrix-element question (does 3FS or 4FS describe initial-state charm better) — a property of
the PDF/ME setup, not of detector conditions. Pileup, alignment and calibration differences
between preEE / postEE / 2023 do not change the parton-level 4FS/3FS ratio. The AN quotes a
single **30%, "100% correlated"** across all years (Table 16). What *does* matter is √s, so
generate at **13.6 TeV** once and apply the result to every Run-3 era, correlated.

**No detector simulation / no selection.** As the AN defines it the quantity is the *inclusive*
cross-section ratio — LHE/gen-level counting only. That is what keeps the job at ~20k events.

| version | what it answers | events each | verdict |
|---|---|---|---|
| **gen-level, inclusive** | the AN's 30% normalization | **~20k** | ✅ do this |
| through reco, SR-level | is the FS difference *flat* in the discriminant? | ~1.5M | ❌ not unless flatness is challenged |

<span>The reco number is ~20k / 0.007 (SR efficiency) / 0.185 ($N_\text{eff}$ dilution) ≈ 1.5M —
about 50× the gen-level job, for a check the AN never performed. If flatness ever *did* fail,
the fix is a shape nuisance, which is a larger design question than the sample request.</span>

⚠️ **Size in two steps.** The 20k assumes the 3FS negative-weight fraction resembles the 4FS
nominal's (0.262). An unmerged 3FS NLO sample can be worse. Generate a small batch, measure
$N_\text{eff}/N$, then size the rest — don't commit the full request blind.

## 2e. Object IDs / working points and their SF sources (checked 2026-07-31)

### Electrons — `wp80iso`

**Selection** (`hww_combine_fixed.yaml:52-54`): `pt > 10`, `|η| < 2.5`,
`working_points.electron_id(events, 'wp80iso')`; pair cuts `l1.pt > 20`, `l2.pt > 10`,
`(l1+l2).pt > 30`.

**Definition** (`analysis/working_points/working_points.py:12`):

```python
"wp80iso": events.Electron.mvaFall17V2Iso_WP80      # Run 2 NanoAOD
           if hasattr(...) else events.Electron.mvaIso_WP80   # Run 3  <- ours
```

i.e. the **EGamma MVA ID *with* isolation, 80% signal-efficiency WP**, read straight off the
NanoAOD boolean branch `Electron_mvaIso_WP80`. The same helper also exposes `wp90iso`, the
`cutBased` ladder (`fail/veto/loose/medium/tight` = 0–4) and an `mvaHZZIso` BDT ID — none used.

**Official source**, cited in `analysis/corrections/electron.py:29`:
<https://twiki.cern.ch/twiki/bin/view/CMS/EgammSFandSSRun3#Scale_factors_and_correction_AN1>

### Muons — `tight` ID + `tight` iso

`working_points.py:90` → `events.Muon.tightId` (options: `looseId`/`mediumId`/`tightId`);
isolation via `muon_iso`. Configured at `hww_combine_fixed.yaml:153-154`.

### All correction files actually loaded (2022postEE)

| key | correction(s) | file |
|---|---|---|
| `electron_id` | `Electron-ID-SF` | `/cvmfs/cms-griddata.cern.ch/cat/metadata/EGM/Run3-22EFGSep23-Summer22EE-NanoAODv12/2025-10-22/electron.json.gz` |
| `electron_reco` | `Electron-ID-SF` | *(same file)* |
| `electron_ss` | scale & smearing | `.../EGM/.../latest/electronSS_EtDependent.json.gz` |
| **`electron_hlt`** | `Electron-HLT-SF`, `-DataEff`, `-McEff` | `/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/EGM/2022_Summer22EE/electronHlt.json.gz` |
| `muon` | MUO Z-based SFs | `.../MUO/.../2025-08-14/muon_Z.json.gz` |
| `muon_ss` | scale & smearing | `.../MUO/.../muon_scalesmearing.json.gz` |
| **`muon_hlt`** | HLT efficiency | `~/higgscharm/analysis/data/muon_hlt/2022postEE_Muon_HLT_Eff.json` (local, not CVMFS) |
| `pileup` | `puWeights` | `.../LUM/.../2024-01-31/puWeights.json.gz` |
| `ctagging` | 1D PNet c-tag *(superseded)* | `.../BTV/.../2025-08-20/ctagging.json.gz` |
| **`ctagging_2d`** | `ParticleNetAK4_pseudocontinuous` | `/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022postEE.json.gz` |
| `jetvetomaps` | JME veto maps | `.../JME/.../2025-10-07/jetvetomaps.json.gz` |

⚠️ Note the EGM/MUO/BTV/LUM files come from the **CAT metadata** area
(`cms-griddata.cern.ch/cat/metadata/...`), *not* the usual `jsonpog-integration` path — only
`electron_hlt` uses the latter.

### 🟢 Trigger SFs are already implemented, just not enabled

`analysis/corrections/electron.py` contains a complete HLT implementation keyed by working
point, with the json path already resolved:

```python
"wp80iso": "HLT_SF_Ele30_MVAiso80ID"
"wp90iso": "HLT_SF_Ele30_MVAiso90ID"
```

and there is a `muon_hlt` efficiency json alongside it. So the "missing trigger SF" from §2 is
a **configuration change** (`trigger: false` → enable + add the nuisance), **not** new
development — cheaper than the "low effort" originally estimated. AN impact is still **0.0%**,
so this is a correctness item, not a limit-improving one.

## 3. What's DONE / not-applicable
- **Signal theory shapes** (`ps_*`, `scalevar_*` on hplusc): ✅ present — `hplusc` is not in `no_theory`.
- **1D fixed-WP c-tag SF** (`CTagCorrector`, BTV `particleNet_wc/tnp`): N/A — superseded by the 2D pseudo-continuous SF for this analysis.
- **JER**: single `CMS_res_j` Total — no split needed at current precision.

## 4. Current limit (updated 2026-07-31)

Baseline MVA + negrw + 2D c-tag SF, on `sumw_records` normalisation, **no LOWESS smoothing**:

| variant | full | stat-only | freeze-autoMCStats |
|---|---|---|---|
| no SF | **1150** | 668 | 905 |
| **+ `CMS_ctag2d_2022`** | **1164** | 676 | 930 |

<span>Two configuration changes landed 2026-07-31 and **supersede all earlier numbers**
(1343 / 1371 / 1422 and the intermediate 1172 / 1192):</span>

1. **`read_scale` → self-normalising `sumw_records`** — the sidecar `sumw_<year>.json` was stale
   for the signal (records = shard-metadata = 7.823e+04 vs sidecar 9.266e+04). Signal template
   +18.4%, vjets +6.0%, everything else unchanged. See
   [[2026-07-31-sumw-normalization-trap]].
2. **`smooth_shapes: false` everywhere** — LOWESS was double-treating the negrw-reweighted vjets
   templates. Limit *improves* ~2%; stat-only identical, as it must be.

⚠️ **vs the published analysis:** AN-23-102 quotes an expected UL of **431 at 138 fb⁻¹**
(1POI). Scaled to our 26.7 fb⁻¹ that is $431\times\sqrt{138/26.7} =$ **980**, so we are
**~19% worse**, not at parity. Our stat-only 676 does beat the AN's scaled stat-only (~723).

The 2D SF is applied **natively in the processor** (`CTag2DCorrector`); the post-hoc
`apply_ctag2d_sf.py` is retired.

### All three arms, same configuration (re-measured 2026-07-31)

| variant | full | stat-only | freeze-autoMCStats |
|---|---|---|---|
| baseline, no SF | **1150** | 668 | 905 |
| baseline + SF | **1164** | 676 | 930 |
| **2D-cat + SF** | **1676** | **637** | 1393 |

The 2D-cat tree was repaired first — the merge had been **interrupted** (34 of 57 group
parquets; all raw shards present), completed with the repo's `merge_parquet_files`, then
one-hots → inference → build.

**Reading it:** stat-only *improves* **−5.8%** (637 vs 676), so the 2D-cat MVA is genuinely the
sharper discriminant. But the full limit is **+44% worse** — far more than the +6% the old
sidecar+smoothing series suggested. The SR composition explains it:

| SR | baseline | 2D-cat | ratio |
|---|---|---|---|
| signal | 0.203 | 0.261 | 1.29× |
| **tt** | 7,274 | 16,939 | **2.33×** |
| total | 9,199 | 20,664 | 2.25× |

$S/\sqrt{B}$ *falls* to 0.86×, and the stat→full inflation is **2.63×** vs 1.72× for baseline.
<span>**On the current configuration, baseline scores + SF is the better choice.**</span>
