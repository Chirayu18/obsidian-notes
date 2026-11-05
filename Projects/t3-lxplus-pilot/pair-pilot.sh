#!/usr/bin/env bash
# Run in your laptop terminal: the pairing secret is printed there, not in chat.
set -euo pipefail
exec ssh \
  -S /home/cgupta/.ssh/cm-cgupta@lxplus.cern.ch:22 \
  -o ControlMaster=no -o ControlPersist=no -o BatchMode=yes \
  -o PreferredAuthentications=none -o GSSAPIAuthentication=no \
  -o PubkeyAuthentication=no -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o StrictHostKeyChecking=yes \
  -o UpdateHostKeys=no lxplus \
  'env T3CODE_HOME=/tmp/cgupta-t3-pilot-20261105-hgv57rp7/state LD_LIBRARY_PATH=/tmp/cgupta-t3-pilot-20261105-hgv57rp7/runtime/lib /tmp/cgupta-t3-pilot-20261105-hgv57rp7/runtime/t3 pair --base-dir /tmp/cgupta-t3-pilot-20261105-hgv57rp7/state --label laptop-pilot --ttl 10m --scope orchestration:read --scope orchestration:operate --scope providers:manage --scope terminal:read --scope terminal:operate --scope filesystem:read --scope filesystem:write --scope diagnostics:read --scope access:read'
