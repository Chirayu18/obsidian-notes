---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# Run A TRAIN v2: diagnosis and retry of failed partitions (12 Nov 2026, 01:35–02:03 CET)

**Status: agent-reported.** 296 failed partitions were resubmitted; none has finished yet, so no recovery is validated. Scope is recovery of the already-authorized Run A production only ([[Projects/HToWW/samples-and-production/full-rerun/2026-11-11-run-a-train-submission]]: "Then run the A and B routes", "submit now no questions"; periodic checks: [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-run-a-periodic-check]]).

What was **not** changed:
- analysis code, selection, corrections or hash inputs;
- the shared filesets, original `jobnum.txt` / `partitions.json` / `.sub` files, or the wrapper `condor/submit.sh`;
- any EOS output (nothing deleted or overwritten);
- the Condor queue: no release and no removal;
- Route B, negrw and b-hive jobs or delegates; credentials; and nothing was pushed.

Paths: repo `R = lxplus:~/higgscharm_thomas/higgscharm_thomas_new/higgscharm` (branch `hww-analysis`). The work dir `W = lxplus:~/htoww_submit_logs/runA_v2_retry_20261112/` holds every script, input list and log named below.

## Census (immediately before submission, 02:00:18 CET)

Expected partitions come from `R/condor/hww_allfix_4fs__train/<era>/<ds>/jobnum.txt`. A partition is complete when its end marker `<ds>_<n>.coffea` (or the single-job `<ds>.coffea`) exists, the same rule as `jobs_status.py`. The live queue is joined on era, dataset and the **first Args token** (ProcId is not the partition). The Run A filter is UserLog containing `hww_allfix_4fs__train/`, which excludes v1.

| era | expected | marker | in queue | absent, not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 506 | 440 | 2 | 64 |
| 2022postEE | 1188 | 966 | 41 (incl. 1 held) | 181 |
| 2023preBPix | 640 | 580 | 46 | 14 |
| 2023postBPix | 393 | 333 | 22 | 38 |
| total | 2727 | 2319 | 111 | 297 |

- Scripts: `W/census.py` (stdlib, `/usr/bin/python3 -S`; mounted listing first), then `W/eos_verify.py`, which runs `eos root://eosuser.cern.ch ls` for each of the 47 sample dirs. All 297 absent markers were **confirmed on the server**: 0 present, 0 listing errors. The 01:40 pass gave 290 confirmed.
- `condor_history` (`W/hist_013600.txt`) timed out at 120 s with 2555 rows, back to cluster 9701246. A second query for clusters 9701215–9701246 also timed out (150 s, 0 rows), because history is scanned backward over the whole file. Terminal status therefore rests on "no marker on the server and not in the live queue" plus each partition's own v2 `.err` file, not on history alone. Within the history that was returned, every absent partition had ExitCode 1 and none had ExitCode 0, so there were no marker or layout mismatches.

## Diagnosis (`W/diag.py` → `W/diag_020018.tsv`)

Every candidate was mapped to its newest v2 `.err` file (cluster ≥ 9701215) through the bash trace line `+ JOBID=<n>`. All 297 had one. Signatures:

| count | signature | last XRootD host | class |
|---:|---|---|---|
| 192 MC + 5 data | `OSError: XRootD error: [ERROR] Operation expired` | `redir.t2.ucsd.edu:1095` (194), `grid143.kfki.hu` (2), `cmsdcadisk.fnal.gov` (1) | input-site read timeout |
| 97 data | `FileNotFoundError ... [3010] Unable to open ... permission denied` | `cmsio3.rc.ufl.edu:1094` | file-specific UFL failure |
| 1 | `OSError: expected Chunk of length 403` (2023preBPix GluGluHto2Wto2L2Nu p2) | `cmsio3.rc.ufl.edu` | corrupt read from UFL |
| 1 | staging race: `FileNotFoundError` on `R/4f69cab6-..._%2FEvents%3B1_0-85162.parquet` in `parquet_writer.py:139` (2022postEE GluGluHto2Wto2L2Nu p1) | eoscms | the shared-AFS-cwd race fixed by `3a03245` |
| **1** | `ValueError: in ListArray64 attempting to get 5, index out of range` at `jerc.py:377` (**2023preBPix GluGluHto2Tau p1**) | xrootd-cms.infn.it | **deterministic bad input file; excluded** |

Per-host outcomes over all v2 partitions (`W/hoststats.py`, partitions containing that host, done vs failed):

| host | done | failed | failed fraction |
|---|---:|---:|---:|
| `redir.t2.ucsd.edu` | 25 | 192 | **0.88** |
| `skynet013.crc.nd.edu` | 381 | 196 | 0.34 |
| `cmsio3.rc.ufl.edu` | 599 | 109 | 0.15 |
| most other hosts | | | 0.02–0.25 |

A failed partition contains files from several hosts, so it is counted under each one. The `.err` files attribute the failures to UCSD and UFL.

Direct probes (proxy `~/private/x509up_u151861`, 570997 s left at 01:4x, about 158 h):
- UFL file `.../Run2022E/EGamma/.../02572330-...root`: `xrdfs stat` rc 54 at `cmsio3`, but stat and a 1 MB read succeed through `xrootd-cms.infn.it` and `cms-xrd-global.cern.ch`.
- UCSD file `.../DYto2L-2Jets_MLL-50.../0079a015-...root`: stat and a 1 MB read **succeed** at UCSD right now, and through `xrootd-cms.infn.it`. Through the global redirector the stat succeeds but the read returned 0 bytes in 60 s.
- Conclusion: UCSD is unreliable under job load (88% of its partitions failed) rather than down, and UFL refuses specific files. A plain resubmit with the same URLs would mostly fail again.

### Held job 9701317.23 (2022postEE DYto2L_2Jets_10to50, Args partition **24**)

- The end marker `DYto2L_2Jets_10to50_24.coffea` **exists on the EOS server** (2477 B, 00:33).
- The job started at 00:19:42 and its `.out` and `.err` came back at 00:33. The user log shows `004 Job was evicted. Code 12 Subcode 5`, then `012 Job was held` at 00:33:31.
- So processing and the EOS write finished. Only the return of the incidental `mode_opts.bin` to `R/` failed (AFS errno 5).
- **Not released**, because a release reruns the partition and rewrites good output.
- Recommendation, needing Chirayu's OK for `condor_rm`: remove 9701317.23. The partition already counts as done by marker.
- Payload (parquet rows) not validated here; `check_train_rows` covers it later.

### Why `mode_opts.bin` lands in the repo root

- The v2 `.sub` files have no `initialdir`. `submit.sh` writes `mode_opts.bin` and `partition_fileset.json` into the scratch dir, and Condor returns new scratch files to the submit directory, which is `R/`.
- Every Run A job therefore writes the same two filenames into the shared repo root. That contention produced the errno-5 hold.
- `R/mode_opts.bin` (23 B, `--mode train --folds 5`) and 184 untracked `R/*.parquet.*.tmp` staging leftovers were left untouched.

## Hash consistency check before retry

Jobs run the live tree (`cd $BASEDIR`), and HEAD moved after the v2 submission (`eaab247`, `7b4b930`, `3a03245`, `0995853`). Diff `f84d311..HEAD` touches no `selection_signature` input (`corrections/`, `selections/`, `working_points/`, `leptonmva/`, `features/hww.py`, selection data dirs).

Direct check (`W/hashcheck.py` in the job image `coffea-base-almalinux9:0.7.30-py3.10`, markers copied to `/tmp` with `xrdcp` because the container cannot read `/eos/user`): the current tree gives features `36f655f4724cb1a4…` and selection `80e75bca3f231c49…`. These **match** the provenance in markers written at 00:13, 00:14, 00:48, 01:44 and 01:45 (TWminusto4Q_2, TWminusto2L2Nu_2, WtoLNu_2Jets_1J_59, TTto4Q_19, EGamma0Run2023Dv1_9).

## Retry method (retry-only staging; originals untouched)

`W/build_retry.py` writes `W/stage_020018/<era>/<ds>/` containing:
- `partitions.json`: **only the retry partition keys**, with the same LFNs in the same order (so the same chunks, entry ranges and fileuuids). The only change is a URL rewrite for the two proven-bad hosts: `root://(redir.t2.ucsd.edu|cmsio3.rc.ufl.edu)(:port)//store/…` → `root://xrootd-cms.infn.it//store/…`. Each rewrite is asserted LFN-identical. Count: 733 of 4264 file entries (720 in the 01:40 test staging).
- `retry.txt`: the partitions to queue.
- `retry.sub`: the original `.sub` with three differences: the staged `partitions.json` in `transfer_input_files`; `Queue JOBNUM from retry.txt`; and `initialdir = <stage>/<ds>/p$(JOBNUM)` (one per-job directory, pre-created), so the returned `mode_opts.bin` and `partition_fileset.json` no longer go to `R/`. Everything else is unchanged: `executable = R/condor/submit.sh`, the same `arguments`, `arguments.json`, `jobnum.txt`, image, memory 2000, `request_cpus 2`, `workday`, proxy, and the original log/out/err paths, which carry new cluster IDs so nothing is overwritten.

Why the replica rewrite is safe:
- TRAIN chunk identity is coffea's `_partition_key` (fileuuid, tree, entry range).
- File coverage uses `store_path()`, the `/store/` LFN (`analysis/processing_checks.py:42`).
- Parquet shard names are uuid-based.
- So a different replica of the same LFN leaves the bookkeeping identical. This mirrors the established `jobs_status.py` blacklist regeneration, but without touching the shared fileset.

Checks of the retry inputs:
- **Condor:** `condor_submit -help` (25.0.14) says `-queue` needs a submit file without a Queue statement, which ours have, so standalone retry `.sub` copies were used instead. `condor_submit -dry-run` on all 46 staged files gave 296 procs. Each proc's `Args` partition matches `retry.txt`, `Iwd = …/p<partition>`, and `TransferInput` starts with the staged `partitions.json` (checker `W/check_dryrun.py`).
- **Replicas:** `xrdfs xrootd-cms.infn.it stat` on all 720 rewritten URLs from the 01:40 staging gave 606 OK and 114 fail at 24-way parallelism. Re-probing the 114 at 6-way gave 109 OK via EU, 4 OK only via global, and 1 OK only at the original UCSD host. The original UCSD/UFL hosts failed again on 29 of them.
- **Reads:** a 1 MB read via EU succeeded on 7 of 8 random rewritten files. One returned 0 bytes in 60 s (`6e0d1a1d-…`).
- **Residual risk:** about 5 URLs and the 13 URLs rewritten after 01:40 were not individually re-proven. A small number of retries may fail again on input access.

## Submission (02:02:07–02:02:42 CET)

`W/allow.py` lets through only diagnosed signatures: Operation expired, `[3010]`, `expected Chunk of length`, and the parquet staging race with no ListArray error. Result: 296 allowed. Excluded by signature and by `W/exclude.tsv`: 2023preBPix GluGluHto2Tau p1.

`W/submit_retry.py W/stage_020018 W/submit_020018.log` takes a fresh `condor_q` (106 live Run A jobs at 02:02:08) and runs `eos ls` per dataset immediately before each `condor_submit -name bigbird28.cern.ch -batch-name runA_v2_retry_20261112 <retry.sub>`. Any partition that was in the queue or had a marker would have skipped its dataset; there were 0 clashes.

- **46 datasets, 296 jobs, clusters 9701959–9702005** (9701970 is not ours), batch name `runA_v2_retry_20261112`. Per-cluster mapping: `W/submit_020018.log`.
- Breakdown: 2022preEE 64, 2022postEE 181, 2023preBPix 13, 2023postBPix 38.
- Queue at 02:02:49: retry 279 idle + 17 running; original 105 running + 1 held (9701317.23); **0 duplicate (era, dataset, partition) keys**.

## Not recovered: decisions or OKs for Chirayu

1. **2023preBPix GluGluHto2Tau, the only partition (p1)**:
   - The partition holds `e182930b-b855…` and the bad `1d4e1a08-9b2c…`, so the sample has **0** v2 TRAIN outputs.
   - The live `fileset_2023preBPix_nanov12_lxplus.json` contains `1d4e1a08` again. The 11 Nov removal (`.bak-20261111-ggHtautau`) was undone by the later fileset restore.
   - Options, none taken:
     - (a) a retry-only partition with just `e182930b`, as on 11 Nov. This is a sample-content change; normalisation uses processed sumw, so the sample is halved.
     - (b) leave the sample out of TRAIN.
     - (c) patch `jerc.py`. That changes `selection_signature` and invalidates all TRAIN outputs, so it is not recommended.
   - The sample is also the Winter23/forPU65 sample flagged on 11 Nov.
2. **Held 9701317.23**: removal needs an OK (see above). It is harmless while held.
3. **Shared-repo sandbox returns**: the original `.sub` files still return files to `R/`. Any future retries should reuse the `initialdir` staging above. Changing `submit_condor.py` waits until A/B jobs are idle.

## Next (parent / periodic check)

- Do not poll in a loop. On the next periodic check, run `W/census.py` → `W/eos_verify.py` → `W/diag.py` again; history is optional.
- For retry clusters 9701959–9702005: confirm markers appear, and check any new `.err` files for EU-redirector read failures before deciding on a second round.
- Spot-check that the provenance of a retry marker matches `36f655f4…` / `80e75bca…`.
- Check that no retry job is held on output transfer.
- Then run full `check_train_outputs.py` (row coverage), sample/file coverage and frozen-hash gates before any training. No readiness claim follows from this note.
