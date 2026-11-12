---
tags: [reference, production]
status: active
date: 2026-11-12
source: laptop
evidence: agent-reported
---

# b-hive pipeline test: recovered state after c1 limit

The c1 Opus test agent failed at its five-hour limit on12November03:07CET (native notice: reset05:00Europe/Brussels). Parent recovered its saved note, activity positions215–232 and the real grid job/log state. No account/provider fallback, replacement task, extra training or job release/removal was performed.

Source worker note: [[Projects/HToWW/framework/2026-11-12-bhive-training-pipeline-test]]. It remains an in-progress TEST on a stale TRAINv1 subset, not production model training and not permission to use diagnostic models for production.

Failed delegate: <t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/thread:delegated-task:command%3Amcp%3A0d23aee7-6514-464b-96ac-9899a2819963%3Adelegate-task%3A40bd6f6d-c3f8-4599-a0a4-af35a59c2abb>.

## Recovered evidence

| item | observed evidence | boundary |
|---|---|---|
| ONNX export unit tests | Child activity217 records `TestOnnxExport`2/2OK in11.807s, rc0 | Author-run log read by parent, not re-executed; unchanged code tests should not be repeated |
| Real v11 export | Earlier child activity185 reports agreement with PyTorch around3e-7, old checkpoint unchanged | Agent-reported; saved exact outputs must be located before claiming independent validation |
| Fold0 job9701591 | Parent read live queue and `~/bhive_test_20261112/fold0.9701591.{err,out}` via existing ssh at **03:07:53CET** | Queue JobStatus5, remote wallclock454s, not an active ongoing training job |
| Fold0 processing block | stdout: `fold0 rc=0 end 2026-11-12T01:12:54+01:00`; stderr's final Luigi summary shows InferenceTask ran successfully with DatasetConstructorTask/TrainingTask dependencies complete | Worker-run test block completed; parent read saved logs. Model/export/row artifacts still need checking |
| Cache guard | stdout: `rerun rc=1 (expect1): refusing: .../DatasetConstructorTask/HPlusCHToWW_2dcats/test_20261112_05d7e0f8_f0_train exists (stale fold data)` | Expected refusal observed; do not delete constructed datasets or bypass the guard to repeat the run |
| Condor hold | `Transfer output files failure ... reading ... /pool/condor/dir_12817/fold0.sh: (errno2) No such file or directory` | Sandbox-return problem; it is not evidence the training block failed. No release/removal attempted, to avoid duplicating successful test work |

Exact parent command: `ssh -o BatchMode=yes lxplus 'date; condor_q -name bigbird28.cern.ch 9701591 -af JobStatus RemoteWallClockTime HoldReason; tail -n22 ~/bhive_test_20261112/fold0.9701591.err; tail -n10 ~/bhive_test_20261112/fold0.9701591.out'`.

## Resume boundary

- Preserve existing test outputs and checkpoints. First inspect the fold0 model, held-out inference outputs and `train_val_split.json`; do not reconstruct/retrain blindly or infer GPU work is still running from the stopped wait task.
- Complete fold0 export/PyTorch parity, diagnostic registration and the intended one-file RUN smoke/independent template comparison. These stages are **not established complete** by this handoff.
- Review the worker's uncommitted edits in b-hive and analysis scripts; preserve other agents' changes. Diagnostic-only hash exceptions must remain blocked for submitted production.
- The worker note explicitly says only the validation shuffle was seeded; torch initialization and epoch ordering were still unseeded. Chirayu's requested reproducibility is therefore **not yet established** by that change. Resolve and test the actual scope before production training; this handoff authorizes no silent recipe change.
- Full production requires complete/validated TRAINv2, current hashes, appropriate provenance and the remaining physics gates. Stale v1 diagnostic success cannot satisfy those gates.
- Substantial implementation remains c1 Opus work after availability returns. No new automatic-resumption schedule was created: the earlier proposed negrw resumption schedule was rejected by automatic approval review, and no indirect workaround is authorized.

This is a recovered-state note, not a completed correctness review or model acceptance. No analysis/config/model files changed by parent; no credentials/services changed; no data deletion or push. Only this note is committed locally.
