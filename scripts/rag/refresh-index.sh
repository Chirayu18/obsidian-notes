#!/usr/bin/env bash
# Refresh the RAG index in the background, then exit immediately.
#
# Called from SessionEnd (1.5s shared budget) and PreCompact hooks, so it must
# never block: it detaches the rebuild and returns at once. A lock keeps
# overlapping sessions from embedding the same files twice.
#
#   refresh-index.sh          # detached, silent -- the hook path
#   refresh-index.sh --wait   # run in foreground, show output -- for testing
#   refresh-index.sh --worker # internal: the actual rebuild, holds the lock
set -uo pipefail

VAULT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
SELF="$VAULT/scripts/rag/refresh-index.sh"
LOCK="$VAULT/.vault-rag-index.lock"
LOG="$VAULT/.vault-rag-index.log"

worker() {
  # flock -n: if a rebuild is already running, drop this one rather than queue.
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "[rag] $(date -Is) rebuild already running, skipped" >>"$LOG"
    return 0
  fi
  {
    echo "--- $(date -Is) rebuild start"
    python3 "$VAULT/scripts/rag/build_index.py"
    echo "--- exit=$? $(date -Is)"
  } >>"$LOG" 2>&1
  # Keep the log from growing without bound across many sessions.
  if [[ -f "$LOG" ]] && (( $(wc -l <"$LOG") > 500 )); then
    tail -200 "$LOG" >"$LOG.tmp" && mv "$LOG.tmp" "$LOG"
  fi
}

case "${1:-}" in
  --worker) worker ;;
  --wait)   worker; tail -6 "$LOG" ;;
  *)
    # Detach fully: new session, stdio closed, so the hook's 1.5s budget is
    # not spent waiting on embedding work that can take minutes.
    setsid "$SELF" --worker </dev/null >/dev/null 2>&1 &
    disown 2>/dev/null || true
    ;;
esac
exit 0
