"""BM25 keyword arm for vault-search.

Replaces the ripgrep match-count arm with Okapi BM25 (k1=1.2, b=0.75), the same
ranking function combine-mcp uses through rank_bm25, written in stdlib so it also
runs on lxplus where there is no Ollama and no extra packages.

Two choices tuned for this vault:
  * fields: the file name and the first H1 count 3x, other headings 2x, body 1x,
    because names are chosen and prose is incidental (the reason the old arm
    boosted filename matches);
  * code-aware tokens: an identifier such as make_combine_inputs or ctag2d.py is
    kept whole AND split into its parts, so both "make_combine_inputs" and
    "combine inputs" find it.

The token statistics are cached in .vault-bm25-cache.json (gitignored), keyed by
path and mtime, so only changed notes are re-tokenised.
"""
from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path

CACHE_FILE = ".vault-bm25-cache.json"
K1, B = 1.2, 0.75
FIELD_WEIGHT = {"title": 3.0, "heading": 2.0, "body": 1.0}
STOP = {
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "for", "with",
    "how", "why", "what", "when", "which", "that", "this", "is", "are", "was", "were",
    "do", "does", "did", "i", "my", "me", "it", "its", "from", "at", "by", "as", "be",
    "been", "can", "could", "would", "should", "get", "got", "out", "up", "so", "not",
    "no", "yes", "we", "you", "there", "then", "than", "into", "also", "only", "all",
}
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+-]*[A-Za-z0-9+]|[A-Za-z0-9]")


def tokenize(text: str) -> list[str]:
    out = []
    for raw in _IDENT.findall(text.lower()):
        parts = [p for p in re.split(r"[_.\-]+", raw) if p]
        if len(parts) > 1 and len(raw) <= 60:
            out.append(raw)  # whole identifier
        for p in parts:
            if len(p) >= 2 and p not in STOP:
                out.append(p)
    return out


def _fields(path: Path, text: str) -> Counter:
    """Weighted term frequencies for one note."""
    tf: Counter = Counter()
    stem = path.stem.replace("-", " ").replace("_", " ")
    for t in tokenize(stem):
        tf[t] += FIELD_WEIGHT["title"]
    body_lines = []
    for line in text.splitlines():
        if line.startswith("# "):
            w = FIELD_WEIGHT["title"]
        elif line.startswith("#"):
            w = FIELD_WEIGHT["heading"]
        else:
            body_lines.append(line)
            continue
        for t in tokenize(line.lstrip("#")):
            tf[t] += w
    for t in tokenize("\n".join(body_lines)):
        tf[t] += FIELD_WEIGHT["body"]
    return tf


def _iter_notes(vault: Path, skip: set[str]):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d.lower() not in skip and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                yield Path(root) / f


class Index:
    def __init__(self, vault: Path):
        self.vault = vault
        try:
            from vault_ops import _SKIP_DIRS as skip
        except ImportError:
            skip = {".git", ".obsidian", "node_modules", "__pycache__"}
        self.skip = {s.lower() for s in skip}
        cache_path = vault / CACHE_FILE
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}
        docs, changed = {}, False
        for p in _iter_notes(vault, self.skip):
            rel = str(p.relative_to(vault))
            try:
                mtime = p.stat().st_mtime
            except OSError:
                continue
            hit = cache.get(rel)
            if hit and hit["mtime"] == mtime:
                docs[rel] = hit
                continue
            try:
                text = p.read_text(errors="replace")
            except OSError:
                continue
            tf = _fields(p, text)
            docs[rel] = {"mtime": mtime, "tf": dict(tf), "len": sum(tf.values())}
            changed = True
        if changed or len(docs) != len(cache):
            try:
                tmp = cache_path.with_suffix(".tmp")
                tmp.write_text(json.dumps(docs))
                tmp.replace(cache_path)
            except OSError:
                pass  # read-only vault: still works, just without a cache
        self.docs = docs
        self.n = len(docs)
        self.avgdl = sum(d["len"] for d in docs.values()) / max(1, self.n)
        df: Counter = Counter()
        for d in docs.values():
            df.update(d["tf"].keys())
        self.idf = {t: math.log(1 + (self.n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def search(self, query: str, limit: int = 40) -> dict[str, float]:
        terms = [t for t in dict.fromkeys(tokenize(query)) if t in self.idf]
        if not terms:
            return {}
        scores: dict[str, float] = {}
        for rel, d in self.docs.items():
            tf, dl = d["tf"], d["len"]
            s = 0.0
            for t in terms:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / self.avgdl))
            if s > 0:
                scores[rel] = s
        return dict(sorted(scores.items(), key=lambda kv: -kv[1])[:limit])


_cached: dict[str, Index] = {}


def bm25_hits(vault: Path, query: str, limit: int) -> tuple[dict[str, float], str]:
    """Same contract as vault-search keyword_hits: ({relpath: score}, error)."""
    try:
        key = str(vault)
        if key not in _cached:
            _cached[key] = Index(vault)
        return _cached[key].search(query, limit * 4), ""
    except Exception as exc:  # never break search; caller falls back
        return {}, f"bm25 failed: {exc}"
