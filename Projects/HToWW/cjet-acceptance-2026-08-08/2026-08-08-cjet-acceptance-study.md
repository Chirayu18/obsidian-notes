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

## Status (2026-08-08 ~02:05)

- Submitted 01:44–01:54. Variants 1 & 2: 6 jobs each. Variant 3: **496 jobs**, all running.
- Variants 1 & 2 hit transient **XRootD timeouts** (below); a retry loop is running.

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

## Results

*(pending — jobs running)*

## Files

| file | content |
|---|---|
| `run_all2.sh` | tmux submission driver for all three variants |
| `retry.sh` | resubmit loop for the XRootD-flaky signal variants |
| `acceptance.py` | raw counts + weighted yields vs baseline |
