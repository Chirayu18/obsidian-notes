---
name: vub-wifi-mac-block
description: VUB eduroam/VUBnext ignore the laptop's real MAC; fixed with a cloned Intel-prefix MAC on 2.4 GHz
metadata:
  type: project
---
As of 2026-09-29, VUB's Aruba APs don't answer 802.11 auth from the laptop's hardware MAC 50:28:4a:65:4b:cc (kernel log: "authentication ... timed out"). Credentials are fine.
Randomized (locally-administered) MACs got through EAP but received no DHCP lease.
Working fix: eduroam and VUBnext profiles use cloned-mac-address 50:28:4a:12:c7:a7 (Intel OUI), band bg, dhcp-timeout 90.
**Why:** likely an Aruba auth-failure blocklist on the hardware MAC; DHCP seems to deny random MACs.
**How to apply:** if VUB wifi breaks again, check `journalctl -k | grep wlp0s20f3` for auth timeouts before suspecting the password. The profiles also don't validate the server certificate yet (not fixed).
