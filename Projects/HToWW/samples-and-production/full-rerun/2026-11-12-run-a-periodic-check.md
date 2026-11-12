---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# Run A TRAIN v2: periodic grid check, 12 November 2026

## Scope and authorization

Chirayu requested: "Keep checking jobs and the subagents every now and then". This scheduled check follows that request. [[Projects/HToWW/samples-and-production/full-rerun/2026-11-11-run-a-train-submission]] records the prior explicit instructions "Then run the A and B routes" and "submit now no questions", the v2 submission and previous missing-job recovery. No job mutation was made in this check. Running Route B, negrw and b-hive delegates were not polled or duplicated.

## Queue snapshot: 00:54:09 CET

Read via existing `ssh -o BatchMode=yes lxplus`, schedd `bigbird28.cern.ch`, owner cgupta. Filter: UserLog contains `hww_allfix_4fs__train/` (excludes the archived v1 path).

| era | running (JobStatus 2) | held (JobStatus 5) |
|---|---:|---:|
| 2022preEE | 25 | 0 |
| 2022postEE | 267 | 1 |
| 2023preBPix | 463 | 0 |
| 2023postBPix | 341 | 0 |

Total: 1,096 running and 1 held. No other queue states appeared for this workflow in this snapshot. These are in-queue counts, not counts of successfully completed jobs. Expected submitted partitions remain 2,727 per the v2 submission record (506 / 1,188 / 640 / 393).

Command: `condor_q -name bigbird28.cern.ch cgupta -af JobStatus UserLog`, aggregated by era; held reason read separately using `-constraint "JobStatus == 5" -af ClusterId ProcId HoldReason`.

### Held job

`9701317.23`, Run A / 2022postEE / DYto2L_2Jets_10to50. Condor reports:

> Transfer output files failure at access point bigbird28 while receiving files from execution point slot1_29@b9p02p4377.cern.ch. Details: writing to file /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/mode_opts.bin: (errno 5) Input/output error

This is the same held job observed at 00:52:58 CET, not a newly identified second held job. No release, removal or resubmission attempted. A bounded `stat` of the destination did not complete within 10 seconds, so storage recovery was not established.

## Recent termination sample

Command: `timeout 15 condor_history -name bigbird28.cern.ch cgupta -limit 400 -af ExitCode UserLog`, filtering the same Run A path. Result: 355 rows with ExitCode 0 and 33 with ExitCode 1 among the returned Run A rows. This is a rolling history sample, not the full v2 census, and does not by itself identify the cause of the 33 failures. ExitCode 0 is not a substitute for input/output coverage validation. Failed partitions have not yet been matched against current in-flight jobs and EOS end markers; no bulk retry was initiated.

## Output-completeness check: inconclusive

Read the live `jobs_status.py` implementation. Its completion criterion is a per-job `.coffea` end marker at `<output>/<era>/<dataset>/<dataset>_<partition>.coffea` (with the documented single-job fallback); parquet shard presence alone is insufficient. `submit.py` writes the marker after processing completes, including zero-selection jobs.

A bounded remote Python check attempted to enumerate EOS via `eos root://eosuser.cern.ch find -f <era-root>` and match markers against every prepared `condor/hww_allfix_4fs__train/<era>/<dataset>/jobnum.txt`. The overall 45-second timeout expired with no summary rows. The check cannot establish whether the stall was Python/environment startup, AFS metadata or EOS enumeration; do not infer zero markers or a completed production from it.

A separate bounded EOS server listing did return entries from `/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train/2022preEE/`, including sample and parquet-partition directories. This establishes only that the path contains outputs, not how many partitions finished or whether they are valid. Reading `jobs_status.py` also eventually succeeded after an initial delay. No real output payload was loaded/validated here.

## Next action and boundary

- Keep the existing periodic job check active while Run A is in flight.
- Once storage is responsive, match expected partitions, EOS `.coffea` end markers and active queue identities; identify missing partitions that are not in flight before any already-authorized retry.
- Inspect the sampled failed jobs' actual logs before classifying them or choosing a site blacklist. Reassess the held output transfer after destination I/O recovers.
- Full `check_train_outputs.py`, sample/file coverage and frozen-hash checks remain prerequisites to production model training. No readiness claim follows from this snapshot.

No immediate decision or credential action is established for Chirayu by this check. No analysis code changes, delegate launches, job submissions/releases/removals, data deletion, credential/service changes or push. Existing unrelated vault changes were preserved. Only this note is committed locally.


## Follow-up: 01:12–01:16 CET

Fresh queue command (same schedd, owner and exact workflow filter) at **01:12:52 CET**: 2022preEE 10 running; 2022postEE 96 running + the same 1 held; 2023preBPix 145 running; 2023postBPix 89 running. Total **340 running, 1 held**. These counts and the marker census below were taken sequentially while jobs continued to finish, so their difference must not be used as an exact failed-job census.

Using `/usr/bin/python3 -S` (avoids user-environment/site startup), a bounded read-only check successfully matched prepared `jobnum.txt` entries against mounted EOS `.coffea` filenames:

| era | expected partitions | end markers present | absent markers |
|---|---:|---:|---:|
| 2022preEE | 506 | 432 | 74 |
| 2022postEE | 1188 | 914 | 274 |
| 2023preBPix | 640 | 493 | 147 |
| 2023postBPix | 393 | 278 | 115 |
| total | 2727 | 2117 | 610 |

Method: for each `condor/hww_allfix_4fs__train/<era>/<dataset>/jobnum.txt`, compare each partition to `<EOS root>/<era>/<dataset>/<dataset>_<n>.coffea`, accepting the single-job fallback exactly as `jobs_status.py` does. Marker filenames were listed through the mount; this is **not** a payload/file-coverage/hash validation, and a complete server-side census remains needed before retry or training decisions. The earlier timeout is superseded only as an operational marker-listing blocker; its historical observation remains above.

Three most recent failed Run A jobs were inspected using filtered `condor_history` (ExitCode != 0, exact v2 UserLog path, limit 3), then the matching `.err` files:

- `9701500.2`: 2023postBPix / GluGluZH_ZtoAll_Hto2Wto2L2Nu. `OSError: XRootD error: [ERROR] Operation expired`, `root://redir.t2.ucsd.edu:1095`, input ending `da2fe407-196c-41ec-9229-febf144843ed.root`.
- `9701499.1`: 2023postBPix / ZH_ZtoAll_Hto2Wto2L2Nu. Same error/site, input ending `d523e19e-a45e-43c0-8f42-db1958e123c7.root`.
- `9701316.110`: 2022postEE / DYto2L_2Jets_50. Same error/site, input ending `f0972ca0-acf7-4dbe-aa03-bace6b834b12.root`.

These three failures are established input-read timeouts, not evidence that all failed jobs share this cause. Source logs are under `condor/logs/hww_allfix_4fs__train/<era>/<dataset>/hww_allfix_4fs__train_<dataset>.<cluster>.<proc>.err` in the canonical analysis repo.

Direct EOS server cross-check (`eos root://eosuser.cern.ch ls <era>/<dataset>`, rc=0 each) found zero `.coffea` markers in each of the two 2023postBPix ZH sample directories, and 15 in the 2022postEE DY-50 directory. Other partitions were still running, so missing markers alone do not authorize blanket retry of either sample.

The held destination `mode_opts.bin` now responds to `stat` (23 bytes). The held job remains JobStatus 5, HoldReasonCode 12 / HoldReasonSubCode 5, Args starts with partition **24** (ProcId is 23; do not confuse these). No release was attempted: successful `stat` alone does not establish successful output transfer or whether the job already wrote its EOS payload. Before recovery, inspect the partition-24 marker and exit/transfer state.

No jobs or analysis inputs were changed in this follow-up. Next: finish matching missing-marker partitions to live `Args` (not ProcId), confirm absent markers directly on EOS, and retry only proven terminal failures within the existing recovery scope. Avoid editing shared filesets/wrappers while A/B jobs are running. All scientific validation and production-training gates remain open.


## Follow-up: 01:33 CET and recovery ownership

Fresh live-queue/marker match at **01:33:07 CET** used the exact workflow UserLog path and the first token of live job `Args` as the partition number. Queue: 2022preEE 3 running; 2022postEE 59 running + the same 1 held; 2023preBPix 74 running; 2023postBPix 36 running. Total 172 running + 1 held.

| era | expected | mounted EOS end markers | absent and in queue | absent and not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 439 | 3 | 64 |
| 2022postEE | 1188 | 949 | 58 | 181 |
| 2023preBPix | 640 | 558 | 74 | 8 |
| 2023postBPix | 393 | 321 | 36 | 36 |
| total | 2727 | 2267 | 171 | 289 |

The census is sequential while jobs finish; jobs with markers may still be in the queue (for example during output transfer). The 289 absent/not-in-queue entries are **recovery candidates**, not 289 proven failures: server-side marker verification and terminal-history/log diagnosis are still required. Several gaps are data samples; do not assume every gap is an XRootD timeout.

A new bounded recovery task was delegated to **Claude Opus 5.5, c1, high effort**, as requested by Chirayu for substantial coding/operational work. It owns diagnosis, direct EOS verification, safe targeted retries and the held-job assessment. It must preserve running-job inputs, avoid shared fileset/wrapper changes, avoid successful-output overwrite, and return after bounded recovery rather than starting a shell polling loop. No new physics choice, full production restart or full model training is authorized by this task.

Recovery thread: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3Ac185fc50-2415-4b0f-b864-f696a60303be%3Adelegate-task%3Aa38661fc-1037-4c46-874b-039333a90f91>.

Until its native result returns, parent periodic checks remain read-only for Run A; do not submit duplicate retries or poll the delegate. Route B, negrw and b-hive retain their separate existing owners.


## Follow-up: 01:53 CET (read-only while recovery agent owns retries)

Snapshot timestamp **01:53:02 CET**. Same bounded `/usr/bin/python3 -S` census and exact workflow filter as the previous entry; live identity is (era, dataset, first Args token). No delegate polling and no job/input changes.

| era | expected | mounted EOS end markers | missing in live queue | missing not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 440 | 2 | 64 |
| 2022postEE | 1188 | 963 | 44 | 181 |
| 2023preBPix | 640 | 577 | 53 | 10 |
| 2023postBPix | 393 | 328 | 27 | 38 |
| total | 2727 | 2308 | 126 | 293 |

Queue counts: **126 running, 1 held**, no other Run A queue states. Held job remains `9701317.23` / DY10–50 partition24 with the same mode_opts.bin AFS output-transfer failure. The queue includes jobs that may already have end markers; counts are sequential, not atomic. No inference that the held job needs processing again.

The 293 absent/not-in-queue partitions remain recovery candidates requiring direct EOS confirmation and failure diagnosis by the existing recovery owner. Parent did not submit duplicate retries, modify inputs or attempt release. End-marker presence is not payload/input-file/hash validation. Run A remains incomplete; full training gates remain open. Periodic checks stay enabled while grid work is pending. No new human decision established by this snapshot.


## Recovery handoff after c1 rate limit: ~02:04 CET

The recovery delegate reached its **five-hour Claude c1 limit**, not a processing failure. Its native terminal notice reports reset at **05:00 Europe/Brussels**, 12 November. No provider/account fallback or replacement delegate was started.

The failure happened **after** successful submission of **296 targeted retry jobs** (46 datasets, clusters9701959–9702005 except9701970, batch `runA_v2_retry_20261112`) and after its vault note was committed as `7a4e1c5`. Read [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-run-a-train-v2-failure-recovery]] for the commands, EOS server verification, terminal-log diagnosis, dry-run checks, staged replica changes and per-job sandbox isolation. Parent read the saved note and native activity through the submission, queue duplicate check and commit; no need to restart or duplicate the completed submission work. Successful recovery of those retries is not yet validated. A parent read-only queue check at **02:05:29 CET** confirmed all 296 retry jobs still in the batch: **151 running, 145 idle**, no held retry jobs.

The held original job9701317.23 **already has** its EOS `.coffea` end marker (worker checked server-side); the failure was incidental sandbox return of mode_opts.bin. Do not release and rerun good processing. Removal is optional and remains unperformed.

One deterministic failure was excluded: 2023preBPix GluGluHto2Tau partition1 includes the known bad genJetIdx file `1d4e1a08-9b2c...`; the earlier file exclusion was undone by a later restore. This sample has no v2 end marker. Recovering it requires a documented sample-content/correction decision before complete TRAIN acceptance; nothing was silently dropped or patched here.

Parent periodic grid monitoring remains enabled and read-only; there is no active Run A recovery delegate to wait on. Substantial new coding still uses c1 Opus after availability returns. No new jobs, account switch, deletion, release, input/config changes or push by parent in this handoff.


## Follow-up: 02:13–02:16 CET (original + retry batch)

At **02:13:06 CET**, exact-workflow queue query included original jobs and batch `runA_v2_retry_20261112`, joined by first Args token. **0 duplicate (era,dataset,partition) keys**. Original: 79 running + the known1 held. Retry batch: **275 running, 0 idle, 0 held** (preEE63, postEE181, preBPix5, postBPix26). Total live running354 +1 held. Snapshot is sequential with the marker census.

| era | expected | mounted EOS end markers | missing in live queue | missing not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 442 | 64 | 0 |
| 2022postEE | 1188 | 977 | 210 | 1 |
| 2023preBPix | 640 | 582 | 40 | 18 |
| 2023postBPix | 393 | 341 | 40 | 12 |
| total | 2727 | 2342 | 354 | 31 |

Missing/not-in-queue entries are candidates, not automatically confirmed failures; no second retry batch was submitted. Held original9701317.23 remains unchanged and already has an EOS marker.

### New retry failure category: proxy visibility, not established expiry

A filtered **10-row rolling retry-history sample** returned ExitCode0 for1 job and ExitCode1 for9. Inspected `9702005.1` (2023preBPix Muon1Run2023Cv1) `.err`: it exits at the initial `voms-proxy-info -all -file /afs/cern.ch/user/c/cgupta/private/x509up_u151861` with **"Couldn't find a valid proxy."** Source:
`R/condor/logs/hww_allfix_4fs__train/2023preBPix/Muon1Run2023Cv1/hww_allfix_4fs__train_Muon1Run2023Cv1.9702005.1.err`.

Parent read-only lxplus check at **02:14:11 CET**: `voms-proxy-info -timeleft -file <same path>` returned **569059 seconds** (~158h), and the600-mode file exists (mtime10Nov16:18). This establishes that the lxplus copy is valid; it does **not** establish worker-node visibility or identify why this retry could not validate it. No proxy renewal is requested on this evidence. The staged retry `.sub` passes the AFS proxy path in arguments; its transfer_input_files contains the partition/jobnum/arguments JSON inputs, not the proxy. This is a diagnosis lead, not a validated cause or authorized credential-delivery change. No modification or repeat retry attempted while other jobs run and c1 is limited.

### One successful retry end marker: provenance checked

`condor_history` filtered to batch and ExitCode0 returned **9701991.1**, Args partition4, 2022preEE/TWminusto4Q. Parent copied its end marker via `xrdcp` from:
`/eos/user/c/cgupta/higgscharm/outputs/hww_allfix_4fs__train/2022preEE/TWminusto4Q/TWminusto4Q_4.coffea`
to lxplus scratch `/tmp/cgupta/cgupta_runA_markercheck_49m0t4q_/TWminusto4Q_4.coffea`.

Executed the saved `~/htoww_submit_logs/runA_v2_retry_20261112/hashcheck.py` inside the established coffea0.7.30 image, read-only for analysis/output. rc0: marker and current tree **match** features `36f655f4724cb1a4…` and selection `80e75bca3f231c49…`. This validates that one retry marker's model-input provenance matches; it does not validate all retry payloads or complete file/row coverage. No repeated unit tests were run.

Next checks: continue observing retry completion; inspect and distinguish worker credential-visibility failures from input-site failures before any further recovery. Run full payload/file/hash gates once inputs are complete. Bad GluGluHto2Tau sample-content decision and incomplete negrw review remain open. Parent changed no jobs, analysis inputs, credentials or services. Monitoring remains enabled while in-flight grid work can progress.


## Follow-up: 02:33 CET (read-only)

At **02:33:09 CET**, combined original/retry query has **225 running, 1 held**, zero duplicate live partition identities. Originals:16 running; retries:209 running; no idle or held retry jobs. Held original9701317.23 remains the same postprocessing transfer hold with a known marker; no release/removal attempted.

| era | expected | mounted EOS end markers | missing in live queue | missing not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 459 | 47 | 0 |
| 2022postEE | 1188 | 1036 | 147 | 5 |
| 2023preBPix | 640 | 594 | 13 | 33 |
| 2023postBPix | 393 | 363 | 18 | 12 |
| total | 2727 | 2452 | 225 | 50 |

Method and mount/payload caveats are unchanged: compare original prepared jobnum.txt lists with end-marker names, join queue by first Args token, and retain full validation gates. Snapshot is sequential while jobs finish.

A subsequent retry-only census of all296 staged retry.txt entries returned **70 markers, 202 missing/in queue, 24 missing/not in queue**. Its queue was taken later than the main snapshot, so running counts are not expected to match. For each absent/not-in-queue retry, matched the newest retry `.err` via the traced `+ JOBID=<partition>` and cluster range9701959–9702005 (excluding9701970). Signatures: **20 worker proxy-check failures**, **3 XRootD Operation expired**, **1 AFS I/O error**. These are log classifications; candidate markers were checked through the mount, not a new full server census. No blanket retry or output-validation claim.

Example logs under `R/condor/logs/hww_allfix_4fs__train/`:
- `2023postBPix/TTto4Q/hww_allfix_4fs__train_TTto4Q.9701996.2.err`: representative proxy-check category, same initial-check issue as the previous entry.
- `2022postEE/DYto2L_2Jets_50/hww_allfix_4fs__train_DYto2L_2Jets_50.9701959.48.err`: representative XRootD timeout category.
- `2022postEE/MuonRun2022F/hww_allfix_4fs__train_MuonRun2022F.9701968.6.err`: inspected separately; `pkg_resources.safe_listdir` fails with `OSError: [Errno 5] Input/output error` reading the shared AFS repo path. This is an environment/filesystem startup failure, not evidence of a new selection defect.

Existing proxy validity on lxplus was established in the02:14 entry; no expiry/renewal claim follows from worker-side failures. Parent did not change delivery, submit more retries, poll delegates or change any analysis/config/output. Existing in-flight jobs still make progress, so periodic monitoring stays enabled. c1 coding/review work remains limited pending its reset; bad GluGluHto2Tau decision and negrw acceptance remain unresolved.


## Follow-up: 02:53 CET (read-only)

At **02:53:21 CET**, combined Run A queue: **56 running +1 held**, zero duplicate live partition identities. Original1 running (2022postEE) + known held9701317.23; retries55 running (preEE17, postEE37, postBPix1), no idle/held retry jobs. No 2023preBPix Run A jobs remain in the live queue, but that era is **not complete**.

| era | expected | mounted EOS end markers | missing in live queue | missing not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 489 | 17 | 0 |
| 2022postEE | 1188 | 1146 | 37 | 5 |
| 2023preBPix | 640 | 604 | 0 | 36 |
| 2023postBPix | 393 | 380 | 1 | 12 |
| total | 2727 | 2619 | 55 | 53 |

Retry-only census of all296 staged entries: **218 markers, 54 missing/in queue, 24 missing/not in queue**. Sequential snapshots can differ from queue counts where a job already has a marker but still returns sandbox files. The24 absent/not-in-queue retries are the same count as the prior census; no evidence of a new failure category was established in this check. Prior log classifications remain20 worker proxy-check failures,3 input read timeouts and1 AFS startup error; do not treat missing-marker counts alone as a fully validated terminal census.

Method unchanged: original jobnum.txt expected partitions, mounted marker listing, first Args token live join, both batch identities. Full payload/file coverage, all-marker hashes and direct-server confirmation of remaining gaps are still pending. No queue disappearance/completeness equivalence is claimed. The known held job already has an EOS marker and was not released. Bad GluGluHto2Tau sample-content decision and incomplete negrw acceptance remain open.

No delegates polled; no jobs, inputs, outputs, credentials, accounts or services changed. No repeat batch or full training launched. Existing jobs still progress; the periodic grid monitor stays enabled.


## Follow-up: 03:13 CET (read-only)

At **03:13:37 CET**, Run A has **3 running retries +1 known original held job**, zero duplicate live identities. The running partitions are one2022preEE and two2022postEE. No idle/held retry jobs. Aggregate read-only query also sees **3 running Route B TRAIN jobs** (`hww_routeb_3fs4fs__train`); parent neither polled its delegate nor altered that work.

| era | expected | mounted EOS end markers | missing in live queue | missing not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 505 | 1 | 0 |
| 2022postEE | 1188 | 1181 | 2 | 5 |
| 2023preBPix | 640 | 604 | 0 | 36 |
| 2023postBPix | 393 | 381 | 0 | 12 |
| total | 2727 | 2671 | 3 | 53 |

All296 staged retries: **269 markers, 3 missing/in queue, 24 missing/not in queue**. Previous log categories for the24 remain recorded above; no new per-log classification or complete server census was run in this check. The53 absent/not-in-queue entries include original failures and the excluded deterministic bad input; they are not resolved by the approaching queue drain. The held job has a marker and stays untouched.

Same first-Args-token identity and end-marker method; mount listing is not full payload/file/hash validation. No job/input/model/credential/service changes, account fallback, replacement delegate, repeat retry batch or production training. Keep the grid schedule enabled while these six A/B jobs can still progress. Remaining coverage/recovery, worker proxy visibility, bad GluGluHto2Tau decision, b-hive pipeline completion/reproducibility and negrw review remain open; no readiness claim.
