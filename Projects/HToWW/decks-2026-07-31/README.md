---
tags: [reference]
status: active
date: 2026-07-31
source: lxplus
---

# Two decks — negative-weight reweighting & official 2D c-tag SFs

Both are Marp markdown, rendered to PDF alongside. Images in `img/`.

## Rendering

```bash
cd Projects/HToWW/decks-2026-07-31
CHROME_PATH=/usr/bin/google-chrome \
  npx -y @marp-team/marp-cli@latest <deck>.md -o <deck>.pdf --allow-local-files
```

---

## 1. `negrw-deck.md` — Negative-weight reweighting (41 slides)

The complete story of the fix: diagnosis → method → training → validation → limit.

**Structure**

| part | content |
|---|---|
| 1. The problem | the signed estimator as a cancellation; the actual broken template; the fit consequence |
| 2. The method | $g = 2P_+-1$; why the mean is preserved (the algebraic identity, Eqs. 2–6) |
| 3. Training | train-loose/infer-tight region, 20 gen features, 20× HistGBDT ensemble, convergence, ROC, importance, closure, $N_\text{eff}$ |
| 4. Validation | calibration, $g$ vs realised sign, SR closure + the renorm decision, the method nuisance |
| 5. Result | limit cascade, the numbers, template-level evidence, reproducibility, the 3 bugs, what it did *not* fix |
| backup | config reference, failure modes, per-bin SR table |

**Headline:** $r_{95}$ 1742 → **1343** (v11) and 1935 → **1491** (v32), both −23%.
autoMCStats inflation collapses 710 → 243 (v11) and 867 → 408 (v32).

### New plots made for this deck

| plot | what it shows |
|---|---|
| `P1_SR_vjets_template.png` | **the smoking gun** — SR V+jets template pre/post negrw with MC-stat errors. Bin 6 goes from `0 ± 41` (rel. err 4×10⁹%) to `83.4 ± 20.4`. Usable-bin mean rel. err **59.6% → 30.3%** |
| `P1_CRvjets_vjets_template.png` | same for CR_vjets: **21.4% → 13.8%**, every bin improves |
| `P3_limit_cascade.png` | stat-only → freeze-autoMCStats → full, baseline vs negrw, both builders. The curves **overlap** until the last stage — isolating autoMCStats as the entire effect |

Generators: `negrw_extra_plots.py` (cascade), `p1v3.py` (templates), both run on lxplus against
the real combine ROOT files (`v11_hplusc_v4.root` and its `.bak_pre_negrw`).
Existing 13 training/validation plots reused from `../negrw-training/img/`.

---

## 2. `ctag-sf-deck.md` — Official 2D c-tag scale factors (27 slides)

The 2D scheme, the official SFs, and a **controlled with/without-SF closure**.

**Structure**

| part | content |
|---|---|
| 1. The scheme | plane + frozen edges; B recoverable from CvsL/CvsB (verified 3 ways); the plane plot; only 7 of 11 categories populated |
| 2. The SFs | source/signature, central matrix, uncertainty band, how it enters the fit |
| 3. Closure | how the A/B was built, the **sumw trap**, the result, the matched 2D-cat combination, MVA cost, recommendations |
| backup | numeric SF matrix + the L0 convention, file map, batch gotchas |

**Headline:** the SF weakens the limit by **~2%** (1343 → 1371) — the correct sign and size for
adding a real, previously-neglected uncertainty. With the matched 2D-cat discriminant: 1422
(stat-only *improves* to 749, but the wider SR admits 2.3× more tt).

### New plots made for this deck

| plot | what it shows |
|---|---|
| `C1_sf_matrix.png` | central SF heatmap, 3 flavours × 11 categories, $p_T$=60 GeV. Corrections are O(10–30%) |
| `C2_sf_band.png` | central SF with the `up/down_Total` band — **this band is the `CMS_ctag2d_2022` nuisance**. Populated categories only, because B1–B4 carry ±[0.3,3.0] placeholder bands that compress everything real |

Generator: `ctag_sf_plots.py`, evaluated directly from
`flavTaggingSF_2022postEE.json.gz` via correctionlib.
Plane plot reused from `/eos/user/c/cgupta/HToWW/plots/ctag2d_plane_bins.png`.

---

## The closure A/B — how it was built

Non-destructive. Nothing in `hww_combine_fixed` was modified.

| | no-SF variant | with-SF variant |
|---|---|---|
| workflow yaml | `hww_combine_nosf.yaml` (= `hww_combine_fixed.yaml` minus the `CMS_ctag2d_2022` line) | `hww_combine_sfchk.yaml` (verbatim copy) |
| tree | `outputs/hww_combine_nosf/2022postEE/` — **585 symlinks** to `.bak_pre_ctag2dsf` | `outputs/hww_combine_sfchk/2022postEE/` → symlink to the live tree |
| nuisance count | 29 | 30 |
| output | `v11_hplusc_nosf.{root,txt}` | `v11_hplusc_sfchk.{root,txt}` |

Both go through the *same* builder on the *same* day, so the only differences are the
central-SF weight rescale and the one nuisance row.

### ⚠️ The trap this uncovered

The first pair of rebuilds disagreed with the reference datacard by **2.4× in V+jets**.
Cause: `make_combine_inputs.py` had been reverted (2026-07-31 03:04, before this session) from
the **sidecar** `sumw` source to the **parquet-metadata** one, which undercounts low-efficiency
samples — `WtoLNu_2Jets` by **5.8×**, `TbarQto2Q` by 72×, and `WWZ/WZZ/ZZZ` have no metadata at all.
Since `sumw` is the denominator of `lumi*xsec/sumw`, this **inflates** the yield.

Restored the sidecar version (old one kept as `.bak_parquetmd_20260731`) and rebuilt.
Full write-up: [[2026-07-31-sumw-normalization-trap]].

**Sanity check for any future rebuild:** SR V+jets ≈ **735**, all-channel V+jets ≈ **5.8k**
(2022postEE). If V+jets is ~14k, the wrong `read_scale` is active.

---

## Related

- [[RESUME-condor-retrain]] — negrw training/run log
- [[2026-07-17-closure-renormalization-decision]] — the SR renorm decision
- [[2026-07-18-v32-optimization-negative-results]] — the four things that did *not* work
- [[2026-07-19-ctag2d-full-documentation]] — full 2D c-tag write-up
- [[2026-07-31-sumw-normalization-trap]] — the normalization bug found here
- `References/HToWW/2510.16217-negweight-reweighting.pdf`
- `References/HToWW/2D-SFbc-calibration-AN-25-222.pdf`
