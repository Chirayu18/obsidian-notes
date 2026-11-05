---
tags: [index]
status: active
date: 2026-11-05
source: laptop
---

# Vault sync

Current source of truth: [[Meta/setup]] and [[CLAUDE]].

- Workers commit locally and do not push.
- The keeper reviews changes, runs `git pull --rebase`, then pushes; never force-push.
- The configured upstream of master is `ssh/master`. `origin` and `ssh` point to the same GitHub vault.
- Obsidian Git auto-commit and auto-push are off; auto-pull remains enabled.
- Historical instructions are retained in [[Meta/_history/SYNC]] and [[Meta/_history/lxplus-global-CLAUDE]]. They are snapshots, not current operational instructions.

All PNG and PDF files stay local and are ignored, including reference papers; the published reorganisation branch does not track those files in its current tree. Existing remote history is preserved. The retained `.omp/config.yml` Hindsight backend remains a setup-review issue; publication of this separate branch does not merge or validate it.
