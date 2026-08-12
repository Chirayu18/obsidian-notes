---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# CR structure, the per-channel result, and the xsec_vjets degeneracy

## 1. Per-channel binning variant: MEASURED, and it is NEGATIVE

| configuration | limit | vs baseline |
|---|---|---|
| all 6 channels, 10 bins each | **1160** | — |
| CR_st/CR_higgsbkg/CR_diboson -> 1 bin | **1193** | **+33 (worse)** |
| all 5 CRs -> 1 bin | ~1210 | +50 (worse) |

The `per_channel` variant has been **disabled** in `hww_combine_2dcat.yaml` with
the measurement recorded inline. The CR shapes carry real constraint; removing
information costs the limit monotonically.

**Process note:** this result was produced by a build at 14:05 that overwrote the
card on disk. A freeze test launched afterwards reported "nominal 1193" which
initially looked like a discrepancy — it was simply the variant card. Always
check `uproot`-level bin counts per channel before trusting a card's identity:

```python
import uproot
f = uproot.open('v11_hplusc_2dcat.root')
for ch in ['SR_hplusc','CR_higgsbkg','CR_tt','CR_st','CR_diboson','CR_vjets']:
    print(ch, len(f[ch+'_vjets'].values()))
# 1160 card = 10 everywhere; per_channel variant = 1 for st/higgsbkg/diboson
```

## 2. Channel composition (fraction of each channel's own total)

| channel | hplusc | higgsbkg | tt | st | diboson | vjets | total |
|---|---|---|---|---|---|---|---|
| SR_hplusc | 0.0% | 0.6% | 82.0% | 7.2% | 2.9% | 7.3% | 20,664 |
| CR_higgsbkg | 0.0% | 0.5% | 86.4% | 6.5% | 1.6% | 5.0% | 9,220 |
| CR_tt | 0.0% | 0.1% | **94.1%** | 5.1% | 0.3% | 0.5% | 44,199 |
| CR_st | 0.0% | 0.0% | 87.6% | 10.0% | 1.8% | 0.6% | 20,135 |
| CR_diboson | 0.0% | 0.0% | 72.4% | 11.1% | 10.5% | 6.0% | 6,585 |
| CR_vjets | 0.0% | 0.7% | 49.6% | 4.2% | 2.3% | **43.2%** | 9,214 |

Where V+jets actually lives:

| channel | vjets yield | share of all vjets |
|---|---|---|
| CR_vjets | 3,979.4 | **59.6%** |
| SR_hplusc | 1,507.7 | 22.6% |
| CR_higgsbkg | 464.4 | 7.0% |
| CR_diboson | 395.9 | 5.9% |
| CR_tt | 215.0 | 3.2% |
| CR_st | 111.9 | 1.7% |

## 3. "Four of five CRs are tt-dominated" is NOT an indictment

The SR is itself **82% tt**. tt is the dominant background everywhere in an eμ
final state, so a CR being tt-rich is expected, not a design failure.

- **CR_tt is excellent**: 94.1% pure over 44,199 events. It pins `rate_tt`, the
  free-floating rateParam covering 82% of the SR. This is the single most
  valuable constraint in the fit.
- CR_st / CR_higgsbkg / CR_diboson are largely redundant *with each other* —
  three slices of the same top phase space. Collapsing them was a reasonable
  hypothesis; it measured +33 and was reverted.

## 4. The xsec_vjets "+13 anomaly" — RETRACTED, it does not reproduce

**An earlier impacts scan reported freezing `xsec_vjets` giving 1173 (+13) —
i.e. the limit getting WORSE when a nuisance was removed. Re-measured on a
freshly rebuilt 1160 card, it does not reproduce.**

| test | earlier scan | re-measured 2026-08-12 |
|---|---|---|
| nominal | 1160 | **1160** |
| freeze `xsec_vjets` | 1173 (**+13**) | **1159 (-1)** |
| freeze `rate_tt` | — | 1155 (-5) |
| freeze BOTH | — | 1154 (-6) |

Same nominal, same configuration. `xsec_vjets` behaves as an ordinary small
nuisance: freezing it *improves* the limit by 1 unit, the normal direction.

Likely causes of the original number, in order:
1. A bad fit at that scan point — `AsymptoticLimits` occasionally finds a poor
   minimum, and that scan was single-shot with no repeats.
2. A subtly different card state — the disk card was rewritten mid-window
   (14:05). The scan's nominal printed 1160, but not every point in the loop can
   now be proven to have used the same file.

**Also note `rate_tt` (-5) and `xsec_vjets` (-1) are close to additive (-6
together) — i.e. they barely interact.** That is the opposite of a degeneracy.

### What was wrong with the original explanation

A mechanism was written up here claiming the +13 came from `xsec_vjets` being
degenerate with the free-floating `rate_tt` through the 49.6%-tt CR_vjets, with
the fit using the lnN as slack to protect `rate_tt`. The composition numbers in
that story are correct, but **the effect they were invoked to explain is not
real**. The story is retracted.

**Process lesson: re-measure an anomalous point before explaining it.** A ~1%
shift on a single unreplicated measurement is not a phenomenon; it is within the
range where a refit can move it. The mechanism was plausible and internally
consistent, which is exactly why it should have been tested before being
written down.

## 5. What NOT to do

- **Do not drop the CRs.** Collapsing costs 33-50 units; dropping is the
  limiting case of that trend. CR_vjets alone holds 59.6% of all V+jets in the
  fit — without it there is no V+jets constraint from anywhere.
- **Do not redefine the CRs as cut-based.** Cut-based CRs are *less* pure than
  the argmax-defined ones. (AN-23-102's cut-based top CR does not even separate
  tt from single-top.) The argmax construction is already the purer one; a
  redefinition would move backwards.

## 6. What actually helps

With the +13 retracted, there is **no degeneracy pathology to fix**. The CR
structure is behaving normally: freezing `rate_tt` costs 5 units, freezing
`xsec_vjets` costs ~1, and they are near-additive.

CR_vjets purity (43.2%) is still near its ceiling given the current V+jets
samples, and improving it remains worthwhile on its own merits — better
modelling and more effective statistics — via tasks #27 (W+jets 0J/1J/2J) and
#28 (DY -> ττ-filtered). But it should be motivated as a **MC-statistics and
modelling** improvement, not as a fix for a fit pathology that does not exist.

Bigger lever still, unrelated to CRs: **`scalevar_muF` at -69** (task #35), about
twice the size of anything CR-structural.
