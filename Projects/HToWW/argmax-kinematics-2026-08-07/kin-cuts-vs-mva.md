---
marp: true
theme: default
paginate: true
size: 16:9
title: Kinematic cuts vs the MVA
style: |
  section {
    font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
    font-size: 21px;
    padding: 44px 56px;
    background: #FAFAF8;
    color: #16181C;
  }
  h1 {
    font-family: Fraunces, "Iowan Old Style", Georgia, serif;
    font-size: 38px; line-height: 1.12; color: #16181C;
    border-bottom: 2px solid #16181C; padding-bottom: 12px; margin-bottom: 18px;
  }
  h2 {
    font-family: Fraunces, "Iowan Old Style", Georgia, serif;
    font-size: 29px; line-height: 1.18; color: #16181C;
    margin: 0 0 6px 0;
  }
  h3 { font-size: 17px; color: #6E7178; font-weight: 600; margin: 0 0 16px 0; }
  table { border-collapse: collapse; width: 100%; font-size: 17px;
          font-variant-numeric: tabular-nums; margin: 10px 0; }
  th, td { padding: 7px 11px; text-align: right; border-bottom: 1px solid #E2E0DB; }
  th:first-child, td:first-child { text-align: left; }
  thead th { background: #EDEFF1; font-size: 13px; letter-spacing: .07em;
             text-transform: uppercase; color: #6E7178; border-bottom: 1px solid #CFCCC5; }
  strong { color: #B23A2E; }
  .win { background: #F5E7E4; }
  code { font-family: "JetBrains Mono", ui-monospace, monospace;
         font-size: .88em; background: #EDEFF1; padding: 1px 5px; border-radius: 2px; }
  .callout { border-left: 3px solid #B23A2E; background: #F5E7E4;
             padding: 11px 15px; font-size: 19px; margin-top: 12px; }
  .flag { border-left: 3px solid #7C8794; background: #EDEFF1;
          padding: 11px 15px; font-size: 19px; margin-top: 12px; }
  .kicker { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 13px;
            letter-spacing: .15em; text-transform: uppercase; color: #B23A2E; }
  .stats { display: flex; gap: 18px; margin: 14px 0; }
  .stat { flex: 1; border: 1px solid #E2E0DB; padding: 12px 14px; background: #fff;
          display: flex; flex-direction: column; gap: 3px; }
  .stat .lab { display: block; font-size: 12px; letter-spacing: .09em;
               text-transform: uppercase; color: #6E7178; line-height: 1.3; }
  .stat .val { display: block; font-family: "JetBrains Mono", ui-monospace, monospace;
               font-size: 30px; font-weight: 700; line-height: 1.15; }
  .stat .note { display: block; font-size: 14px; color: #6E7178; line-height: 1.3; }
  .hi .val { color: #B23A2E; }
  .ok .val { color: #2E6B4F; }
  footer { font-size: 13px; color: #6E7178; }
  section.lead { display: flex; flex-direction: column; justify-content: center; }
  section.lead h1 { border-bottom: none; font-size: 44px; }
  img { display: block; margin: 6px auto; max-height: 340px; }
---

<!-- _class: lead -->

<span class="kicker">H→WW · 2022postEE · v11 6-class MVA</span>

# Kinematic cuts buy pre-selection S/√B — they do not buy control-region purity

The MVA defines **purer** control regions *without* any kinematic cut, and already applies
those cuts internally when it picks the signal region.
The real lever on SR yield is the **charm-tag working point**.

---

## 01 · The tt̄ control region is purer when the MVA defines it

### Purity = fraction of events whose *true* process is tt̄. Pooled MC, 4,046,127 events, raw/unweighted.

| tt̄ CR definition | N | tt̄ purity | signal contam. | non-tt̄ bkg |
|---|---:|---:|---:|---:|
| **argmax = tt̄, no kinematic cuts** | **1,565,461** | **87.86%** | **0.0004%** | **12.14%** |
| mT<sub>l2</sub>>30 & mT<sub>ll</sub>≤60 *(classic top CR)* | 565,368 | 78.10% | 0.0142% | 21.89% |
| m<sub>ll</sub>>72 | 2,375,781 | 83.04% | 0.0009% | 16.96% |
| m<sub>ll</sub>>72 & mT<sub>l2</sub>>30 & mT<sub>ll</sub>>60 | 1,614,248 | 83.12% | 0.0004% | 16.88% |

<div class="callout">

**The MVA CR wins on both axes at once** — purest (87.9% vs 78.1%) *and* 2.8× larger
(1.57M vs 565k). The classic cut-based top CR is the **worst of the four**, and carries
35× the signal contamination of the MVA CR.

</div>

---

## 01b · What is actually in the MVA tt̄ CR

| true process | N | fraction |
|---|---:|---:|
| tt̄ | 1,375,464 | 87.86% |
| single top | 146,891 | 9.38% |
| Higgs bkg | 41,122 | 2.63% |
| diboson | 1,872 | 0.12% |
| V+jets | 105 | 0.01% |
| **H+c (signal)** | **7** | **0.00%** |

<div class="callout">

Single-top is the only real contaminant — and it is physically tt̄-like, which is exactly
what you want a tt̄ CR to constrain. Signal leakage is **7 events out of 1.57M**.

</div>

---

## 02 · The MVA has already internalised the SR kinematic cuts

### Fraction of events called signal across the (m<sub>ll</sub>, mT<sub>ll</sub>) plane — no kinematic cut applied

![w:760](internalised_2d_plane.png)

<div class="stats">
<div class="stat hi"><span class="lab">below the mT<sub>ll</sub> wall</span><span class="val">0.0098%</span><span class="note">75 events of 662,103</span></div>
<div class="stat"><span class="lab">above the wall</span><span class="val">11.36%</span><span class="note">1,160× higher</span></div>
</div>

argmax=signal support is bounded at mT<sub>ll</sub> ∈ [52.8, 202] and m<sub>ll</sub> ≤ 100 —
despite `mtll` **not being an input feature**.

---

## 03 · Where the network puts tt̄ — and where the hand-made CR sits

### argmax=tt̄ density across the same plane, with the cut-defined top CR overlaid

![w:700](cr_topcr_argmax_tt_plane.png)

The tt̄ class fills a **broad** region — the cut box (mT<sub>ll</sub>≤60 & mT<sub>l2</sub>>30)
sits inside it but captures only **15.3%** of all argmax=tt̄ events. Purity inside the box is
42.5% vs 38.1% outside: the cut buys **+4 points of tt̄ fraction while discarding 85% of the
tt̄ the network already identifies.** That is the whole case for the MVA-defined CR on one plot.

---

## 03b · Same behaviour in the top CR — separation is learned, not cut

![w:720](cr_topcr_2d_plane.png)

Across the entire cut-defined top CR the argmax=signal fraction peaks at **0.48%**;
only **66 of 565,368** events are called signal (0.0117%), max P(H+c) = 0.358 — below the
0.5 needed to ever win argmax.

<div class="callout">

**The cut is redundant with the classifier.** The network independently recovers the same
region because both follow the same physics — not because it was trained on the cut.
`hww_MVA.yaml` has no mT/m<sub>ll</sub> cut in its base selection; labels are process truth.

</div>

---

## 04 · Cutting shrinks the training set the MVA needs

### Efficiency of each kinematic cut, on top of the ≥1 c-jet requirement

| cut | ε<sub>S</sub> | ε<sub>B</sub> | S/√B | gain |
|---|---:|---:|---:|---:|
| mT<sub>ll</sub> > 60 | 0.926 | 0.790 | 0.00091 | 1.04× |
| mT<sub>l2</sub> > 30 | 0.890 | 0.827 | 0.00086 | 0.98× |
| m<sub>ll</sub> ≤ 72 | 0.978 | 0.397 | 0.00136 | 1.55× |
| **all three (the SR)** | **0.845** | **0.271** | **0.00143** | **1.63×** |

<div class="flag">

**The cost, made concrete.** Putting `mll≤72` into the base selection empties the
high-m<sub>ll</sub> CR *by construction* — a region holding **2.38M events at 83.0% tt̄ purity**.
You trade a well-populated constraint region for a 1.63× pre-selection number the MVA does not need.

</div>

---

## 05 · The real lever: the charm tag, not the kinematics

<div class="stats">
<div class="stat hi"><span class="lab">c-jet eff — H+c signal</span><span class="val">23.1%</span><span class="note">medium WP discards 77% of signal</span></div>
<div class="stat"><span class="lab">c-jet eff — ggH</span><span class="val">15.9%</span><span class="note">the shape-degenerate competitor</span></div>
<div class="stat ok"><span class="lab">enrichment H+c / ggH</span><span class="val">1.46×</span><span class="note">ggH:H+c 681:1 → 467:1</span></div>
</div>

### Loose vs medium, measured offline on the untagged tree (5,619 H+c events, `hww_2dcat_nocjet`)

| c-tag option | signal N | eff of ≥1-jet base | vs medium |
|---|---:|---:|---:|
| medium (CvL>0.160, CvB>0.304) | 3,244 | 57.7% | 1.00× |
| **loose (CvL>0.054, CvB>0.182)** | **5,337** | **95.0%** | **1.65×** |
| no tag at all | 5,619 | 100.0% | 1.73× |

<div class="callout">

**Loosening the WP recovers 1.65× the signal — most of what dropping the tag entirely would give
(1.73×), while still rejecting light-flavour.** Compare the kinematic cuts, worth 1.63× on S/√B but
paid for with the control regions.

</div>

---

## 05b · The missing half: what the looser WP admits — and the answer is *no*

### `hww_ctag_compare`, 2022preEE, full MC — four categories over **one** untagged jet collection, weighted yields

| process | base (no tag) | medium WP | loose WP | kin, no tag |
|---|---:|---:|---:|---:|
| **H+c (signal)** | 1.79× | **1.00×** | **1.70×** | 1.56× |
| **ggH (degenerate)** | 2.92× | **1.00×** | **2.67×** | 2.16× |
| tt | 1.87× | 1.00× | 1.55× | 0.56× |
| V+jets | 2.39× | 1.00× | 2.23× | 0.34× |

<div class="stats">
<div class="stat"><span class="lab">signal gain, medium→loose</span><span class="val">1.70×</span><span class="note">what slide 05 measured</span></div>
<div class="stat hi"><span class="lab">ggH gain, medium→loose</span><span class="val">2.67×</span><span class="note">the half that was missing</span></div>
<div class="stat hi"><span class="lab">H+c/ggH enrichment retained</span><span class="val">0.64×</span><span class="note">loosening destroys 36% of it</span></div>
</div>

<div class="callout">

**ggH grows 1.57× faster than signal.** The charm tag exists to buy H+c-over-ggH
enrichment, and loosening the WP gives back **36%** of it. Dropping the tag entirely is
worse (0.62×). The acceptance gain on slide 05 is real but it is **not free** — this is the
measurement that decides it, and it says **keep the medium WP.**

</div>

---

## 06 · What this argument does not yet prove

- ~~**Loosening the WP admits more ggH too.**~~ **Now measured — see slide 05b.** ggH rises
  2.67× against signal's 1.70×, so the enrichment falls to 0.64×. CvL carries the
  H+c-vs-ggH separation (AUC 0.731), CvB does not (0.551 ≈ coin flip); a looser WP moves
  down the CvL axis and admits the degenerate background faster than the signal.
- **Purity is measured here; sensitivity is not.** These are event counts, not a limit. The
  limit also depends on how systematics act on a larger background.
- **Selection and SF boundaries do not coincide.** The 2D SF scheme bins on
  `x=CvL/(CvL+CvB(1−CvL))` and `y=1−CvB`; a rectangular WP cut is a different shape in
  that plane. Already true in production, but worth stating.

<div class="flag">

**Slides 01–05 are 2022postEE** (`hww_combine_fixed` MVA tree, raw counts); **slide 05b is
2022preEE** (`hww_ctag_compare`, weighted yields, full MC). The two agree on the signal
ratio to within a few percent across different eras, weighting, and code paths — the
raw-postEE loose/medium of 1.65× against the weighted-preEE 1.70×.

The **H+c and ggH samples are 100% complete** (7/7 and 4/4 partitions), so the
signal, ggH, and enrichment figures on slide 05b are final — they were unchanged between
the 174/191 and 186/191 snapshots. The tt and V+jets rows are drawn from 186/191 jobs.

</div>

---

<!-- _class: lead -->

## Summary

1. **MVA-defined CRs are purer than cut-defined ones** — 87.9% vs 78.1% on tt̄, and 2.8× the events.
2. **The MVA already applies the SR kinematic cuts internally** — 0.0098% vs 11.36% argmax=signal
   across the mT<sub>ll</sub> wall, with `mtll` not even an input.
3. **Cutting deletes the sidebands the network learns from**, and empties the CRs you need to fit.
4. **Neither acceptance lever is free.** Medium → loose recovers **1.70×** the signal —
   comparable to the 1.63× the kinematic cuts buy — but admits ggH at **2.67×**, giving back
   36% of the H+c/ggH enrichment. **Keep the medium WP.** The kinematic cuts buy 1.63× on
   S/√B but empty the CRs. The MVA-defined regions remain the one change that costs nothing.

<footer>Slides 01–05: 2022postEE, v11 6-class MVA [hplusc, higgsbkg, tt, st, diboson, vjets], pooled MC 4,046,127 events, raw · Slide 05b: 2022preEE hww_ctag_compare, weighted yields, full MC · purity = true-process fraction</footer>
