---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# 2023preBPix ggH→ττ Summer23 replacement and A/B retry round 3, 12 Nov 2026 (15:08–15:27 CET)

**Status: agent-reported.** Both routes got the replacement sample (3 TRAIN partitions each) and the 11 failed retries were resubmitted. All 17 jobs were submitted at 15:19–15:23; none had finished when this note was written. The checks named under "Validated" were run. Nothing here is production-ready until the post-completion checks pass.

**Authorization.**
- Chirayu's approval of the replacement with 125.09 GeV normalization and continued A/B recovery: "Yes do all that, I need things done soon" ([[2026-11-12-afternoon-approved-followups]]).
- His request to continue on the Claude 2 account after the Claude 1 quota failures.
- The existing recovery authorization in [[2026-11-12-ab-train-retry-round2]].

Worker: Claude Opus 5.5 on Claude 2, the sole owner of samples, coverage and recovery; no subagents.

Paths:
- `R = lxplus:~/higgscharm_thomas/higgscharm_thomas_new/higgscharm`
- `W = lxplus:~/htoww_submit_logs/ab_recovery_20261112pm`
- `G = W/ggtt_replace`, `R3 = W/retry3`

Every script, TSV and log named below is in these directories.

## 0. State inherited from the failed Claude 1 worker

The rate-limited Claude 1 worker `d9470788` left only one file: `lxplus932:/tmp/cgupta_ggtt_v14v2_files.txt` (13:59), a list of 31 LFNs. It is identical to the DAS list I fetched again (`G/das_files.tsv`).

No changes were found after 13:35 in any of:
- `R/analysis/filesets`;
- `R/condor/*/2023preBPix/GluGluHto2Tau`;
- `W`.

`R` HEAD was `0bd528c` at the start of this work.

Queue at 15:13: only B MuonRun2022F p2 and p5 (`9704382.1`, `.3`) were running. EGammaRun2022D p5 (`9704395.4`) had left the queue, and its marker appeared in the census below. Also in the queue:
- the held A job `9701317.23`;
- the unrelated held b-hive job `9701591.0`.

**Proxy:** 522296 s left at 15:13. It was not renewed.

## 1. Normalization: 125.09 GeV, from primary sources

The sample is *generated* at M = 125 GeV (`GluGluHto2Tau_M-125`). Only the *normalization* uses mH = 125.09 GeV.

Sources were fetched on lxplus with the existing Kerberos SSO and archived in `G/sources/`:

| quantity | value at 125.09 | value at 125.00 | source |
|---|---|---|---|
| σ(ggF), 13.6 TeV, N3LO QCD + NLO EW | **52.17 pb** | 52.23 pb | LHCHWG twiki `LHCPhysics/LHCHWG136TeVxsec_extrap`, r7 (2026-03-06); extrapolation of YR4, documented in arXiv:2402.09955 |
| BR(H→ττ) | **6.256E-02** | 6.272E-02 | LHCHWG twiki `LHCPhysics/CERNYellowReportPageBR` (YR4), r23 (2023-12-21) |

Applied value: xsec = 52.17 × 0.06256 = **3.2637552 pb**.

Archived pages (sha256 prefixes):
- `LHCHWG136TeVxsec_extrap.html`: `883d4752e0701a9a`
- `CERNYellowReportPageBR.html`: `befc8eab8a4e0a3d`

**The previous 2.9766912 pb was not a 125.09 value.**
- It factors exactly as 47.46 pb × 0.06272.
- 0.06272 is the YR4 BR at **125.00**.
- 47.46 pb matches no ggF entry on the 13.6 TeV twiki. Its origin is unknown.
- The new value is 9.64% higher.

**Other eras are not changed and are now inconsistent.** 2022preEE, 2022postEE and 2023postBPix GluGluHto2Tau still have 2.9766912:
- 2022preEE and 2023postBPix use the powheg `GluGluHToTauTau` samples;
- 2022postEE uses the same amcatnloFXFX generator as the replacement.

I did not edit them:
- B jobs reading the 2022 YAMLs at runtime were live;
- the approval covered the replacement.

`scripts/mva/split_folds.py:155` takes xsec from the era YAML (`get_dataset_config`) when it splits, so aligning the other eras later needs **no reprocessing**. The TRAIN parquet `xsec` metadata of those eras would still read 2.9766912.

Side observation: VBFHToTauTau carries 0.255872512 = 4.0796 × 0.06272. The twiki gives VBF 4.075 pb at 125.09. Not audited further.

## 2. Replacement sample checks (read-only)

New sample: `/GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM`. DAS: VALID, 31 files, 1975609 events (`G/das_files.json`).

**Replicas** (rucio, `G/replicas.py` → `G/replicas.tsv`):
- Every file has 6 non-tape replicas.
- The EU redirector answers `[3010] Unable to locate … permission denied` for this dataset. The global redirector finds it.
- Chosen replicas:
  - 30 files at T2_US_MIT;
  - `b56bce2b…` at T2_UK_London_IC, because MIT returned `[3012] Too many DFS read attempts` and Nebraska gave a TLS error. PIC and Estonia also read it fully.
- No UCSD, UFL, KFKI, NCHC or KIPT URLs are used.
- Final list: `G/final_urls.tsv`.

**Full-read defect scan** of all 31 chosen URLs in the job image (`G/scan.py`; results in `G/scan.tsv` and `G/scan_alt.tsv`):
- 1975609 entries, equal to DAS;
- Runs genEventSumw total 233574802.571;
- **0 events** with `Jet_genJetIdx >= nGenJet`;
- **0 events** with `FatJet_genJetAK8Idx >= nGenJetAK8`.

For comparison, the Winter23 files had 12.4% defective events (retry-round2 §5).

## 3. Shared-file changes (fresh guard immediately before)

`G/apply_fileset.py`, 15:17:17. Guards:
- 0 live jobs of any workflow for `2023preBPix/GluGluHto2Tau`, and 0 for 2023preBPix at all;
- the A and B output directories exist and are empty on the EOS server.

Backups, `cp -p`, sha256-verified:
- `R/analysis/filesets/2023preBPix_nanov12.yaml.bak-20261112-ggtt-winter23`
- `R/analysis/filesets/fileset_2023preBPix_nanov12_lxplus.json.bak-20261112-ggtt-winter23`

The originals are kept. Each file was replaced atomically (`os.replace`).

Changes:
- **Era YAML:** only two lines of the `GluGluHto2Tau` entry changed, `query` and `xsec`. Every other entry was asserted equal. `process: ggH` and `key: gghto2tau` are unchanged. sha256 `452325c4…` → `da5c2a5f…`. Committed alone as `R` **`045af4a`**, with `git commit -- <path>`.
- **Fileset JSON:** only the `GluGluHto2Tau` key was replaced, 2 Winter23 URLs → 31 URLs. Key order and the other 95 keys were asserted identical, with no truncation. sha256 `9dc2fdc7…` → `140aea6f…`. The file is untracked by git.
- **Hashes:** filesets and era YAMLs are not hashed inputs. The smokes below confirm the frozen hashes are unchanged.

`make_filesets.py` was **not** run: it overwrites the whole JSON with only the requested samples, which caused the earlier `.bak-20261111-truncated` files.

## 4. Smokes (single file, job image, node-local outputs)

`G/smoke.sh` ran `submit.py --mode train --folds 5` from `R` on `b56bce2b`, with output under `lxplus932:/tmp/cgupta_ggtt_smoke/`.

The first attempt failed because I had not bound `/eos` into apptainer, so the 2023 ctag2d correction JSON on `/eos/cms` was missing. That was my environment, not the sample; Condor nodes mount `/eos`. The rerun with `-B /eos` exited 0 for both routes.

| check (`W/hashcheck2.py`, `G/smoke_check.py`) | A `hww_allfix_4fs` | B `hww_routeb_3fs4fs` |
|---|---|---|
| features / selection hash | `36f655f4724cb1a4` / `80e75bca3f231c49`: **match** | `36f655f4724cb1a4` / `24b63ba31bf672de`: **match** |
| routeb_stitching sha256 | none (expected) | equals the frozen `__init__ b77acc70…`, `hplusc_routeb 5b4e256b…`, `routeb_io eb9bb587…` |
| execution_checks | 14965 / 14965 entries | 14965 / 14965 |
| parquet metadata | xsec `3.2637552`, sample `GluGluHto2Tau`, year 2023preBPix, mode train | same |
| rows | 6 (base), process `ggH` | 6 (base), process `ggH` |

## 5. Replacement TRAIN submission

`G/build_replace.py`, 15:19. It partitions exactly as `submit_condor.py`: the repo's own `divide_list`, executed from source, with `nfiles` 15 from `arguments.json`. Result: **3 partitions of 11, 10 and 10 files**, keys `GluGluHto2Tau_1..3`. The LFN order equals DAS order.

**Old records archived, not deleted.** `partitions.json`, `jobnum.txt`, `arguments.json` and the `.sub` were copied (sha256-verified) to `G/archive_winter23/<wf>/`. The old logs stay in `R/condor/logs/<wf>/2023preBPix/GluGluHto2Tau/`.

**Expected manifest installed.** New `partitions.json` (sha256 `b9a88508f2791fca`) and `jobnum.txt` (`1 2 3`) are in `R/condor/<wf>/2023preBPix/GluGluHto2Tau/`. `arguments.json` and the `.sub` there are unchanged.

Per-file manifest: `G/manifest_A.tsv`, `G/manifest_B.tsv`, columns wf, era, ds, partition, key, LFN, URL.

**Submission is from immutable staged copies.** `G/stage_{A,B}/2023preBPix/GluGluHto2Tau/replace.sub` transfers the staged `partitions.json`, `replace.txt` and `arguments.json`. Like retry2, it sets:
- a per-job `initialdir p<n>/`;
- `requirements = (Machine =!= "b9p29p4279.cern.ch")`.

**Dry run** (`G/check_dryrun_replace.py`) passed for both routes:
- Args first token = 1, 2, 3;
- Iwd per job;
- the staged TransferInput;
- the bad-node exclusion;
- staged LFNs equal the DAS list;
- no bad-site hosts.

**Submission:** `G/submit_replace.py` is `submit_retry2.py` with the file names changed. It took a fresh `condor_q` and an EOS-server marker check just before each submit: 0 clashes.

| batch | route | cluster | partitions |
|---|---|---|---|
| `runA_v2_ggtt_summer23_20261112pm` | A | **9705541** (.0–.2) | 1, 2, 3 |
| `routeb_train_ggtt_summer23_20261112pm` | B | **9705543** (.0–.2) | 1, 2, 3 |

The previously staged exclusion of the Winter23 p1 is superseded: it is a replacement, not a retry. The old Winter23 partition is no longer in the expected manifest.

## 6. New expected-partition manifest

These numbers supersede A 2727 / B 2862 in [[2026-11-12-ab-train-retry-round2]] and [[2026-11-12-ab-grid-check-1359]].

| era | A expected | B expected |
|---|---:|---:|
| 2022preEE | 506 | 523 |
| 2022postEE | 1188 | 1246 |
| 2023preBPix | **642** (was 640) | **681** (was 679) |
| 2023postBPix | 393 | 414 |
| **total** | **2729** | **2864** |

The change is −1 Winter23 partition + 3 Summer23 partitions in each route. Monitors must read `jobnum.txt`, which now contains `1 2 3` for this dataset.

## 7. Retry round 3: the 11 failed retries

**Census at 15:18:25** (`R3/`, `census2.py`, joined on the first Args token): A 2722/2727 markers, B 2852/2862, with 2 live in B.
- The non-live gaps were exactly the 11 recorded failures plus the Winter23 p1 in each route.
- 0 listing errors and 0 duplicate live keys.

`diag2.py` on the newest traced `.err` gave 9 `Operation expired` and 2 NCHC `[FATAL] Connection error`. This matches the monitor log, with no proxy or AFS signatures.

**URL checks** (`R3/collect3.py`):
- The 161 URLs of the 11 retry2-staged partitions were stat-probed with the full PFN path (`R3/statone.sh`). 104 of 105 unique URLs were OK.
- The extra failure was B 2022preEE GluGluHto2Wto2L2Nu `10079c75…` at the EU redirector, in a non-failing file.
- Alternate replicas from rucio (`R3/alt3.py`) for the 8 affected LFNs excluded tape, UCSD, UFL, KFKI, NCHC, KIPT and every host that had already failed for that LFN.
- All 31 candidates passed a real read test in the job image (`R3/readtest.py`: `Events` run + Jet_pt read in full).
- The highest-preference OK replica was chosen:

| LFN (basename) | used by | new replica |
|---|---|---|
| `0584d50d` Muon 2022F | A + B postEE p1 | T2_CH_CERN (eoscms) |
| `c4ef779e` Muon 2022F | A + B postEE p22 | T2_CH_CERN |
| `e35d879f` DY50 2023 | A + B preBPix p17 | T2_CH_CERN |
| `991f48f9` ggH→WW 2023 | A + B preBPix p2 | T1_DE_KIT_Disk |
| `ee6fb2ce` DY50 2022 | B preEE p16 | T2_CH_CERN |
| `21d498af` ggH→WW 2022 | B preEE p3 | T1_IT_CNAF_Disk. This **supersedes** its retry2 global-redirector override, which is the route that failed. |
| `10079c75` ggH→WW 2022 | B preEE p3 (non-failing file) | T1_US_FNAL_Disk |
| `07c69347` WG PTG200to400 | B postEE p5 | T2_US_MIT |

**Staging.** `W/build_retry2.py`, unchanged, wrote `R3/stage_{A3,B3}`, using `R3/override3.tsv`: the 4 kept retry2 overrides plus the 8 new picks. It made no exclusions.

Checked against the retry2 staging:
- 11 partitions and 161 URLs;
- LFN order identical;
- exactly **12 URLs differ**, all of them the read-tested picks.

`check_dryrun2.py` passed for all 9 dataset directories.

**Submission:** `submit_retry2.py` with a fresh queue and EOS guard at 15:23:04/05. 0 clashes.

| batch | route | clusters (partitions) |
|---|---|---|
| `runA_v2_retry3_20261112pm` | A (4 jobs) | 9705579 (postEE Muon p1, p22), 9705580 (preBPix DY50 p17), 9705581 (preBPix ggH→WW p2) |
| `routeb_train_retry3_20261112pm` | B (7 jobs) | 9705582 (postEE Muon p1, p22), 9705583 (postEE WG p5), 9705584 (preEE DY50 p16), 9705585 (preEE ggH→WW p3), 9705586 (preBPix DY50 p17), 9705587 (preBPix ggH→WW p2) |

No duplicates of the 401 retry2 jobs: the retry2 jobs still live are only B Muon p2 and p5, which are other partitions.

**Queue after submission:** 20 live A/B keys and 0 duplicates.

**Census on the new manifest:**

| route | expected | markers | live | not live |
|---|---:|---:|---:|---:|
| A | 2729 | 2722 | 7 | **0** |
| B | 2864 | 2852 | 12 | **0** |

If all 17 replacement and retry3 jobs and the 2 B retry2 jobs succeed, coverage is complete: A 2729/2729, B 2864/2864.

## 8. Validated by checks vs agent-reported

**Validated by checks run here:**
- DAS counts.
- Full-read defect scan of all 31 files.
- The YAML and JSON diff assertions.
- Smoke hashes and metadata in both routes.
- Dry-run assertions.
- 0 submit clashes and 0 duplicate live keys.
- **Frozen hashes on 8 already-finished retry2 markers** (`W/hashcheck2.py` after `xrdcp` to `/tmp/cgupta_hash3.*`): 3 A, all `36f655f4/80e75bca`; 5 B, all `36f655f4/24b63ba3` with the frozen routeb_stitching sha256, including `HplusCharm_3FS_HToWW_ext1_1` (2022postEE) and DY50 / MuonRun2022F markers. All **match**.

**Agent-reported or pending:**
- The 17 new jobs and 2 B retry2 jobs have not finished.
- A replica read test does not guarantee that a job's full read succeeds.
- Not yet run, because coverage is incomplete:
  - full `check_train_outputs.py`;
  - sample and file coverage;
  - Route B stitching and row checks;
  - hash checks on the new replacement and retry3 markers.

## 9. Blockers and needs Chirayu

1. **Decide whether to align the other eras' GluGluHto2Tau xsec** to 125.09. The values would be 3.2637552 pb if their samples are treated like this one. Today 2023preBPix is 9.6% above the other three eras. This is a YAML-only change, picked up by `split_folds.py`. It is safe once no jobs for those eras are live.
2. **A file I did not change.** Since 15:17:57, `R/analysis/processors/base.py` has an uncommitted edit by the negrw worker. It adds the RUN-only `negrw_model_sha256` provenance. Grid jobs import `base.py` from `R` when they run, so the new jobs run with it. The TRAIN path is unchanged, and my smokes, run after that edit, matched the frozen TRAIN hashes. Two other things changed during this session, also not mine: `R` HEAD moved to `8535275` (b-hive registration), and there are uncommitted negrw/combine script edits. None were touched.
3. **Held job `9701317.23`** still has its marker. It was not released or removed.
4. **Infrastructure observations:**
   - The EU redirector cannot locate the Summer23 ggH→ττ dataset.
   - The MIT replica of `b56bce2b` gave `[3012] Too many DFS read attempts`.
   - Node `b9p29p4279.cern.ch` stays excluded.

   None was reported to site or batch support.

**Not done:**
- no deletion, release, removal or proxy renewal;
- no service actions;
- no full model training, RUN or Combine production;
- no negrw, RUN, mva or b-hive edits;
- no Meta, README or deck edits;
- no push.
