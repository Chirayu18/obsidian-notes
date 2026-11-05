---
name: home-assistant-security
description: "ha-mcp auth posture — secret-URL mode chosen deliberately, plus open items"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ca21f69-71ba-4de4-a60c-ac4ca2aeca80
  modified: 2026-07-26T22:16:03.214Z
---

ha-mcp authenticates by **secret URL** — the webhook URL itself is the credential,
there is no token or OAuth on it. Chosen deliberately on 2026-07-27 after the
"Home Assistant sign-in" (OAuth) mode failed: HA's `/auth/authorize` rejects a
`redirect_uri` on a different origin than the `client_id`, so the Claude Code
localhost callback returns "Invalid redirect URI". Legacy OAuth mode (issues a
Client ID/Secret, needs an HA restart) was not tried and remains the fallback if
better auth is wanted.

**Why this is acceptable here:** the house is lights-only — three Govee bulbs and
a shopping list. No locks, cameras, or thermostats. Reconsider if any of those
are ever added, since the credential scope is all of HA, not just lights
(`ha_restart`, `ha_manage_backup`, `ha_manage_hacs` are all reachable, and HA
backups contain every credential HA holds).

**Open items** the user knows about and has not actioned:
- Port 9584 (ha-mcp direct access) binds `0.0.0.0`. Laptop is a NordVPN Meshnet
  hub, so reachability is every Meshnet peer, not just the LAN. The configured
  path is the `8123` webhook, so 9584 can be firewalled.
- A long-lived HA token (issued 2026-07-26, expires 2036) is still valid with no
  consumer left. It leaked into a session transcript. Deleting it costs nothing.
- Dead `home-assistant` MCP server entry still in `~/.claude.json`
  (`claude mcp remove home-assistant`).

See [[Meta/claude-memory/_history/workflow/home/home-assistant-setup|home-assistant-setup]] for the entities and scenes.
