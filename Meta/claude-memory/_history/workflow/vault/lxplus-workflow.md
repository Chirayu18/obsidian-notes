---
name: lxplus-workflow
description: "How to connect to and run work on lxplus (CERN) from this machine — auto-connect, ssh, sshfs mount, micromamba"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2e766a78-f7a7-4774-8ddf-2080cc28bf1b
---

The user works on CMS analysis on lxplus (CERN) and wants Claude sessions on this
machine to transparently do work there. **Why:** analysis code, EOS data, and the
b-hive environment all live on lxplus; the laptop just runs Claude + Obsidian.

**How to apply:**
- **Connection is auto-established at session start** by a SessionStart hook in
  `~/.claude/settings.json` → runs `~/bin/lxplus-session-start.sh`, which is
  idempotent: it ensures the ssh ControlMaster is up and `~/mnt/lxplus` is
  sshfs-mounted. It does NOT run any user/analysis code — that only happens when
  the user asks.
- **Login is non-interactive:** `~/bin/lxplus-connect.py` pulls the password from
  `keyring get lxplus cgupta` and the 2FA TOTP secret from
  `keyring get lxplus_2FA cgupta`, generates the code with `pyotp`, and drives
  ssh's keyboard-interactive prompts with `pexpect`. Prompts are
  `(cgupta@lxplus.cern.ch) Password:` then `Your 2nd factor (cgupta):`. The user
  must NEVER be prompted for password/TOTP — I supply them.
- **If the connection DROPS mid-session** (Kerberos ticket expired → `ssh lxplus`
  fails with `Permission denied (publickey,gssapi-with-mic,keyboard-interactive)`
  and falls back to a password prompt; the resume hook reports
  `[lxplus] connection: FAILED`), recover in this order — ALWAYS do this yourself,
  never ask the user for a password or run `kinit` by hand:
  1. **Reconnect:** `python3 ~/bin/lxplus-connect.py` — idempotent (prints
     `MASTER_ALREADY_UP` if fine), re-auths non-interactively from the keyring.
  2. **The mounts do NOT come back on their own.** When the connection dropped they
     died too: the `lxplus-eos.service` (systemd --user) goes to `failed`, and the
     AFS sshfs mount at `~/mnt/lxplus` just vanishes (both `ls` return empty; `mount`
     shows no lxplus entries). Remount by restarting the EOS service **and** re-running
     the session-start script (there is NO `lxplus.service` — that name errors):
     `systemctl --user restart lxplus-eos`
     `~/bin/lxplus-session-start.sh`  (idempotent; re-does the AFS sshfs mount)
  3. **Verify all three:** `ssh lxplus 'echo OK $(hostname)'`, then
     `ls ~/mnt/lxplus` and `ls ~/mnt/lxplus-eos` must both be non-empty. Confirm with
     `mount | grep sshfs` → two `fuse.sshfs` lines (AFS home + EOS).
  Node may change on reconnect (load-balanced, e.g. lxplus933 → lxplus955).
- **Run commands on lxplus with** `~/bin/lxplus-ssh '<cmd>'` (NOT bare `ssh lxplus`).
  The wrapper checks the ControlMaster and, if it's dead, re-runs `lxplus-connect.py`
  (keyring + pexpect) BEFORE running the command — so a mid-session master death can
  never fall through to an interactive password/2FA dialog. **Why the dialog used to
  pop:** the master would die mid-session and a bare `ssh lxplus` re-authed
  interactively. **Anti-dialog guard:** the `lxplus` host block in `~/.ssh/config` now
  sets `BatchMode yes` (a dead master FAILS fast instead of prompting) and
  `ControlPersist 8h` (master rarely dies). `connect.py` overrides with `BatchMode=no`
  on its own spawn, so non-interactive auth still works. Lands on the same node,
  home = `/afs/cern.ch/user/c/cgupta`. Bare `ssh lxplus` still works when the master
  is up; use the wrapper for anything automated.
- **micromamba is a shell function, not on PATH** in non-interactive ssh — prefix
  env commands with `source ~/.bashrc`, e.g.
  `ssh lxplus 'source ~/.bashrc; micromamba activate b_hive; <cmd>'`. Envs live
  under `/eos/home-c/cgupta/EPR_task/b-hive/micromamba`: `base`, `b_hive`,
  `fjbench`, `test`.
- **Filesystem:** `~/mnt/lxplus` = the AFS home, browsable locally for Read/Edit.
- ssh prints a post-quantum key-exchange warning on every call — filter it out
  (`grep -v -i 'post-quantum|vulnerable|openssh.com/pq'`).

Default expectation: when the user asks to work on something in a new session, do
it ON lxplus (not locally). Full write-up in the vault at
`References/Private/lxplus-workflow.md` (gitignored — that whole `References/Private/`
folder is private/machine-local, never committed). Related: `[[vault-sync-discipline]]` (unresolved historical reference; source absent from imported corpus).
