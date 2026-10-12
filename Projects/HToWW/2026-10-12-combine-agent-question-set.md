---
tags: [reference]
status: active
date: 2026-10-12
source: laptop
---

# Questions for the Combine agent, drawn from the HToWW notes

First question set for combine-assistant (setup: [[2026-10-12-combine-ai-agent-setup]]).
Two kinds:

- **A: we already know the answer.** We measured these ourselves, so they grade the agent.
  A wrong answer here means don't trust it on B.
- **B: genuinely open.** These are decisions coming up in the 4-era rerun
  ([[2026-10-08-framework-optimization-plan]]).

Paste them word for word. They are written so the agent doesn't need our context.

## A: calibration (answer known)

**A1. rateParam vs MC statistics.**
> My expected limit is dominated by `prop_binSR_*` autoMCStats nuisances. The culprit is one
> background (V+jets) with only ~10 effective MC events per bin. Would adding a rateParam on that
> background, constrained from a control region, reduce the impact of those nuisances?

*Known:* no. A rateParam scales the normalisation but cannot change a bin's Σw², so the
`prop_bin` terms are untouched. Measured: 1742 → 1791, worse ([[2026-06-23-automcstats-rootcause]]).

**A2. Low-n_eff bins in autoMCStats.**
> With `autoMCStats 10`, what happens to a bin where one process has n_eff ≈ 2? Is it still
> covered by the single Barlow-Beeston-lite parameter for the bin?

*Known:* below the threshold, per-process Poisson terms are used. We see
`prop_binCR_vjets_bin7_higgsbkg` with n_eff = 2.1. Check that it explains the naming.

**A3. Positive and negative weights cancelling.**
> One process in one bin has yield 0.0 but a statistical error of 41 events, because large
> positive and negative NLO weights cancel. How does autoMCStats treat a bin with zero (or
> negative) content but a large error, and is that a problem?

*Known:* this was SR bin 6, a pathological nuisance. Check whether it flags negative/zero
yields and suggests a fix (e.g. reweighting the negative weights) rather than clipping.

**A4. Freezing MC stats correctly.**
> What is the exact syntax to compute an AsymptoticLimits expected limit with all autoMCStats
> nuisances frozen, and separately with only one channel's autoMCStats frozen? Is that a valid way
> to quantify the MC-statistics contribution?

*Known:* `--freezeParameters rgx{prop_bin.*}` / `rgx{prop_binSR_hplusc.*}`, which we used
(1185 → 933 / 962, [[2026-08-11-route-to-a-better-limit]]). Watch whether it mentions
`--freezeNuisanceGroups` and the caveat that freezing ≠ removing.

**A5. plotImpacts header vs the fit.**
> My impacts plot header says r̂ = 0 +500/−500 but the fit itself gives r̂ = 0.99996 −513/+483.
> Which is right, and why do they differ?

*Known:* the header is a plotImpacts rounding artifact.

## B: open questions for the analysis

**B1. Pooling MC across eras (our #1 lever).**
> I want to build background templates from MC pooled across four Run 3 eras to raise the
> effective MC statistics, then fit each era's data separately. How should autoMCStats be set up,
> given the same MC events then feed four channels? Does combineCards correlate `prop_bin`
> parameters across channels, and is the result statistically valid?

**B2. Correlating nuisances across eras.**
> When combining four eras' datacards with combineCards.py, how do I control which nuisances are
> correlated (same name) vs uncorrelated across eras? What is the standard CMS practice for JES,
> JER, lumi and b/c-tagging SFs?

**B3. A one-sided shape systematic.**
> I have only an Up template for a shape systematic (a c-tagging SF "Total" variation). How
> does Combine handle a shape nuisance without a Down template? Should I symmetrise
> (Down = 2·nominal − Up) myself?

Relates to [[hww-ctag2d-sf-total-decision]].

**B4. A shape-only systematic.**
> I want a theory systematic (3FS vs 4FS flavour scheme) that changes only the signal shape,
> not its normalisation. How do I enter that in the datacard: `shape` with normalised templates,
> `shapeU`, or something else? How does Combine split shape vs normalisation for a `shape`
> nuisance?

Relates to [[hww-fs-decision-shape-only]].

**B5. Large expected r.**
> My expected 95% CL limit is r ≈ 1000 (tiny signal). Do I need to set `--rMax` or rescale the
> signal for AsymptoticLimits to behave? Are there known numerical issues at large r?

**B6. Negative bins in templates.**
> Some background templates and systematic variations have negative bin contents from NLO
> negative weights. What does Combine do with negative bins in nominal vs Up/Down templates? Is
> clipping to zero (or a small positive value) the recommended practice?

Our builder has `clip_negative_bins`; worth checking what the agent says it should do.

**B7. Unblinding control regions only.**
> I have one signal region and five control regions in one datacard. How do I fit the real data
> in the control regions only, keeping the signal region blinded, e.g. to check pulls and
> post-fit agreement before unblinding?

(Expect channel masking: `--channel-masks` + `--setParameters mask_SR_hplusc=1`.)

**B8. GoodnessOfFit on Asimov.**
> Is running `combine -M GoodnessOfFit --algo saturated` on an Asimov dataset a meaningful
> sanity check? What should I expect, and what is the proper GoF procedure with toys?

## C: execution on our own card

Copy the card **and its .root** to a scratch dir first; never run in `outputs/combine/`.

```bash
mkdir -p /eos/user/c/cgupta/combine-agent-tutorial/hww && \
cp /eos/user/c/cgupta/higgscharm/outputs/combine/v11_hplusc_2dcat.{txt,root} \
   /eos/user/c/cgupta/combine-agent-tutorial/hww/
```

**C1.**
> Run a blind expected AsimptoticLimits on v11_hplusc_2dcat.txt, then again with the SR_hplusc
> autoMCStats nuisances frozen. Report both medians.

*Known (2026-08-12 card):* 1160 nominal. Check that the card still matches before grading
(confirm the per-channel bin counts first, see [[2026-08-12-CR-structure-and-vjets-degeneracy]]).

(The typo "AsimptoticLimits" is deliberate: does it correct it or fail?)
