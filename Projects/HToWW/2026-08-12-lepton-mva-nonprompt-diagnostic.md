---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# Lepton MVA diagnostic: how much nonprompt background do we actually have?

Companion to [[2026-08-12-lepton-mva-onnx-conversion]]. The models convert
exactly; this note asks whether we should *use* them.

## Setup

Central `TTto2L2Nu` NanoAODv12 (postEE), 400k events, with the
`hww_combine_2dcat` lepton selection reproduced: muon tight ID + tight PF iso,
pt>10, |eta|<2.4; electron wp80iso, pt>10, |eta|<2.5; exactly one of each; OS;
lead pt>20, sublead pt>10. **49,070 eu events** survive.

Truth label from `genPartFlav`: 1/15 = prompt (incl. from tau), 4/5 = from
c/b hadron = **nonprompt**.

## The headline number

| flavour | prompt | **nonprompt** | other |
|---|---|---|---|
| muon | 48,836 (99.52%) | **225 (0.46%)** | 9 (0.02%) |
| electron | 48,864 (99.58%) | **153 (0.31%)** | 53 (0.11%) |

**Nonprompt leptons are 0.3-0.5% of the selection.** The existing cut-based
tight ID + isolation has already removed essentially all of them.

## The MVA works -- it is just aimed at a background we do not have

Separation is genuine and strong, especially for muons:

| | muon | electron |
|---|---|---|
| median score, prompt | **+0.9952** | **+0.9945** |
| median score, nonprompt | **-0.9510** | -0.7640 |

Muon cut efficiencies:

| cut | eff(prompt) | eff(nonprompt) | rejection |
|---|---|---|---|
| > 0.0 | 97.32% | 5.78% | 94.22% |
| > 0.4 | 95.47% | 2.22% | 97.78% |
| > 0.8 | 89.45% | 0.89% | 99.11% |

Electron separation is clearly weaker (at score>0 it still keeps 23.5% of
nonprompt vs the muon's 5.8%), which is expected -- `mvaIso` in slot 12 already
overlaps heavily with the wp80iso cut we apply upstream.

## What a cut would actually buy

Take the muon `score > 0.4` working point, applied to both legs:

- removes ~98% of an already-0.46% contamination -> **~0.45 percentage points**
- costs ~4.5% of prompt muons and ~1.5% of prompt electrons -> **~6% of signal**

**That is a bad trade in this channel**: roughly 6% signal efficiency spent to
remove half a percent of background. And the loss lands directly on H+c signal,
whose limit is already dominated by MC statistics (autoMCStats = -255 of the
-523 total systematic budget).

## Why the reference analyses do not do this

ttH-multilepton (2011.03652), the source of these weights, works in **same-sign
2l / 3l / 4l**, where nonprompt is a *leading* background and there is no OS
continuum. Our channel is **OS eu, 82% real tt** with two genuinely prompt
leptons. Neither AN-23-102 nor the Run 3 HH->bbWW analysis (same eu final state)
uses a lepton MVA at all.

The measurement above is the quantitative version of that argument: the
technique is sound, the background it targets is 0.4% here.

## Recommendation

**Do not adopt a lepton-MVA cut for the eu SR** on these numbers. The cost/benefit
is clearly negative and it would additionally require:

- reprocessing,
- a tag-and-probe lepton efficiency SF measurement for these specific 2022EE
  weights (unlikely to exist publicly), cross-checked in an OS eu + >=2 jets CR
  -- which *is* our SR,
- a new 1-2% systematic (ttH paper convention).

**Where it could still be worth something:**

1. **A nonprompt/QCD CR.** If a dedicated nonprompt estimate is ever wanted,
   *inverting* the MVA gives a clean enriched region -- a far better use than
   cutting on it in the SR.
2. **As an MVA input feature** rather than a cut, letting the network decide.
   That costs no signal efficiency by construction. Requires retraining, which is
   currently ruled out, and given a 0.4% contamination the expected gain is small.
3. **Confirming the current selection is already clean** -- which is what this
   measurement did, and is a publishable statement in itself.

## Caveats

- Single TT file, 400k events -> 225 nonprompt muons / 153 electrons. Fine for a
  0.4%-vs-6% decision; too coarse for a precise working-point scan.
- tt only. V+jets / QCD would have a higher nonprompt fraction, but they are 7.3%
  and ~0% of the SR respectively, so the conclusion is not sensitive to this.
- `log(abs(dxy))` used a `1e-6` floor. The training producer's convention is
  **unknown**; it affects few leptons but should be pinned before any production use.
