---
name: lxplus-gpu-interactive
description: How to run GPU jobs on lxplus-gpu from this laptop — hop via lxplus Kerberos, name the node, hold the ssh session (tmux dies)
metadata:
  type: reference
---

Interactive GPU (Tesla T4 16 GB, 28 cores) works when condor A100/H100 slots are busy (2026-09-24: condor idle >1 h, lxplus-gpu free immediately).

- Reach it FROM lxplus using the delegated Kerberos ticket, never with a bare local ssh (see [[Meta/claude-memory/_history/workflow/vault/lxplus-ssh-askpass-trap|lxplus-ssh-askpass-trap]]):
  `ssh lxplus 'ssh -o BatchMode=yes -o GSSAPIDelegateCredentials=yes lxplus905.cern.ch "..."'`
- `lxplus-gpu.cern.ch` is load-balanced: each login lands on a different node. After the first login, address the node by name (e.g. lxplus905).
- tmux/nohup processes are KILLED when the ssh session logs out, unlike plain lxplus (see [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]]). Run the job in the foreground of an ssh session kept open by a local `run_in_background` Bash call. The job dies if that connection drops.
- The first run on a new node spends ~1–2 min in D state importing torch from EOS (cold cache). That is not a hang.
- Env: MAMBA_EXE/MAMBA_ROOT_PREFIX from [[Meta/claude-memory/_history/projects/Flashjet/vault/flashjet-workflow|flashjet-workflow]].
