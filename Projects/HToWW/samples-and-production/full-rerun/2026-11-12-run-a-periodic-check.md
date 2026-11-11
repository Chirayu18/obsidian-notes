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
