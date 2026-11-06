#!/usr/bin/env bash
# Compatibility entry point: use the current pilot manifest, not a stale node/path.
set -euo pipefail
exec python3 /home/cgupta/obsidian-notes/scripts/t3/pair-lxplus-pilot.py "$@"
