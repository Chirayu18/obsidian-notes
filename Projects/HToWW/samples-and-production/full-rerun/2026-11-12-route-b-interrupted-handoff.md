---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# Route B: recovered state after c1 limit, 12 November

Route B's c1 Opus delegate reached the same five-hour account limit at **03:14CET**, native reset notice05:00Europe/Brussels. Parent read the saved implementation/submission note and native activity through positions185–202. No replacement, account fallback, second submission or credential action was started.

Worker record: [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train]]. Original task: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3A0d23aee7-6514-464b-96ac-9899a2819963%3Adelegate-task%3A1ad22fea-f9ee-43af-824d-8a16954e8067>.

## Submission preserved

All four eras were submitted01:10–01:21CET with rc0 per worker logs; expected partitions523/1246/679/414, total **2862**. Logs `~/htoww_submit_logs/routeb_submit_<era>_20261112.log`; outputs `/eos/user/c/cgupta/higgscharm/outputs/hww_routeb_3fs4fs__train/<era>/`. No model training, RUN or Combine is recorded. Do not repeat the initial submission.

The delegate's last pre-limit action was a queue watcher, followed by a failed continuation when that watcher ended. It did **not** return a completed full-coverage check or validated retry result. Early sampled preEE failure logs included input-site FileNotFoundError/[3010] and XRootD timeouts; those samples do not establish the cause of all missing outputs or exclude every code failure.

## Parent read-only census: 03:15:20 CET

Same end-marker criterion as Run A. Expected partitions from `condor/hww_routeb_3fs4fs__train/<era>/<dataset>/jobnum.txt`; marker filenames through mounted EOS; live Condor join by first Args token, exact workflow UserLog path. **2 running**, both2023preBPix; no other live Route B states and zero duplicate live partition keys.

| era | expected | mounted EOS end markers | absent/in queue | absent/not in queue |
|---|---:|---:|---:|---:|
| 2022preEE | 523 | 456 | 0 | 67 |
| 2022postEE | 1246 | 1066 | 0 | 180 |
| 2023preBPix | 679 | 612 | 2 | 65 |
| 2023postBPix | 414 | 377 | 0 | 37 |
| total | 2862 | 2511 | 2 | 349 |

The349 absent/not-in-queue partitions are recovery candidates, not a validated failure census. Verify missing markers directly on EOS and inspect actual terminal/error evidence before any retry. Parent submitted nothing, changed no shared inputs and did not run jobs_status resubmission. Queue drain alone does not establish completeness.

## Remaining boundaries

- Run A recovery method and isolated retry staging are documented separately; do not blindly copy its296-job batch or rewrite shared filesets. Route B identity includes stitching provenance and its own selection hash.
- The worker reports118/118 tests and successful parity/stitching smokes; these remain cited author logs, not a fresh parent correctness review. Preserve checks under the htoww-review protocol before acceptance.
- Worker says Race fix3a03245 is backward compatible and out of its initial file list. It is already committed/tested by that worker; parent has not separately validated it or assumed new approval requirements solely from that narrative. No rollback or cleanup performed.
- Resolve reported Route B PDF/rate, scale-envelope, empty-masked-RUN-path and independent model/split gates before RUN/cards. Its recorded0.0016626 normalization has not been freshly audited here against Chirayu's125.09GeV-everywhere convention; do not claim that convention has been implemented from this note.
- negrw v2 remains unadopted pending interrupted acceptance review. b-hive fold0 test work is recovered separately; no diagnostic model can be promoted to production.

Parent grid monitoring remains read-only and can include Route B now that its delegate is terminal. Substantial coding remains c1 Opus after availability, with no unasked provider/account fallback. No automatic delegate-resumption schedule was created after the earlier approval rejection. Only this handoff note is committed locally; no push.


## Final read-only grid check: 03:33–03:34 CET

Route B has **no jobs left in the live queue**, but remains incomplete: markers456/523(preEE),1066/1246(postEE),613/679(preBPix),377/414(postBPix), **2512/2862 total**. All350 candidate missing markers were confirmed absent directly on the EOS server, with no listing errors. No retries/replacement worker/model training launched. Full rows/file/stitching/hash validation remains pending. Parent periodic grid monitoring was disabled because no A/B compute job can currently progress; see [[Projects/HToWW/samples-and-production/full-rerun/2026-11-12-run-a-periodic-check]] for final evidence and morning decisions. No completeness/readiness claim from queue drain.
