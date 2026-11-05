---
name: lxplus-eos-persistent-mount
description: "EOS is mounted at ~/mnt/lxplus-eos by a persistent systemd user service, not the Claude hook"
metadata: 
  node_type: memory
  type: project
  originSessionId: 22858022-ebec-42a3-bd7c-86327e8c0e8f
---

lxplus EOS (`/eos/home-c/cgupta`) is mounted locally at `~/mnt/lxplus-eos` by a
**persistent systemd user service** `lxplus-eos.service`
(`~/.config/systemd/user/lxplus-eos.service` → runs `~/bin/lxplus-eos-mount.sh`).

- The service runs `sshfs -f` in the foreground so systemd tracks it;
  `Restart=always` remounts on network drop / process death (verified: kill the
  sshfs PID and it comes back in ~10s).
- `loginctl enable-linger cgupta` is set, so it survives logout and starts at boot.
- Manage it with `systemctl --user {status,restart,stop} lxplus-eos`.
- The SessionStart hook (`~/bin/lxplus-session-start.sh`) no longer mounts EOS by
  hand — it just `systemctl --user start`s the service if not mounted, keeping the
  service the single owner of the mountpoint. It still mounts AFS `~/mnt/lxplus`.

**Why the initial "connection: FAILED" happens:** the SessionStart hook can fire
*before* gnome-keyring's secrets daemon + DBus are ready at login, so
`~/bin/lxplus-connect.py`'s `keyring get` failed and aborted. Fixed by making
`keyring_get()` retry for ~30s. See [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]].
