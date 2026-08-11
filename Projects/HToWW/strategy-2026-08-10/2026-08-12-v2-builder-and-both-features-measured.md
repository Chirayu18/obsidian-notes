---
tags: [reference]
status: active
date: 2026-08-12
source: lxplus
---

# v2 card builder: per-channel binning + process/class decoupling, both MEASURED

New file `scripts/combine/make_combine_inputs_v2.py` (277 lines). The original
`make_combine_inputs.py` is **untouched**, so **r < 1160** stays exactly reproducible.

## The verdict — both new features HURT the 1POI limit

| configuration | stat-only | full | vs best |
|---|---:|---:|---:|
| **merged higgsbkg, CRs 10-bin** | **637** | **1160** | — ⭐ best |
| ggH split only, CRs 10-bin | 637 | 1185 | **+25** |
| ggH split + CRs yield-only | 638 | 1235 | **+75** |

**Decomposed: the ggH split costs 25, the yield-only CRs cost 50.** Independent and additive.
Config reverted to the 1160 state; both features remain available behind yaml keys.

## Why the yield-only CRs cost 50 — our CRs are not AN-24-091's CRs

AN-24-091 Table 10 makes **every** CR a single bin, and AN-23-102 line 662 makes the top CR
yield-only. Both precedents are real, but they do not transfer, because their CRs are
**dedicated cut-based regions**, each built to constrain one background. Ours are
**argmax-defined and heavily tt-contaminated**:

| our CR | tt fraction |
|---|---:|
| CR_st | 87% |
| CR_diboson | 72% |
| CR_vjets | 50% |

So our CR *shapes* are doing real constraining work across processes, not merely fixing a
normalisation. Collapsing them to yields throws that away. **A yield-only CR is right for a
pure CR; ours are not pure.**

## Why the ggH split costs 25 — it is more correct, not more sensitive

Splitting lets the AN's **real 50%** apply to ggH alone instead of the 1.066 average a merged
group forces. Measured with the nuisance frozen:

- **1185 card** (split): freezing `flavor_composition_ggH` → 1209, i.e. it costs **26**
- **1160 card** (merged): freezing it → 1159, i.e. it costs **1**

The 1.066 was so watered down it did almost nothing. The split does not add uncertainty — it
**stops hiding** uncertainty the AN says is there. The cost is the price of correctness.

**Keep the split available**: it is the prerequisite for the 2POI fit (AN-23-102 v10 splits
`bkg-H` into `bkg-H+c`/`bkg-H+notc`), and once the reprocessing campaign lands the per-event
`higgs_plus_c` weight supersedes the whole scoping question anyway.

## Bonus finding: `CMS_ctag2d_2022` is the most expensive shape nuisance

Freezing it on the 1160 card gives **1125** — a **35-unit** cost, larger than the ggH split.
For comparison on the same card: `CMS_scale_j` 1, `CMS_res_j` 0, `pileup` 0, `lhe_pdf` 1.

This raises the priority of the ctag2d decomposition (currently one `up_Total/down_Total`;
HiggsDNA splits it into Extrap/Interp/Stat/PUWeight/XSec_BRUnc_*). See
[[hww-ctag2d-sf-total-decision]] — the deferral was reasonable, but it is now the largest
single measured shape systematic.

## The v2 builder

Thin wrapper: imports `make_combine_inputs` and reuses `process_sample`, `gather_samples`,
`build_variations`, `clip_negative_bins`, `smooth_shape_variations`, `to_uproot_th1` and
`write_datacard` unchanged. Overrides only the two ROOT writers (single `edges` → per-channel)
and the process derivation.

**Both features are opt-in. With neither key set, v2 produces a byte-identical datacard.**

### The equivalence test earned its keep

The first v2 run produced a card **missing all six object-shift systematics** — `main()` never
implemented the shift-directory pass. Had the features been enabled straight away, the limit
would have moved for the wrong reason. After adding the pass (+ the LOWESS hook):

```
Folded 6 object-shift systematics: [CMS_res_e, CMS_res_j, CMS_res_m,
                                    CMS_scale_e, CMS_scale_j, CMS_scale_m]
DATACARD IDENTICAL
```

### Feature 1 — per-channel binning

```yaml
combine:
  binning:
    edges: [0.0, 0.2, ...]        # default for unlisted channels
    per_channel:
      CR_tt: [0.0, 1.0]           # 1 bin -> yield-only
```

### Feature 2 — process/class decoupling

```yaml
combine:
  processes: [hplusc, ggH, higgsbkg, tt, st, diboson, vjets]
  process_map:
    ggH:      [ggH, ggZH]
    higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]
```

Channels stay one-per-class (that is what argmax means); a datacard *process* is just a row.
**This is how to split ggH without retraining.**

**The silent-drop bug is now a hard error.** Reproduced deliberately:

```
KeyError: process_map has keys ['ggH'] absent from combine.processes -- their samples
would be SILENTLY DROPPED (the 2026-08-11 ggH bug).
```

Verified clean this time: SR total unchanged at 20664.132, with ggH (102.762) +
higgsbkg (28.330) = 131.092, exactly the old merged value.

## Standing conclusion

**1160 remains the best 1POI limit.** Both features are correctness improvements that cost
sensitivity, and both stay one yaml key away. Revisit when:

- the **2POI fit** is attempted → the ggH split becomes mandatory
- the **reprocessing campaign** lands → `higgs_plus_c` supersedes the scoping question
- **CR purity** improves → yield-only CRs stop discarding useful constraints
