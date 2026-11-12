---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# Run A and Route B TRAIN: second recovery round, 12 Nov 2026 (13:07–13:40 CET)

**Status: agent-reported.** 401 targeted retries submitted: Run A 52, Route B 349. None has finished, so nothing is recovered or validated yet. The one deterministic failure, 2023preBPix GluGluHto2Tau p1, needs a decision from Chirayu (section 5).

**Authorization.** Chirayu, 13:04 Brussels: "Forget this, can you continue the jobs from the overnight thing? Launch the subagents again". The parent brief authorizes safe, targeted resubmission of proven failed or missing partitions of these same productions.

**Prior state.**
- [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-run-a-periodic-check]]: final census at 03:34.
- [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-run-a-train-v2-failure-recovery]]: first retry batch and method.
- [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-interrupted-handoff]] and [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train]]: Route B submission and handoff.

**Not changed:**
- analysis code, hashed corrections or selection;
- shared filesets and original `condor/<wf>/…` `jobnum.txt` / `partitions.json` / `.sub` files;
- the wrapper `condor/submit.sh`;
- credentials and the proxy;
- EOS outputs: nothing deleted or overwritten;
- the queue: no release or removal; held Run A job `9701317.23` is untouched;
- b-hive, mva and negrw files.

Nothing was pushed.

Paths:
- `R = lxplus:~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
- `W = lxplus:~/htoww_submit_logs/ab_recovery_20261112pm/`, which holds every script, TSV and log named below.

## 0. Snapshot before any action (13:07:53 CET, lxplus932)

- `R` is on `hww-analysis`, HEAD `0995853`. The only commit since Route B was submitted is `3a03245..0995853`, which adds `scripts/negrw/make_negrw_v2_plots.py`.
- Uncommitted diff: `scripts/mva/bhive_fold_commands.py` and `scripts/mva/register_folds.py` (b-hive owner, not touched). `git diff | sha256sum` = `47418e2aa612ad9e…`.
- `analysis/processors/base.py` mentions `scripts/mva` only in a comment, so job processing does not import it.
- File sha256 prefixes: `hplusc_routeb.py 5b4e256b4fdfd826`, `routeb_io.py eb9bb58752ee3a19`, `stitching/__init__.py b77acc70d6e8c6a9`, `condor/submit.sh 33f9ebd683549429`, `corrections/jerc.py 3e09a3e4d8ec03d7`.

**Frozen hashes** (`W/hashcheck2.py`, run in the job image `coffea-base-almalinux9:0.7.30-py3.10`; markers copied to `/tmp/cgupta_abhash_GYRT` with `xrdcp`):

| workflow | current tree: features / selection | markers checked |
|---|---|---|
| A `hww_allfix_4fs` | `36f655f4724cb1a4` / `80e75bca3f231c49` | DY-50_48 (first-retry batch) and 2023postBPix TTto4Q_1: **match** |
| B `hww_routeb_3fs4fs` | `36f655f4724cb1a4` / `24b63ba31bf672de` | 2023preBPix HplusCharm_3FS_1, 2022postEE HplusCharm_3FS_ext1_2 and WZ_2: **match**. `routeb_stitching` sha256s equal the current files (above). |

The new retries run the same tree, so they should carry the same provenance. This is to be confirmed on their markers.

## 1. Census (13:09:23 CET, EOS server)

Method (`W/census2.py`):
- Expected partitions: `R/condor/<wf>/<era>/<ds>/jobnum.txt`.
- Markers: `eos root://eosuser.cern.ch ls` per sample directory, read from the EOS server, not the mount.
- Live queue: joined on era, dataset and the **first Args token**. Both batches are included, since the filter is by UserLog path and not by batch name.

| era | A expected | A markers | A gaps | B expected | B markers | B gaps |
|---|---:|---:|---:|---:|---:|---:|
| 2022preEE | 506 | 506 | 0 | 523 | 456 | 67 |
| 2022postEE | 1188 | 1183 | 5 | 1246 | 1066 | 180 |
| 2023preBPix | 640 | 604 | 36 | 679 | 613 | 66 |
| 2023postBPix | 393 | 381 | 12 | 414 | 377 | 37 |
| **total** | **2727** | **2674** | **53** | **2862** | **2512** | **350** |

- A: 231 sample directories; B: 236. Zero `eos ls` errors.
- Live queue: only held `9701317.23`, whose marker is present, and one unrelated held non-A/B job.
- Zero duplicate live keys and no gaps in the queue. This is identical to the 03:34 census.

## 2. Failure diagnosis

Script: `W/diag2.py` → `W/diag_A.tsv` and `W/diag_B.tsv`. For each gap it reads the newest `.err` file (A clusters ≥ 9701215, B ≥ 9701608), matched by the trace line `+ JOBID=<n>`, plus the execution host from the matching `.log`.

| category | A | B | where |
|---|---:|---:|---|
| **Bad worker node `b9p29p4279.cern.ch`: initial `voms-proxy-info` "Couldn't find a valid proxy"** | 20 | 0 | all 20 from the first A retry batch |
| Bad node `b9p29p4279`: `TimeoutError [Errno 110]` reading hashed inputs from AFS | 2 | 2 | B includes **HplusCharm_3FS_HToWW_ext1 p1** (2022postEE) |
| XRootD `[3010]` at UFL `cmsio3.rc.ufl.edu` | 19 | 141 | A: all original jobs |
| XRootD `Operation expired` | 10 | 197 | A: 7 UCSD (original), 2 KFKI + 1 FNAL (first retry batch); B: 194 UCSD, 2 KFKI, 1 FNAL |
| AFS `[Errno 5] Input/output error` on the repo path, on other nodes | 1 | 7 | one per node; B includes 2 chained into "Failed processing file" |
| XRootD `[3004] Unable to readv` (vanderbilt) | 0 | 1 | |
| corrupt read (`expected Chunk of length`, UFL) | 0 | 1 | |
| deterministic `jerc.py:377` (GluGluHto2Tau p1) | 1 | 1 | see section 5 |

**The "proxy" failures are a bad worker node, not the credential.**
- All 24 A+B jobs that ran on `b9p29p4279.cern.ch` between 00:27 and 02:09 failed. None succeeded there.
- The failures were proxy-read failures, AFS EIO and AFS read timeouts.
- Example: `9701996.2` got through input transfer, then exited within 1 s at `voms-proxy-info -all -file /afs/.../private/x509up_u151861`, before touching any input site.

Why the node, and not the credential:
- The jobs read the proxy from AFS. The `.sub` passes the path as an argument; it is not in `transfer_input_files`.
- `~/private` is ACL `cgupta rlidwka` only, and the repo directory gives `system:anyuser` lookup only. So a node that cannot serve authenticated AFS fails at the proxy read, and would fail later reading code anyway.
- On lxplus at 13:08 the proxy had 529800 s left (about 147 h, mode 600, mtime 10 Nov 16:18), and Kerberos was valid until 13 Nov 13:40.
- 272 retry jobs on other nodes used the same AFS proxy path successfully.
- **No credential change is needed.** The fix is job-only: a `requirements` exclusion of that machine.

## 3. Retry staging (originals untouched)

Script: `W/build_retry2.py` writes `W/stage_{A2,B2}/<era>/<ds>/`, the same scheme as the 02:00 batch:

- `partitions.json`: **retry keys only**, with the same LFNs in the same order. Checked: A 52 / B 349 partitions, `lfn_mismatch 0`, and no UCSD/UFL URLs left.
- Replica rewrites; each one keeps the same `/store` LFN, which is asserted:
  1. Proven-bad hosts `redir.t2.ucsd.edu` / `cmsio3.rc.ufl.edu` → `root://xrootd-cms.infn.it/`. A 113 URLs, B 814.
  2. The specific URL named in that partition's failing XRootD error → EU redirector. A 3 (KFKI/FNAL), B 4 (KFKI/FNAL/vanderbilt).
  3. Five LFNs that failed stat at the EU redirector but are OK at the global one → `root://cms-xrd-global.cern.ch/` (`W/override.tsv`, B only).
- `retry.sub`, which is the original `.sub` plus:
  - the staged `partitions.json`;
  - `Queue JOBNUM from retry.txt`;
  - a per-job `initialdir` (`p<n>/`), so sandbox returns no longer go to the repo root, which caused the `9701317.23` hold;
  - `requirements = (Machine =!= "b9p29p4279.cern.ch")`.

  Everything else is unchanged: executable, arguments (same AFS proxy path), image, memory, CPUs, flavour, and log/out/err paths, which get new cluster IDs.
- Excluded (`W/exclude2.tsv`): 2023preBPix GluGluHto2Tau p1, in both A and B.

**Replica probes** (`W/probe.py`, `W/reprobe.py`, `xrdfs stat` with the existing proxy):
- At 8-way parallelism: 820/934 OK.
- The 114 failures re-probed at 4-way: 109 OK at the EU redirector, 5 OK only via global (also OK at UCSD), so these got the override.
- The first, load-related failures match the 01:40 observation (24-way vs 6-way).
- Stat does not prove a full read. A few retries may still fail on input access.

**Dry run:** `condor_submit -dry-run` plus `W/check_dryrun2.py` on all staged files. **A 18 datasets / 52 procs OK; B 68 / 349 OK.** For each proc: Args partition = `retry.txt`, `Iwd = …/p<n>`, staged `partitions.json` first in `TransferInput`, and `Requirements` starts with `((Machine =!= "b9p29p4279.cern.ch")) && (TARGET.Arch == "X86_64") …`.

`W/stage_A`, `W/stage_B` are the first build before the 5 overrides. They were **not submitted** and are kept for reference.

## 4. Submission (13:34:26–13:35:15 CET)

`W/submit_retry2.py` takes a fresh `condor_q` per workflow and runs `eos ls` per dataset immediately before each `condor_submit`. Any clash skips the whole dataset; there were **0 clashes, 0 skips**.

| batch | workflow | datasets | jobs | clusters | per era |
|---|---|---:|---:|---|---|
| `runA_v2_retry2_20261112pm` | A | 18 | **52** | 9704354–9704371 | postEE 5, preBPix 35, postBPix 12 |
| `routeb_train_retry_20261112pm` | B | 68 | **349** | 9704372–9704441 except 9704387 and 9704419 (not ours) | preEE 67, postEE 180, preBPix 65, postBPix 37 |

- Per-dataset cluster mapping: `W/submit_A2.log`, `W/submit_B2.log`.
- Queue at 13:35:21: A retry 52 idle, B retry 349 idle, held `9701317.23`. **0 duplicate (workflow, era, dataset, partition) keys.**
- If every retry succeeds, A reaches 2726/2727 and B 2861/2862 markers. The missing partition in each is GluGluHto2Tau.

## 5. Decision needed: 2023preBPix GluGluHto2Tau (A and B, partition 1)

**The 11 Nov premise was wrong.** The notes from 11 and 12 Nov called `e182930b-b855…` the good file and `1d4e1a08-9b2c…` the bad one. The one-file retry from 11 Nov (cluster `9697157`, only `e182930b`) **also failed**, with the same `ValueError: in ListArray64 attempting to get 5, index out of range` at `jerc.py:377` (`events.GenJet[genjetidx]`). The log is `R/condor/logs/hww_allfix_4fs__train_v1_20261110/2023preBPix/GluGluHto2Tau/*.9697157.0.err`. Every attempt so far (9696807, 9697157, 9701209, A v2 9701442, B 9701787) failed on whichever file it read first.

Direct read-only check (`W/tau_inspect.py`, job image):

| file | events | Runs genEventSumw | events with some `Jet_genJetIdx ≥ nGenJet` |
|---|---:|---:|---:|
| `e182930b-b855…` | 63075 | 1996814.74 | 7848 (12.4%) |
| `1d4e1a08-9b2c…` | 35243 | 1115793.49 | 4377 (12.4%) |

Both files of this Winter23 sample (`Run3Winter23NanoAOD 126X_mcRun3_2023_forPU65_v1-v2`) carry the defect. Under the current hashed `jerc.py`, **no subset of the sample can be processed**, in TRAIN or in RUN.

Options:

- **(R) Replace the sample (recommended).** Use the Summer23 preBPix `GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` (DAS: 31 files, 1975609 events), or the `…v15-v2` version (30 files, 3363684 events).
  - The generator matches the 2022postEE entry, and this resolves the Winter23/forPU65 flag from 11 Nov.
  - Read-only check of 2 files of v14-v2: **0** events with out-of-range `genJetIdx` (140229 events).
  - Filesets and era YAMLs are **not** hashed inputs (`external_inputs` hashes correction files and `data/{jec,lumimask,muon_ss,electron_ss,lhe_yukawa}`), so the A/B frozen hashes are unchanged.
  - Needed afterwards:
    - change the era-YAML query;
    - fetch the fileset for that one dataset with merge, not truncation;
    - one new-dataset TRAIN submission for each of A and B.
  - Normalisation is self-consistent, because it uses processed sumw.
  - The xsec stays at 2.9766912 pb, the same as the other eras. It has **not** been audited here against the 125.09 GeV convention.
  - Current 2023preBPix MC mixes `realistic_v14` (33 entries) and `v15` (41), so either tag is consistent with existing practice.
- **(X) Exclude the sample.** Leave 2023preBPix ggH→ττ out of TRAIN, RUN and cards, documented. This loses one small background in one era; no other sample is affected.
- **(J) Patch `jerc.py`.** Treat out-of-range `genJetIdx` as unmatched. **Not recommended now**: it changes `selection_signature` and invalidates every A and B TRAIN output, forcing a full reprocess.

**Needs Chirayu:** choose (R) with v14-v2 or v15-v2, or choose (X). Nothing has been dropped, patched or added.

## 6. Still open

- Held `9701317.23`: its marker exists, so removal is optional and needs an OK. Do not release it, because a release reruns completed processing.
- After the retries finish:
  1. rerun `W/census2.py` and `W/diag2.py` (no loop);
  2. run `W/hashcheck2.py` on a sample of new A and B markers;
  3. run full `check_train_outputs.py`, sample/file coverage, and Route B stitching/row checks.

  Markers alone are not production readiness.
- If `b9p29p4279.cern.ch` keeps failing for other users, it could be reported to CERN batch support. This has not been done.
- The original `.sub` files still return sandbox files to the repo root. A generator fix (initialdir) belongs to a quiet period and a separate review.
- Parent: read-only grid monitoring can be re-enabled now that real jobs are in flight (401 jobs).
