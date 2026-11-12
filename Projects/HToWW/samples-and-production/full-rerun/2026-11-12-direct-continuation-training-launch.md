---
tags: [reference, production, decision]
status: active
date: 2026-11-12
source: laptop
evidence: in-progress
---

# Direct continuation after worker quota limits

Chirayu asked: **“Can you continue working on the tasks the workers were working on? I need everything done in a few hours”**. Parent continues directly, with no new delegate or provider/account fallback. Subsequent explicit instruction: **“Start using this v2 of negrw in production now. Event MVA training start asap , just do all this asap. So that in the next few hours arm A is done and arm B to be completed soon”**.

This resolves the previous hold on adopting negrw v2. It does not supply the missing fit-bin closure evidence. Parent disclosed that neither full production MVA nor RUN had started and that validated limits in a few hours could not be promised. Prior estimate is about1.5h per fold job, before RUN/export/fits and queues; actual production rates remain to be measured.

## Changes completed so far

- Analysis HEAD found `ccdc8f9`, tracked files clean; earlier normalization continuation left no tracked edits. Existing untracked backups/reference files preserved.
- **Two confirmed retry3 failures recovered:** A/B2023preBPix GluGluHto2Wto2L2Nu p2. The KFKI `69a4d512…root` input was replaced in separate retry4 staging with its KIT replica; all15000event run/Jet_pt rows were read successfully before staging. Other LFNs and order unchanged. Isolated stage under `~/htoww_submit_logs/ab_recovery_20261112pm/retry4_sol/`; dry-run assertions passed. Immediate existing queue/EOS guards found no clashes. Submitted **9705943(A)** and **9705944(B)** at15:52:23–24CET, one partition each. Originals and outputs untouched; no deletion/release/removal/credentials changes.
- **Tau normalization alignment:** analysis local commit **b6d52ea**, four era YAMLs only. Inclusive ggH→ττ3.2637552pb, VBF→ττ0.254932pb, W+H→ττ0.0554882176pb, W−H→ττ0.03543141904pb. Source: archived LHCHWG136TeVxsec_extrap r7 at125.09GeV (52.17,4.075,0.88696,0.566359pb) times YR4 BRττ0.06256, source paths in [[2026-11-12-ggtt-summer23-replacement-and-retry3]]. Sample queries are inclusive in associated-W decay. No affected tau dataset had a pending/running job; other same-era dataset entries were asserted unchanged. Atomic writes and verified original copies preserved. Saved diff manifest `retry4_sol/tau12509_changes.json`. Floating representations in YAML may have trailing binary-roundoff digits; these do not change the source precision.
- **negrw v2 adopted:** analysis local commit **71eef55**, only `hww_allfix_4fs.yaml` and `hww_routeb_3fs4fs.yaml` model paths. File SHA256 checked as **af53567ccfeddeef94c1fa62b3a6ed3c1285937919ced3f7705c565b819155cb** before switching. RUN identity guards fromccdc8f9 remain active. No production RUN outputs existed to mix; earlier diagnostic July outputs are not valid v2 production inputs. TRAIN loss remains class-only; negrw model is weight-only and must not change frozen TRAIN feature/selection hashes.

No changes above were pushed. Global125.09alignment of **all** Higgs processes is not established by the tau update. Other rates need their process-specific normalization evidence; no universal rescale is applied.

## Training-readiness validation in progress

Applying [htoww-review skill](/home/cgupta/obsidian-notes/.agents/skills/htoww-review/SKILL.md) and [[Projects/HToWW/framework/2026-11-05-htoww-review-protocol]] for output verification. Existing unchanged b-hive/negrw unit-test logs are trusted, not rerun.

Scratch validator `retry4_sol/validate_mc.py`, logs `validate_A.log`/`validate_B.log`, uses server-side recursive EOS inventories and installed revised partition lists A2729/B2864. It checks per-job mode/year/features/selection and Route B provenance, expected-vs-processed entries, exact input LFNs per partition, duplicate chunks, parquet metadata/row totals, complete MC sample/file coverage and per-era Route B stitch sums/normalization. This is ongoing, not a PASS claim. Initial invocation failed on a scratch-script import path; corrected before validation ran, with no analysis/output change.

Initial completed MC marker reads: **2436A,2570B**, zero marker hash/LFN/entry errors. Snapshot missing MC markers: ApreBPix ggH→WWp2; BpreEE ggH→WWp3 and preBPix ggH→WWp2. These are live jobs, not an approved exclusion. Footer checks are ongoing. Data-only TRAIN retries need not block supervised training: b-hive uses MC only, and the MC normalization path explicitly excludes data; production RUN data coverage remains a separate requirement.

Training will use all complete MC inputs, class weights only, five outer event%5 folds, internal b-hive85/15 validation, recorded20261112seeds and fresh cache-isolated versions. No production training submission is claimed yet in this note. New-model fit-bin negrw closure remains open despite the explicit switch; it requires scored SR outputs downstream and does not block class-only MVA training.

## ttH→ττ discussion supplied during continuation

Chirayu forwarded a discussion with Tahys Janssen, Thomas Van Laer and a quoted reply from Ming-Yan: a genuine inclusive ttHToNonbb already contains ttH→ττ, so separately adding a full-normalized ττ sample can double count that physical channel. Different MC events/lepton kinematics do not make overlapping inclusive/exclusive predictions disjoint; selected contribution must be quantified. This is user-provided discussion, not independently sourced generator verification.

**Important actual-fileset observation:** current era YAMLs use the process label `ttHnonBB` for exclusive `ttHto2C`, `ttHto2G` (query `ttHtoGG`, photons) and `ttHtoZG`, not a DAS sample named inclusive ttHToNonbb. Parent therefore cannot infer ττ coverage from that label. No inclusive/dedicated ttH sample was added or dropped. The exact Run3 fragment/coverage still needs verification. The originally proposed Base/≥1cjet/mll contribution check remains useful, but no such yield result is claimed here.

## Evidence chain (current boundary)

| Prescription | Implementation / check | Observed status |
|---|---|---|
| Continue confirmed failed partitions, preserve LFNs | retry4_sol staged inputs + read test + dry-run + fresh queue/EOS guard | two targeted jobs submitted; output validation pending |
|125.09for tau normalizations | b6d52ea, archived primary rows, per-entry diff/live-dataset guards | implemented; downstream split uses current YAML, old TRAIN xsec metadata remains historical |
|Use negrw v2 now |71eef55, verified model bytes; existing G2 identity guard | configured for both arms; no full RUN result yet |
|No incomplete supervised training | validate_mc.py and MC-only coverage checks | running; training not yet submitted |

