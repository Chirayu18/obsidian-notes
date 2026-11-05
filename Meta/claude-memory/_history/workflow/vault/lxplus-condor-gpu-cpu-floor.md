---
name: lxplus-condor-gpu-cpu-floor
description: "EosSubmit rewrites CPU/mem to a per-GPU FLOOR (min 5 CPU/15000MB) that no V100S slot can satisfy -- pinning V100S with request_GPUs=1 is unsatisfiable, always"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8cb963cf-d304-4ee6-8f09-c79b0129a6f5
  modified: 2026-09-14T13:17:28.296Z
---

**A GPU job pinned to `Tesla V100S-PCIE-32GB` on the EosSubmit pool can never
match.** Confirmed 2026-09-13 after two clusters sat idle 26 h with
`condor_q -better-analyze` saying *"No machines matched the job's constraints"*.

The pool **rewrites `request_CPUs`/`request_memory` to a per-GPU floor**, and the
floor is above V100S capacity:

| requested | queued as |
|---|---|
| 16 CPU / 32 GB | 6 CPU / 18000 MB |
| 4 CPU / 14 GB | **5 CPU / 15000 MB** |

It is a **floor, not a cap** — asking for less does not get you less. V100S slots
are at best **4 CPU / 16000 MB** (14 of ~20; others 4/10000, 0/6000). 5 > 4, so no
request fits.

**Use A100 (`NVIDIA A100-PCIE-40GB`) or H100 NVL instead** — free slots there carry
8-12 CPUs and 93-106 GB. Repinning flipped the analyzer from "No machines matched"
to "9 reject / 20 would match if drained" = an ordinary queue wait.

**Second trap, hit right after: `State == "Unclaimed"` is NOT an availability
query for GPU jobs.** Partitionable slots advertise leftover CPU/memory while
`GPUs = 0` because every GPU is handed to a running job. 15-17 A100 slots looked
"free" when none had a GPU. Always query:

```bash
condor_status -constraint 'GPUs_DeviceName == "..." && GPUs >= 1 && State == "Unclaimed"'
```

Widening to `A100 || H100 NVL` raised candidate slots 9 -> 26. GPU-hours on this
pool are genuinely scarce; expect to wait even with correct requirements.

**How to tell the difference (do this before waiting hours):**

```bash
ssh lxplus 'aklog; source /etc/profile.d/modules.sh; module load lxbatch/eossubmit; \
            condor_q -better-analyze <cluster>' | grep -E "slots match and are willing|No machines matched"
```

"No machines matched" = a requirements bug, fix it now. Nonzero "would match if
drained" = real contention, just wait (see [[Meta/claude-memory/_history/workflow/vault/lxplus-condor-eossubmit|lxplus-condor-eossubmit]]).

**Third trap (2026-09-14): every idle GPU slot is `InStagedDrain = true`.**
Symptom: a large "would match if drained" (33) with **0 willing**, while
`condor_status` shows 10+ unclaimed slots with a free GPU that satisfy every
published constraint. Those machines are **retiring** — `ShutdownTime` already
in the past — and will never take the job. Always exclude them:

```
requirements = ... && (TARGET.InStagedDrain =!= true)
```

Check what live capacity actually exists before assuming a requirements bug:

```bash
condor_status -constraint 'GPUs >= 1 && InStagedDrain =!= true' -af GPUs_DeviceName | sort | uniq -c
```

Get the per-slot reason from the **slot side** — job-side `-better-analyze`
cannot show it:

```bash
condor_q <cluster> -better-analyze -reverse -machine slot1@<host>
```

Read the numbered steps: `[25] 0 TARGET.RequestMemory <= MY.Memory` is the
memory floor biting (1g.12gb MIG slices advertise 17000 MB, under the 18000 MB
floor); `[9] 0 SCond_dteam_bypass || SCond_staged_drain` is the drain gate.
**Do not** read `[16] not now  time() - EnteredCurrentState` as the blocker —
line `[17]` right below it is the real condition (`> 600`), and slots idle for
*days* still print "not now" on `[16]`. I misread this once and chased a
phantom 10-minute timer.

Also beware: `condor_q -af Requirements` can print a bare `false` (it evaluates
in the wrong context). That is a **display artifact**, not the stored ClassAd —
check `condor_q <cluster> -l | grep -i requirements` before believing it. Both of
these sent me chasing phantom requirement bugs for ~20 min.

MIG slices are separate device names and are fine for plain inference (not for
ncu, where clocks cannot be locked): `NVIDIA H100L-1-12C MIG 1g.12gb` and
`NVIDIA H100L-2-24C MIG 2g.24gb`. They are often the only idle GPUs in the pool.

Also: `condor_submit` failing with *"store_cred of Kerberos credential failed"*
plus `.bashrc: Permission denied` on ssh = expired AFS token → run `aklog`
([[Meta/claude-memory/_history/workflow/vault/lxplus-afs-token-aklog|lxplus-afs-token-aklog]]). Put `aklog` at the front of every remote command in
a long-running condor workflow.
