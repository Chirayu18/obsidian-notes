"""Agent-realistic benchmark: what it costs ME to find a note, with vs without RAG.

The retrieval-metrics comparison (hit@5) is not the real alternative. Without
the RAG I do not run one grep -- I run a *search loop*: guess a term, grep, read
a candidate, guess again. Each step costs a tool call and, when I read a file,
tokens of context.

This simulates that loop:

  no-RAG:   grep for content words -> if no hit, drop to the rarest single term
            -> read top candidates in rank order until the gold note is opened.
            Cost = tool calls + bytes of every file read along the way.

  RAG:      one vault-search call -> read candidates in rank order.
            Cost = 1 tool call + bytes read.

Cost model: a tool call is a round trip; bytes read become context tokens
(~4 bytes/token). Both are counted, neither is estimated away.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_queries import QUERIES  # noqa: E402

VAULT = Path("/home/cgupta/obsidian-notes")
SEARCH = VAULT / "scripts/rag/vault-search"
BYTES_PER_TOKEN = 4.0
MAX_READS = 4          # I give up and ask the user after ~4 wrong files
CANDIDATES = 5

STOP = {
    "the","a","an","and","or","but","if","of","to","in","on","for","with","how",
    "why","what","when","which","that","this","is","are","was","were","do","does",
    "did","i","my","me","it","its","from","at","by","as","be","been","can","could",
    "would","should","get","got","out","up","so","not","no","yes","we","you",
    "did","much","many","things","order","run","come","came","look","looked",
}


def terms_of(q: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9_+-]{3,}", q.lower()) if t not in STOP]


def grep_rank(pattern: str) -> list[str]:
    proc = subprocess.run(
        ["grep", "-rIic", "--include=*.md",
         "--exclude-dir=.git", "--exclude-dir=.obsidian", "--exclude-dir=__pycache__",
         "-E", "-e", pattern, "."],
        cwd=VAULT, capture_output=True, text=True,
    )
    hits = {}
    for line in proc.stdout.splitlines():
        p, _, c = line.rpartition(":")
        if p and c.isdigit() and int(c) > 0:
            hits[p.lstrip("./")] = int(c)
    return [p for p, _ in sorted(hits.items(), key=lambda kv: -kv[1])]


def size_of(rel: str) -> int:
    try:
        return (VAULT / rel).stat().st_size
    except OSError:
        return 0


def simulate_no_rag(query: str, gold: list[str]) -> dict:
    """Grep-and-read loop, the way an agent without an index actually works."""
    calls, read_bytes, reads = 0, 0, []
    ts = terms_of(query)
    if not ts:
        return dict(found=False, calls=0, read_bytes=0, reads=[], gave_up=True)

    # Attempt 1: all content words OR'd -- the natural first grep.
    calls += 1
    ranked = grep_rank("|".join(re.escape(t) for t in ts))

    # Attempt 2: no usable result, so narrow to the most distinctive term
    # (longest word is a decent proxy for rarest).
    if not ranked:
        calls += 1
        ranked = grep_rank(re.escape(max(ts, key=len)))

    for rel in ranked[:MAX_READS]:
        calls += 1                      # a Read is its own tool call
        read_bytes += size_of(rel)
        reads.append(rel)
        if rel in gold:
            return dict(found=True, calls=calls, read_bytes=read_bytes,
                        reads=reads, gave_up=False)
    return dict(found=False, calls=calls, read_bytes=read_bytes,
                reads=reads, gave_up=True)


def simulate_rag(query: str, gold: list[str]) -> dict:
    calls, read_bytes, reads = 1, 0, []
    proc = subprocess.run(
        [str(SEARCH), "--limit", str(CANDIDATES), "--paths-only", query],
        cwd=VAULT, capture_output=True, text=True,
    )
    ranked = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
    for rel in ranked[:MAX_READS]:
        if rel.startswith("lxplus:") or rel.endswith(".pdf"):
            continue
        calls += 1
        read_bytes += size_of(rel)
        reads.append(rel)
        if rel in gold:
            return dict(found=True, calls=calls, read_bytes=read_bytes,
                        reads=reads, gave_up=False)
    return dict(found=False, calls=calls, read_bytes=read_bytes,
                reads=reads, gave_up=True)


def main() -> int:
    rows = []
    for i, item in enumerate(QUERIES, 1):
        q, gold, kind = item["q"], item["gold"], item["kind"]
        a = simulate_no_rag(q, gold)
        b = simulate_rag(q, gold)
        rows.append(dict(q=q, kind=kind, gold=gold, norag=a, rag=b))
        print(f"[{i:2}/{len(QUERIES)}] {kind:10} "
              f"no-RAG: {a['calls']} calls {a['read_bytes']/1024:6.1f}KB "
              f"{'OK ' if a['found'] else 'MISS'} | "
              f"RAG: {b['calls']} calls {b['read_bytes']/1024:6.1f}KB "
              f"{'OK ' if b['found'] else 'MISS'}", file=sys.stderr)

    out = Path(__file__).resolve().parent / "agent_results.json"
    out.write_text(json.dumps(rows, indent=2))

    n = len(rows)
    def s(m, f): return sum(r[m][f] for r in rows)
    print(f"\n{'':10} {'solved':>8} {'tool calls':>11} {'context read':>14}")
    for m, label in (("norag", "no RAG"), ("rag", "RAG")):
        solved = sum(r[m]["found"] for r in rows)
        kb = s(m, "read_bytes") / 1024
        tok = s(m, "read_bytes") / BYTES_PER_TOKEN
        print(f"{label:10} {solved:>4}/{n:<3} {s(m,'calls'):>11} "
              f"{kb:>8.0f} KB ~{tok/1000:.0f}k tok")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
