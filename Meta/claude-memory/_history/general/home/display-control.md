---
name: display-control
description: How to turn the external HDMI monitor on/off from a shell — cosmic-randr needs explicit Wayland env
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ca21f69-71ba-4de4-a60c-ac4ca2aeca80
  modified: 2026-07-26T22:53:21.708Z
---

The laptop drives two displays: `eDP-1` (built-in panel) and `HDMI-A-1` (external
Samsung S24D330, 1920x1080@60, positioned at 1920,0 — right of the laptop).

Control them with `cosmic-randr` (COSMIC/Wayland — `wlr-randr` is NOT installed):

```bash
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
cosmic-randr disable HDMI-A-1     # turn external off
cosmic-randr enable  HDMI-A-1     # turn it back on
cosmic-randr list                 # check state
```

**The env vars are required.** A plain `cosmic-randr enable HDMI-A-1` from an agent
shell fails with `Error: WaylandConnection(NoCompositor)` because the shell doesn't
inherit the Wayland session. There are two sockets in `/run/user/1000/`:
`wayland-1` is the live compositor; `wayland-2` returns `UnknownOutput`.

Only works while an agent is driving the shell. A standalone voice/hotkey trigger
would need a local script bound to a COSMIC keyboard shortcut — HA cannot do this
(it runs in a container and can't reach the display).

Related: [[Meta/claude-memory/_history/workflow/home/machine-graphics-setup|machine-graphics-setup]], [[Meta/claude-memory/_history/preferences/home/browser-automation-preferences|browser-automation-preferences]].
