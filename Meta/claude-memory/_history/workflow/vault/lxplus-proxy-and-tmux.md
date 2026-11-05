---
name: lxplus-proxy-and-tmux
description: "Which grid proxy file is actually valid on lxplus (cms.proxy is EXPIRED), and why long submissions need tmux"
metadata: 
  node_type: memory
  type: project
  originSessionId: af76ec6a-a549-46b2-be18-cf006051e43e
  modified: 2026-09-25T16:53:00.602Z
---

**Use `/afs/cern.ch/user/c/cgupta/private/x509up_u151861`** — this is the valid grid proxy.

```bash
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
```

**Do NOT use `/afs/cern.ch/user/c/cgupta/cms.proxy` or `/afs/cern.ch/user/c/cgupta/x509up`** —
both report `timeleft 0:00:00` (expired; `cms.proxy` dates to 2026-04-07 and its signing cert
has also expired). As of 2026-08-11 the `private/` copy had ~4.9 days left.

**Why it matters:** the proxy is node-local, so `/tmp/x509up_u$(id -u)` is usually absent on
whichever lxplus node you land on. Without `X509_USER_PROXY` pointing at the AFS copy,
`jobs_status.py` fails during fileset regeneration — `fetch.py` raises
`VOMS proxy expired or non-existing`, and the resubmit silently regenerates nothing.

**Never run `voms-proxy-init`/`kinit`** — that prompts for a passphrase. If all AFS copies
are expired, stop and tell the user; do not prompt.

**Long submissions need `tmux`, not `nohup`** — and log to **AFS**, not `/tmp`. `/tmp` is
node-local, so a log written there is unreachable once you reconnect to a different node
(this silently lost a card-build log). Also: `pgrep -f <script>` over ssh matches its **own**
command string, so it reports a dead job as running — check `tmux ls` and output-file
timestamps instead.

**tmux is node-local too — and `ssh lxplus` round-robins.** A waiter polling
`tmux has-session` from a *new* `ssh lxplus` lands on a different node, sees no session,
and exits "done" while the job is still running (2026-09-25, card build). Don't pin with
`ssh lxplusNNN.cern.ch` (host-key prompt → askpass trap, see [[Meta/claude-memory/_history/workflow/vault/lxplus-ssh-askpass-trap|lxplus-ssh-askpass-trap]]).
Wait on a **shared-filesystem signal** instead: the output file on AFS/EOS, or a log line.
The same goes for tmux sessions started with LCG-view env: wrap commands in
`env -u PYTHONPATH -u PYTHONHOME -u LD_LIBRARY_PATH` or conda/cmssw Python breaks.
(As of 2026-09-25 the `private/` proxy is expired, timeleft 0.)

Related: [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]], [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]]
