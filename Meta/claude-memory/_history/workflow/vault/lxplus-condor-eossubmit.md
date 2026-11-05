---
name: lxplus-condor-eossubmit
description: "Condor GPU jobs idle for hours on lxplus is usually just queue contention, not a fixable requirements bug; EosSubmit mechanics if /eos paths are ever actually needed"
metadata:
  type: reference
---

## First: idle GPU jobs are usually just contention

Seen 2026-09-08: **31k idle jobs vs 1,393 running** cluster-wide. A GPU training
job sitting idle for hours is the normal state, and the other flashjet arms
(baseline / CA5 / subjet) all waited this way before running. **Do not go
hunting for a requirements bug by default.**

`condor_q -better-analyze <cluster>` prints a `PreGPURequirements` chain that
includes `(TARGET.NODE_MOUNTS_AFS =?= true)`. **This is a red herring** — I read
it as "the free H100s don't mount AFS, that's why 0 slots match", rebuilt the job
to be EOS-resident, and moved it to the EosSubmit pool. Then checking the actual
slots showed `NODE_MOUNTS_AFS = true` on every free H100/A100. The clause was
satisfied all along; the job was simply queued behind 31k others.

**Before concluding requirements are the problem, check the slots themselves:**

```bash
condor_status -constraint 'TotalGPUs > 0 && State == "Unclaimed"' \
  -af GPUs_DeviceName Cpus Memory NODE_MOUNTS_AFS | sort | uniq -c
condor_q -all -af JobStatus | sort | uniq -c    # 1=idle 2=running; ratio tells the story
```

If free slots exist that satisfy every clause, it is contention — wait, do not
re-engineer. Note `-better-analyze`'s "N slots match" is a snapshot: it read 1
then 0 minutes later simply because that slot got claimed.

The AFS-based scripts under `~/flashjet_condor/` work fine on the standard pool.
That is the default; keep using it.

## EosSubmit mechanics (only if a job genuinely must use /eos paths)

Plain `condor_submit` REFUSES /eos paths: *"Standard batch schedds cannot use
/eos paths directly"*. If that is the real constraint:

1. Executable, submit file, and log/output dir all on EOS.
2. Submit file: `getenv = False`, `should_transfer_files = NO`, and **`log` must
   use `$(ClusterId)` only, never `$(ProcId)`**.
3. Load the module **in the same shell** as the submit:
   ```bash
   ssh lxplus 'source /etc/profile.d/modules.sh; module load lxbatch/eossubmit; \
               cd /eos/.../condor_jobs && condor_submit job.sub'
   ```

Gotchas:
- The module sets `_myschedd_POOL=eossubmit` and `_condor_CONDOR_HOST`; setting
  them by hand gives *"failed to choose schedd"* — load the module.
- `module` is a shell function: `source /etc/profile.d/modules.sh` first. Do
  **not** use `bash -lc` on lxplus — the login profile starts zellij and panics
  with ENOTTY over ssh.
- `condor_q` only shows the pool currently loaded, so jobs appear to vanish if
  you check without the module.
- A prepared EOS-resident copy exists at
  `/eos/user/c/cgupta/flashjet/condor_jobs/` (avoids sourcing `~/.bashrc`; sets
  MAMBA_EXE/MAMBA_ROOT_PREFIX inline, since micromamba already lives on EOS).

See [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]] and [[Meta/claude-memory/_history/workflow/vault/lxplus-afs-token-aklog|lxplus-afs-token-aklog]].
