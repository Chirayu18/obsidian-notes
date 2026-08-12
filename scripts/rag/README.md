# vault-search — semantic + keyword search over notes, papers and code

Answers "where did I write about X" when you know the *meaning* but not the
wording. Complements `rg`, which stays better when you know the exact term.

```bash
scripts/rag/vault-search "why did the limit come out wrong"
scripts/rag/vault-search --tier code "how are condor jobs resubmitted"
scripts/rag/vault-search --paths-only --limit 3 "crab memory"
scripts/rag/refresh-index.sh --wait   # rebuild + prune, foreground
```

## Tiers

| Tier | Source | Weight |
|---|---|---|
| `notes` | vault markdown, recency-weighted | 1.0 |
| `papers` | `References/**.pdf` via `pdftotext` | 0.7 |
| `code` | lxplus analysis repos over the sshfs mount | 0.5 |

Tier weight multiplies the final score, so an equally-relevant note outranks a
code file — "latest notes first, code second" as a single blended ranking rather
than separate result lists. Recency decay is deliberately gentle (900-day
half-life, 0.70 floor): old notes drop below fresh ones but stay findable.

Code ids read `lxplus:higgscharm/runner.py`, which is
`~/mnt/lxplus/higgscharm/runner.py` locally and `~/higgscharm/runner.py` on lxplus.

## How it works

Two rankings, fused with Reciprocal Rank Fusion (RRF):

1. **Semantic** — every document is embedded with `bge-m3` via a local Ollama; the
   query is embedded into the same space and ranked by cosine similarity. Long
   documents are chunked and scored by best-matching chunk, so one relevant
   section surfaces a whole paper.
2. **Keyword** — a `grep`/`rg` pass over the query's content words.

RRF combines the two *rank orders* rather than their scores, which is what makes
fusing cosine values with match counts sound — the two aren't comparable. Tier
weight and recency are applied after fusion.

Why both: semantic alone reliably finds paraphrases ("event weights" → the
negweight notes) but tails off on short factual queries naming none of a note's
distinctive terms. Searching `blacklist` semantic-only returns index stubs;
with the keyword arm the three notes that actually discuss it lead.

## Freshness

`build_index.py` is incremental — it re-embeds changed files (mtime+size test,
which matters over sshfs) and **prunes entries whose source file is gone**.

`refresh-index.sh` is wired to the **SessionEnd** and **PreCompact** hooks. It
detaches the rebuild and returns in ~8ms, because SessionEnd has a 1.5s shared
budget that a real rebuild would blow. A `flock` keeps concurrent sessions from
embedding the same files twice; progress lands in `.vault-rag-index.log`.

Full rebuild is ~5 min for 375 docs / 2188 chunks; incremental is seconds.

## Upstream

The semantic core in `vendor/` is vendored from
[obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain)
(MIT — see `vendor/LICENSE.obsidian-second-brain`), pinned at commit `4d5b673`
(2026-08-08). Only the search files are taken:

- `vendor/semantic_search.py` — embedding, indexing, semantic + hybrid search
- `vendor/vault_ops.py` — shared skip-set (`_SKIP_DIRS`)

The upstream project is a 45-command note-writing framework; that half is
deliberately not installed. Zero third-party Python deps — stdlib plus HTTP to
Ollama.

**Local modification:** the `sys.path` shim in `semantic_search.py` was repointed,
since upstream keeps `vault_ops.py` under `integrations/obsidian-mcp-server/`
while here both files sit side by side. To update, re-copy both files and
re-apply that one-line change.

`vault-search` itself is local: vault-root resolution (works from any cwd,
`$OBSIDIAN_VAULT_PATH` to override), the grep arm, snippets, and `--no-archive`.

## Requirements

- **Ollama** running with `bge-m3` (`ollama pull bge-m3`, ~1.2GB).
- Without it, search degrades to keyword-only and warns on stderr — never
  hard-fails. This is the normal state on lxplus.

## Index

Written to `.obsidian-semantic-index.json` at the vault root (~8.5MB, gitignored,
regenerable). Rebuilds are incremental: unchanged notes reuse cached vectors
(~0.4s vs ~75s cold for 183 notes). The cache self-invalidates if the embedding
model changes, since vectors from different models aren't comparable.

Archive/ is indexed and tagged `[ARCHIVED]` in output; `--no-archive` hides it.
