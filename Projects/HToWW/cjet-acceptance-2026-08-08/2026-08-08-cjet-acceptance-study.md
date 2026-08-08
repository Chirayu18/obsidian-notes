---
tags: [reference]
status: active
date: 2026-08-08
source: lxplus
---

# c-jet acceptance study — 2022postEE

**Question.** The ≥1 c-jet requirement (medium PNet WP) keeps only **23.1%** of H+c
signal, while the kinematic cuts (mTll/mll/mTl2) keep **84.5%** of signal and remove
**73%** of background. Can we recover signal acceptance by loosening or dropping the
charm tag, and buy the background back with the kinematic cuts?

Background and the measurements that motivated this:
[[2026-08-07-v11-argmax-implicit-cuts]].

The decisive prior result: **CvL carries the H+c-vs-ggH separation (AUC 0.731); CvB does
not (0.551 ≈ coin flip)**, and signal sits deeper in the charm region than ggH (21.0%
near threshold vs 46.2%). So the tag is the *only* handle on ggH, which is
shape-degenerate with the signal — acceptance alone cannot decide this, which is why the
study ends in a training + ROC comparison rather than a yield table.

## The three variants

All derive from `analysis/workflows/hww_combine_2dcat.yaml`, one selection line apart
(plus repointed `combine.output`). Each was diffed against the base and loaded through
`WorkflowConfigBuilder` before submission.

| workflow | change | datasets |
|---|---|---|
| `hww_2dcat_nocjet` | `jet_ctagging` line **removed** | signal only |
| `hww_2dcat_looseWP` | `'medium'` → `'loose'` | signal only |
| `hww_2dcat_nocjet_kin` | no tag + `-1` sentinels + kinematic cuts in `base` | all MC + data |

WP thresholds (PNet, 2022postEE): medium `CvL>0.160, CvB>0.304`;
loose `CvL>0.054, CvB>0.182`.

Variant 3 additionally:
- `ak.fill_none(..., -1)` on all four candidate-c-jet features (hadronFlavour, CvL, CvB, pt)
- `transverse_mass_signal` (mTl2>30 & mTll>60) and `dilepton_mass_signal` (mll≤72)
  added to `categories.base` → 10 base selections instead of 8

`atleast_one_cjet` is kept in all three; with no tag it means "≥1 good jet", which keeps
`candidate_cjet` and the `cjet_cand_*` features defined.

## Status — processing COMPLETE (2026-08-08 ~05:00)

Submitted 01:44–01:54; all jobs finished by ~05:00. **All three variants reached 7/7
signal partitions** and the queue drained to zero.

The `nocjet` XRootD failures (below) resolved on their own: the retry loop's second
attempt succeeded once variant 3's 466 jobs drained and IIHE contention dropped —
confirming the diagnosis was endpoint throttling, not bad files. The planned
`--nfiles 3` mitigation was never needed.

## Two operational gotchas worth remembering

**1. The grid proxy is node-local.** `voms-proxy-init` writes `/tmp/x509up_u<uid>` on
**one** lxplus node. Reconnecting to a different node loses it, and `submit_condor.py`
then dies with "VOMS proxy expired or non-existing" even though the proxy is perfectly
valid. The fix is to point at the AFS copy, which `submit_condor.py` itself writes and
which is shared across nodes:

```bash
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
```

**2. Long submissions must not depend on the ssh master.** A `nohup … & disown` still
died when the ssh control master was reset. Use `tmux` instead — `run_all2.sh` and
`retry.sh` both run under it and survive disconnects.

**3. The private signal NanoAOD read is flaky.** H+c postEE lives on
`maite.iihe.ac.be` (the per-era redirector, see [[hww-signal-private-fetch-iihe]]) and
reads time out intermittently:

```
OSError: XRootD error: [ERROR] Operation expired
in file root://maite.iihe.ac.be:1094//store/user/cgupta/HPlusCharm_HToWW_...NANO_NANO_21.root
```

4 of 6 jobs failed this way on the first pass, leaving 4/7 partition dirs. It is
transient — resubmitting is the remedy, which `retry.sh` does automatically (up to 6
attempts per variant, waiting for the queue to drain between tries).

**Consequence for reading yields:** a partial tree gives a *lower* count than the
baseline, which is impossible for a strictly looser selection. That is the sanity gate —
`nocjet ≥ looseWP ≥ baseline` in raw signal count. If it fails, the tree is incomplete,
not the physics.

**4. Waiting on a workflow's jobs needs the CLUSTER ID, not the workflow name.**
`condor_q -nobatch | grep <workflow>` matches nothing — the queue listing shows the
executable and args, not the workflow name. A retry loop built on that check thinks the
queue is empty and resubmits on top of jobs that are merely waiting for a slot. Parse
`submitted to cluster <N>` out of the submit log and poll `condor_q <N> -af ProcId`
instead (`retry.sh` does this).

The missing partitions were consistently **_1, _2, _3** across attempts, which looked
like specific bad input files rather than random timeouts. **Checked directly — it is
not.** `xrdfs maite.iihe.ac.be stat` returns a valid size for all of them, including
`NANO_NANO_21.root`, the exact file named in the XRootD error:

```
NANO_NANO_1.root:  Size: 7808780
NANO_NANO_21.root: Size: 7762372
NANO_NANO_41.root: Size: 7803452
```

So the files are healthy and reachable; the failures are genuine transient timeouts
under load (the whole 496-job variant-3 campaign was hammering the same endpoints).
Retrying is the correct remedy — no need to re-fetch via a different redirector.

## Two more gotchas, from the postprocess step

**5. `run_postprocess.py` has no `--mva` flag.** [[2026-07-24-run-analysis-steps]] step 4
gives

```bash
python3 run_postprocess.py --workflow ... --postprocess --output_format parquet --mva
```

but `--mva` is not in this repo state's argparser and the call dies with
`unrecognized arguments: --mva`. The correct invocation is

```bash
python3 run_postprocess.py -w <workflow> -y 2022postEE --postprocess --output_format parquet
```

**6. Piping a step into `tee` masks its exit code.** `cmd | tee -a log; echo exit=$?`
reports the exit status of `tee`, which is essentially always 0. The first chain run
therefore logged `exit=0` three times while all three steps had failed, and only the
59-second total runtime gave it away. Capture `${PIPESTATUS[0]}`, or redirect to a file
and `tail` it afterwards (what `v3_chain2.sh` does), and abort the chain on the first
real failure instead of letting it cascade.

## Variant 3 mechanism checks (both pass, with one subtlety)

Run on the first 40 signal shards once variant 3's signal reached 7/7.

**Kinematic cuts in `base` — correct.** 100.00% of events satisfy each of
`mTl2 > 30`, `mTll > 60`, `mll <= 72`. They are genuinely applied at processing time.

**`-1` sentinel — present, but read it carefully.**

| column | min | `== -1` | NaN |
|---|---:|---:|---:|
| `cjet_cand_cvsl_pnet` | -1.000 | 10 (1.5%) | 0 |
| `cjet_cand_cvsb_pnet` | -1.000 | 10 (1.5%) | 0 |
| `cjet_cand_pt` | 20.03 | **0** | 0 |

The asymmetry is not a bug in the yaml — all four expressions are written identically
(`ak.fill_none(ak.pad_none(..., target=1).X, -1)`, lines 546/553/560/612). Checking the
sentinel events directly:

- they have **real `cjet_cand_pt` of 20–23 GeV**, so a candidate c-jet *does* exist
- CvL and CvB are `-1` for exactly the same 10 events (perfect overlap)
- their `jet_multiplicity` is **0** — the jet passes the `cjets` pT>20 cut but not the
  `jets` pT>30 cut

So these −1s **come from NanoAOD itself**, where the PNet discriminants are stored as −1
for jets whose tagger output is undefined; `fill_none` never fired. Non-sentinel events
span CvL 0.0335–0.9995 and CvB 0.0005–0.9907, i.e. the physical [0,1] range.

**Consequence for the training:** −1 is now doing double duty — "no c-jet" (the intended
sentinel) and "PNet undefined" (from NanoAOD). At 1.5% of signal events it will not
drive the result, but the two cases are not distinguishable in the feature, and the
network will read both as the same out-of-range value. If the ROC comparison turns on
these events, separate the cases with an explicit `has_cjet` flag rather than overloading
−1.

## Results — signal acceptance

Weighted = `lumi*xsec/sumw` via `read_scale`, i.e. the same normalisation the fit uses.
Sanity gate **passes**: `nocjet ≥ looseWP ≥ baseline` in raw count.

| variant | raw N | weighted | vs baseline |
|---|---:|---:|---:|
| baseline (medium WP) | 1,925 | 0.2910 | 1.00× |
| **1: no c-tag** | 3,285 | 0.5138 | **1.71×** |
| **2: loose WP** | 3,136 | 0.4853 | **1.63×** |
| 3: no-tag + kinematic cuts | 2,801 | 0.4425 | 1.46× |

**The headline: loose WP captures 1.63× of the 1.71× available.** Going all the way to
no tag buys only a further 5% relative in signal, while giving up the charm requirement
entirely — and with it the only handle on ggH. On acceptance-per-unit-risk, **the loose
WP is the standout**: nearly all the gain, a selection that still rejects light jets, and
the existing 2D SF machinery applies unchanged.

Variant 3 sits *lower* than variants 1 and 2 because the kinematic cuts (`mTl2>30`,
`mTll>60`, `mll≤72`) are applied on top — 1.46× vs 1.71× is the 85% kinematic efficiency
acting on the no-tag sample, exactly as predicted from the earlier measurement.

**These are acceptance numbers only and do not settle the question.** Signal is up in
every variant by construction; what matters is whether the network can still separate
H+c from ggH once the tag is loosened. That is the ROC comparison, below.

## Files

| file | content |
|---|---|
| `run_all2.sh` | tmux submission driver for all three variants |
| `retry.sh` | resubmit loop for the XRootD-flaky signal variants |
| `acceptance.py` | raw counts + weighted yields vs baseline |
