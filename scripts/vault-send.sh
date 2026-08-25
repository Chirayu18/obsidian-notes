#!/usr/bin/env bash
# vault-send.sh — copy a file into the vault, commit, push, print its GitHub link.
#
# Usage:
#   scripts/vault-send.sh <file> [dest-subdir]
#
# Copies <file> into Projects/<dest-subdir>/ (default: Outbox/), commits and
# pushes, then prints both the blob and raw GitHub URLs.
#
# The vault repo is PUBLIC — anything sent this way is world-readable.
# Do not send anything unpublished, personal, or credential-bearing.

set -euo pipefail

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${1:?usage: vault-send.sh <file> [dest-subdir]}"
DEST_SUBDIR="${2:-Outbox}"

[ -f "$SRC" ] || { echo "vault-send: no such file: $SRC" >&2; exit 1; }

DEST_DIR="$VAULT/$DEST_SUBDIR"
mkdir -p "$DEST_DIR"

BASE="$(basename "$SRC")"
cp -f "$SRC" "$DEST_DIR/$BASE"

REL="${DEST_SUBDIR}/${BASE}"

cd "$VAULT"

# Refuse to push anything git is set to ignore — that list exists for a reason.
if git check-ignore -q "$REL"; then
  echo "vault-send: REFUSING — '$REL' is gitignored (see .gitignore)." >&2
  echo "            It stays local at: $DEST_DIR/$BASE" >&2
  exit 2
fi

git add -- "$REL"

if git diff --cached --quiet -- "$REL"; then
  echo "vault-send: no change to $REL (already up to date)"
else
  git commit -q -m "vault-send: $BASE" -- "$REL"
  git push -q origin HEAD
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
# URL-encode spaces; leave other chars alone (paths here are ASCII by convention).
URLREL="${REL// /%20}"

echo
echo "  view: https://github.com/Chirayu18/obsidian-notes/blob/${BRANCH}/${URLREL}"
echo "  raw:  https://github.com/Chirayu18/obsidian-notes/raw/${BRANCH}/${URLREL}"
echo
