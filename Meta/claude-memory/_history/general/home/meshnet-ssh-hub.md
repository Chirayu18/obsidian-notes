---
name: meshnet-ssh-hub
description: "Laptop is an always-on SSH server on NordVPN Meshnet, used as the hub for remote work (Mac/phone -> laptop -> lxplus)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e2afe2c-fcb5-4add-9605-00cf993209ff
---

As of 2026-07-18 this laptop (`chirayu.gupta-alps.nord`, meshnet IP 100.126.212.38) is configured as an always-on SSH server: openssh-server enabled, suspend/hibernate targets masked, lid switch ignored via `/etc/systemd/logind.conf.d/always-on.conf`, nordvpnd enabled at boot. User connects from a Mac/phone over NordVPN Meshnet and wants Claude Code always running here (recommended: inside tmux). The laptop maintains the persistent lxplus connection (ControlPersist + sshfs AFS/EOS mounts via `~/bin/lxplus-*` scripts and the SessionStart hook). Per user (2026-07-18): the current lxplus setup does NOT depend on Kerberos ticket renewal — do not flag Kerberos/AFS expiry as a concern for long-running sessions. Related: [[Meta/claude-memory/_history/workflow/home/machine-graphics-setup|machine-graphics-setup]].
