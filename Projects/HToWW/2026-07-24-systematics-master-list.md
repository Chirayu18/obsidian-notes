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
| **Trigger SFs (muon + electron)** | 🔴 MISSING | **0.0%** | **low** | `trigger: false` → enable; SFs from the top-analysis cross-trigger measurement (AN §7.2, ref [23]). Adds `weight_trig*Up/Down` → one shape row. <br>**Genuinely negligible in the AN** — worth adding for completeness/correctness, not for the limit. |
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
2. **Trigger SFs** — you named this as the gap, and it *is* the last missing POG correction,
   but AN Table 17 puts its impact at **0.0%**. Add it for correctness; expect no limit change.
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

## 3. What's DONE / not-applicable
- **Signal theory shapes** (`ps_*`, `scalevar_*` on hplusc): ✅ present — `hplusc` is not in `no_theory`.
- **1D fixed-WP c-tag SF** (`CTagCorrector`, BTV `particleNet_wc/tnp`): N/A — superseded by the 2D pseudo-continuous SF for this analysis.
- **JER**: single `CMS_res_j` Total — no split needed at current precision.

## 4. Current limit (all three latest changes)
negrw (Jul-15 model) + 2D-cat MVA + 2D SF (Total): **r95 = 1422 full / 749 stat-only / 1168 freeze-autoMCStats**.
The 2D SF is now applied **natively in the processor** (CTag2DCorrector); the post-hoc
`apply_ctag2d_sf.py` is retired. Full native re-run in progress (2026-07-24).
