#!/bin/bash
# vault-dump.sh — commit & push whatever has been written into the vault.
# Use from any lxplus session (live or new):  ~/obsidian-notes/scripts/vault-dump.sh "message"
#
# Convention (see CLAUDE.md): generated notes/docs -> Projects/<Project>/ ;
# reference papers/PDFs -> References/<Project>/ (committed) ; regenerable plots/parquet/ROOT
# stay on EOS and are linked, not committed.
set -e
VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$VAULT"
MSG="${1:-lxplus dump $(date +%F\ %H:%M)}"
git pull --rebase --autostash
git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit."
else
  git commit -m "lxplus: $MSG"
  git push
  echo "Pushed: $MSG"
fi
