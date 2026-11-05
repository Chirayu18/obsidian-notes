#!/usr/bin/env bash
# SessionStart vault sync. Called from .claude/settings.json.
#
# Why this exists: several Claude sessions (startup, fork, resume) often start
# at the same moment in this checkout. Concurrent `git pull` runs all rewrite
# the shared .git/FETCH_HEAD, which then has several "for-merge" lines, and
# git fails with "fatal: Cannot rebase onto multiple branches." The old inline
# hook ended with `; true`, so the failure was invisible.
#
# Behaviour:
#   - one sync at a time (flock on the shared git dir); later sessions wait
#     briefly, then skip with a message
#   - normal branch with upstream: git pull --rebase --autostash
#   - autoresearch/* branches, branches without upstream, detached HEAD,
#     or a rebase/merge already in progress: fetch only, no working-tree change
#   - any failure prints "VAULT SYNC FAILED" plus git's output; exit stays 0
#     so a session never fails to start because of sync
set -u
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || { echo "VAULT SYNC FAILED: cannot cd to project dir"; exit 0; }

gitdir=$(git rev-parse --git-dir 2>/dev/null) || { echo "vault sync skipped: not a git repo"; exit 0; }
commondir=$(git rev-parse --git-common-dir)

exec 9>"$commondir/session-sync.lock"
if ! flock -w 30 9; then
  echo "vault sync skipped: another session's sync still holds the lock after 30s"
  exit 0
fi

fetch_only() {
  local reason=$1 out
  if out=$(git fetch --quiet origin 2>&1); then
    echo "vault sync: fetch only ($reason)"
  else
    echo "VAULT SYNC FAILED: git fetch ($reason)"; printf '%s\n' "$out" | tail -5
  fi
  if git rev-parse --verify --quiet '@{u}' >/dev/null; then
    read -r behind ahead < <(git rev-list --left-right --count '@{u}...HEAD')
    echo "vault sync: this branch is $ahead ahead, $behind behind $(git rev-parse --abbrev-ref '@{u}') (not merged)"
  fi
}

if [ -d "$gitdir/rebase-merge" ] || [ -d "$gitdir/rebase-apply" ] || [ -f "$gitdir/MERGE_HEAD" ]; then
  fetch_only "rebase or merge already in progress; resolve it by hand"
  exit 0
fi

branch=$(git symbolic-ref --quiet --short HEAD) || { fetch_only "detached HEAD"; exit 0; }

case "$branch" in
  autoresearch/*) fetch_only "session branch $branch is never auto-rebased"; exit 0 ;;
esac

if ! git rev-parse --verify --quiet '@{u}' >/dev/null; then
  fetch_only "no upstream on $branch"
  exit 0
fi

out=$(git pull --rebase --autostash 2>&1); rc=$?
if [ $rc -eq 0 ]; then
  printf '%s\n' "$out" | tail -3
else
  echo "VAULT SYNC FAILED: git pull --rebase --autostash on $branch exited $rc"
  printf '%s\n' "$out" | tail -8
  git stash list | grep -q autostash && echo "NOTE: an autostash entry is in 'git stash list'; your local edits are there, not lost"
fi
exit 0
