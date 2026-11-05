---
name: lxplus-ssh-askpass-trap
description: "KDE exports SSH_ASKPASS_REQUIRE=prefer, which routes lxplus password/2FA prompts to a GUI dialog and breaks the keyring auto-login; fix is to strip askpass vars in lxplus-connect.py"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca1d5af5-d905-4786-99d4-638c3410fc16
  modified: 2026-09-12T13:26:00.321Z
---

The desktop session exports `SSH_ASKPASS=/usr/bin/ksshaskpass` and
**`SSH_ASKPASS_REQUIRE=prefer`**. `prefer` makes ssh send password/2FA prompts to the
**graphical ksshaskpass dialog even when a tty exists**. That silently breaks
`~/bin/lxplus-connect.py`: it drives prompts with pexpect by reading the pty, but the
prompt never arrives there — pexpect matches nothing and times out on its 60s limit
while the user gets an interactive password popup, which is exactly what the keyring
setup exists to prevent.

Fixed 2026-09-12 in `~/bin/lxplus-connect.py`: the `pexpect.spawn` now passes an `env`
with `SSH_ASKPASS`, `SSH_ASKPASS_REQUIRE`, `DISPLAY`, `WAYLAND_DISPLAY` removed. The
systemd user manager exports these too, so `lxplus-eos.service` inherited the same trap.

**Why:** the user must NEVER be asked for the lxplus password — auth goes through the
keyring (`keyring get lxplus` / `lxplus_2FA` + pyotp). A visible prompt means the
non-interactive path failed, not that interactive auth is acceptable.

**How to apply:**
- A password popup during any lxplus connect = this bug or a regression of it. Do NOT
  "just answer it" and do NOT run bare `ssh lxplus` / `BatchMode=no` probes to diagnose —
  each spawn re-prompts the user. Diagnose from `journalctl --user -u lxplus-eos.service`
  and env inspection instead.
- Secrets live ONLY in gnome-keyring (SecretService). KWallet has higher chainer priority
  (5.1 vs 5.0) but holds nothing for lxplus; the chainer falls through, so that is a red
  herring, not the failure.
- `gcr-prompter: cannot open display` in the login logs is also a red herring — it clears
  once the desktop is up. Don't stop there; the askpass routing is the real cause.
- `lxplus-eos.service` has `StartLimitBurst=10`/`RestartSec=10`, so a failing auth burns all
  restarts in ~2 min and latches off permanently. Recovery needs
  `systemctl --user reset-failed lxplus-eos.service` before `start` — it never self-heals.

See [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]], [[Meta/claude-memory/_history/workflow/vault/lxplus-eos-persistent-mount|lxplus-eos-persistent-mount]], [[Meta/claude-memory/_history/workflow/vault/lxplus-afs-token-aklog|lxplus-afs-token-aklog]].
