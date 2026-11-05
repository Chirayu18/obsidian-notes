---
tags: [reference]
status: superseded
superseded_by: "[[2026-11-05-lxplus-t3-pilot]]"
date: 2026-11-05
source: laptop
---

# lxplus T3 readiness checks and approved AFS cleanup

**Agent-reported, with command-validated observations.** Read-only checks were run from the laptop over the existing ControlMaster on 2026-11-05, approximately 13:20–13:29 UTC. Two subsequent file deletions were explicitly requested by Chirayu and verified. No T3 server/provider was launched, environment paired/linked, service changed/restarted, credential renewed, job submitted or Git push performed.

This records the executed parts of [the proposed checklist](2026-11-05-lxplus-t3-checks-and-project-routing.md) and adds evidence to [the recommendation](2026-11-05-t3-connect-vs-lxplus-setup.md). Earlier investigation-time statements that checks had not run remain historical; this is the later live snapshot, not a replacement for the checklist or policy guidance.

**Verdict: proceed with a short supervised SSH-backed toy pilot once CERN runtime/model-egress permission and a suitable T3 state location are confirmed.** The current transport works. The proposed separate ControlMaster unit is not a prerequisite: the existing master already belongs to the EOS service's cgroup. Deleting the requested files restores home-directory headroom, but does not establish AFS suitability for T3's live database. A persistent deployment is not validated.

## Observed transport and remote tools

- `ssh -O check lxplus`: master running, PID `4084`. `ssh -G lxplus`: BatchMode enabled, ControlMaster auto, control socket `/home/cgupta/.ssh/cm-cgupta@lxplus.cern.ch:22`, ControlPersist `28800` seconds. Subsequent SSH calls named this socket and disabled all fresh authentication methods. They reached **lxplus938.cern.ch**, user `cgupta`, architecture `x86_64`.
- `systemctl --user show lxplus-eos.service`: active/running, Restart always, MainPID `2067`, KillMode `control-group`. `/proc/4084/cgroup` matches that service's cgroup. Thus the master currently runs within the EOS service lifecycle, despite no separate master unit. Restarting/stopping that unit can terminate the shared master; no such test was performed.
- `loginctl show-user cgupta` on the laptop: Linger yes. Only `lxplus-eos.service` was listed by the `lxplus*` user-unit inventory. Both laptop SSHFS mounts were present, writable in the host mount namespace, and their root directories passed a bounded read check. Filenames were suppressed.
- Non-interactive remote `sh -lc` found `curl`, `wget`, `tar`, `sha256sum`, `shasum`, Python and Node. It found Claude at `~/.local/bin/claude`, resolving to `~/.local/share/claude/versions/2.1.196`, executable according to filesystem permissions. Claude was not executed or authenticated. **Codex and T3 were not on PATH**; `~/.t3` did not exist. These checks do not exclude installations elsewhere.
- `node --version`: `v16.20.2`. Compatibility of T3's packaged runtime was not tested; this version alone does not prove that the packaged runtime cannot work.
- `condor_q`, `crab` and `scram` were found at `/usr/bin/condor_q`, `/cvmfs/cms.cern.ch/common/crab`, and `/cvmfs/cms.cern.ch/common/scram`. No scheduler or CRAB command was executed; CMSSW setup was not changed.
- `t3_environment_read` still identifies the laptop server, version `0.1.6`. No remote environment was registered during these checks.

The sandbox initially reported SSH system-config ownership and user-bus errors, and displayed the mounts as read-only. The same authorized observations outside the sandbox succeeded and showed host mounts as writable. Those initial errors were sandbox limitations, not evidence that the host setup was broken.

## Credentials, storage and limits

- Remote `klist -s` returned **0**: a valid ticket existed in this SSH execution context. This does not establish what a future T3 service would inherit.
- `voms-proxy-info -timeleft` returned **1**, reporting no valid proxy. `X509_USER_PROXY` was unset. This only describes default discovery in this session; other custom locations were not searched. A proxy is unnecessary for the synthetic toy test, but proxy-dependent CMS work remains unready. No renewal was attempted.
- Remote `findmnt` confirms home on **AFS**, EOS on its FUSE filesystem, and `/tmp` on node-local ext4. AFS/EOS root directory reads succeeded. Persistence and policy for a T3 state location remain undecided.
- Remote user manager: running; `loginctl show-user` reports **Linger=no**. No logout-survival test was performed. These observations neither authorize nor guarantee a persistent service.
- Reading the current session and ancestor cgroup files showed user-slice `memory.max=36858716160` bytes (about **34.33 GiB**), and ancestor `user.slice` `memory.max=55288074240` bytes. The inspected CPU quota entries were `max 100000`. This is a host/session snapshot, not a resource allocation, a statement of all service limits or permission to use those resources. `getrlimit` reported open-files soft/hard limits `1024/524288`; CPU/address-space limits were unlimited at that layer.

## AFS usage before the approved deletions

`fs listquota -path /afs/cern.ch/user/c/cgupta` initially reported quota **10485760 KiB**, used **10185530 KiB**, **97%** used, about **293 MiB** remaining. `df -h` on AFS did not expose this user-volume constraint. Quota/used fields are documented by [OpenAFS](https://docs.openafs.org/Reference/1/fs_listquota.html).

`du -x -k --max-depth=1` over AFS home completed successfully without following symlinks into EOS. Its home total was **10182961 KiB**; the small difference from volume quota accounting is not treated as missing data. Major pre-deletion consumers, with `du` KiB as the source units:

- `local/`: **2102256 KiB**, almost entirely `local/run2.root`; file allocated size **2152642560 bytes**.
- `.local/`: **1890225 KiB**. Deeper `du` found Python libraries **850671 KiB**, Claude install data **478178 KiB**, and Neovim share data **356315 KiB**; these are subsets, not additional totals.
- `higgscharm_thomas/`: **1412969 KiB**, including its newer checkout **1128816 KiB** and other checkout **284151 KiB**.
- `.cache/`: **714540 KiB**, including pip cache **581826 KiB**. This was measured, not classified as authorized to delete.
- `negrw_condor/`: **697952 KiB**; `negrw_train.tar.gz` accounts for **695945216 allocated bytes**.
- `gridpack/`: **676291 KiB**, with multiple generator/process trees.
- `CMSSW_14_1_0_pre4/`: **576252 KiB**, including `src/` **497122 KiB** and `tmp/` **68031 KiB**.

No other storage was removed, moved or inspected for file contents.

## Explicitly authorized deletions and current quota

Chirayu, verbatim:

> delete run2.root then gimme ur verdict on the pilot

Deleted exactly `/afs/cern.ch/user/c/cgupta/local/run2.root`, after checking that it remained a regular file with the inspected logical size **2152641898 bytes**. Confirmed absent afterward. The subsequent `fs listquota` used value was **8083340 KiB**.

Chirayu then said, verbatim:

> no remove run2mcnano.root as well

Deleted exactly `/afs/cern.ch/user/c/cgupta/Run2mcnano.root`, after the same regular-file/unchanged-size check against **43095590 logical bytes**. At **2026-11-05 13:29:00 UTC**, both paths were confirmed absent. No backups were created by this task.

**Latest quota:** `fs listquota` after the second deletion reports **8041254 KiB used / 10485760 KiB quota**, displayed **77%** used, leaving **2444506 KiB**, approximately **2.33 GiB**. Earlier usage figures above are explicitly pre-deletion snapshots.

## Remaining gates

Before a toy pilot: confirm CERN permission for the runtime/provider egress and choose a suitable allowed live-state location. Then install/start only the approved version/provider, choose Supervised and repeat identity/credential checks from inside the actual T3 runtime. No provider API traffic, OAuth/login, network-egress probe, private analysis test, runtime installation or policy inquiry was performed here.

Keep conductor/keeper on the laptop and one worker globally. Retain the present SSH workflow as fallback. Resolve keeper-reviewed remote vault-commit transfer before routine remote workers. No need to add a cloud tunnel, a separate master service or a second paid plan merely to attempt this pilot.
