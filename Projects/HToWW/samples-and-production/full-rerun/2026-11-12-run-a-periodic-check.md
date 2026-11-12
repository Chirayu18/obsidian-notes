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
