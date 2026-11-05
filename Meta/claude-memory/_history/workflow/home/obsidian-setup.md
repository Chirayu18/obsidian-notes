---
name: obsidian-setup
description: "How Obsidian is installed and launched on this machine (extracted AppImage, not snap)"
metadata: 
  node_type: memory
  type: project
  originSessionId: afabef9f-6e11-4189-ba05-4b2443a23cb8
---

Obsidian runs from an **extracted AppImage**, not the snap (the snap launched silently with no window on this hybrid-GPU/Wayland setup; see [[Meta/claude-memory/_history/workflow/home/machine-graphics-setup|machine-graphics-setup]]).

- App files: `~/Applications/Obsidian.AppDir/` (extracted, not FUSE-mounted — system has FUSE 3 only, no libfuse2).
- Launcher: `~/Applications/obsidian-launch.sh` — calls `Obsidian.AppDir/obsidian --no-sandbox` directly. It bypasses `AppRun` because AppRun's AppDir auto-detection breaks when args are passed while running extracted (resolves binary to `/obsidian`). `--no-sandbox` is required (chrome-sandbox isn't root-owned setuid), matching how the snap launched.
- Menu entry: `~/.local/share/applications/obsidian.desktop` → points at the launcher script.

**How to apply:** To update Obsidian, download the new AppImage, extract it (`./Obsidian-x.y.z.AppImage --appimage-extract`), and replace `~/Applications/Obsidian.AppDir/` — keep the same path so the launcher and desktop entry keep working. Don't suggest the snap.
