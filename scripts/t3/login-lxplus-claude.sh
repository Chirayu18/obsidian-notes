#!/usr/bin/env bash
# Run in a human-controlled laptop terminal. No credentials are copied.
set -euo pipefail
case "${1:-}" in
  1|2) slot=$1 ;;
  *) echo 'Usage: bash scripts/t3/login-lxplus-claude.sh 1|2' >&2; exit 2 ;;
esac
exec ssh -t \
  -S /home/cgupta/.ssh/cm-cgupta@lxplus.cern.ch:22 \
  -o ControlMaster=no -o ControlPersist=no -o BatchMode=yes \
  -o PreferredAuthentications=none -o GSSAPIAuthentication=no \
  -o PubkeyAuthentication=no -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
  -o UpdateHostKeys=no lxplus \
  "env CLAUDE_CONFIG_DIR=/afs/cern.ch/user/c/cgupta/private/claude-t3-$slot /afs/cern.ch/user/c/cgupta/.local/bin/claude auth login"
