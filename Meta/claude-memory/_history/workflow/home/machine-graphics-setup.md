---
name: machine-graphics-setup
description: "Desktop/GPU environment — Ubuntu 26.04, COSMIC/Wayland, hybrid Intel+NVIDIA, group fix for GPU access"
metadata: 
  node_type: memory
  type: project
  originSessionId: afabef9f-6e11-4189-ba05-4b2443a23cb8
---

This machine runs **Ubuntu 26.04 with the COSMIC desktop on Wayland** (`cosmic-comp`), shell is zsh. GPU is **hybrid: Intel UHD (Alder Lake-S iGPU) + NVIDIA RTX 4050 Mobile dGPU**. `ollama` actively uses the NVIDIA card via CUDA.

User `cgupta` was originally **not in the `video`/`render` groups**, which blocked confined apps (snaps) from `/dev/dri/*` and produced `DRM access error: Permission denied (os error 13)`. Fixed via `sudo usermod -aG video,render cgupta` + reboot — now in both groups.

**Why:** Electron/snap GUI apps fail in subtle ways on this stack (silent no-window launches). **How to apply:** When a GUI app won't show a window, suspect this combo: check group membership for GPU access, and consider that snap classic-confinement apps hit the host NVIDIA GL stack and can fail — prefer AppImage/native packages. cosmic-comp logs some harmless config-key-not-found errors on startup; ignore those. See [[Meta/claude-memory/_history/workflow/home/obsidian-setup|obsidian-setup]] for a worked example.
