#!/usr/bin/env bash
# Run in a human-controlled laptop terminal; no credentials enter chat or Git.
set -euo pipefail
if [[ $# -ne 0 ]]; then
  echo 'Usage: bash scripts/t3/login-laptop-claude2.sh' >&2
  exit 2
fi
profile=/home/cgupta/.claude-t3-2
if [[ ! -d "$profile" || -L "$profile" ]]; then
  echo 'The prepared account-2 profile directory is missing or a symlink.' >&2
  exit 1
fi
exec env CLAUDE_CONFIG_DIR="$profile" /home/cgupta/.local/bin/claude auth login --claudeai
