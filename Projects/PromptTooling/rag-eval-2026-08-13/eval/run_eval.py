"""Run the query set through both retrieval methods and record metrics.

Compares:
  grep          -- what Claude Code does without the RAG: ripgrep/grep the vault
  vault-search  -- the RAG (semantic + keyword, RRF fused)

Metrics per query:
  hit@k     did any gold note appear in the top k
  rr        reciprocal rank of the first gold note (0 if absent)
  latency   wall-clock seconds
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_queries import QUERIES  # noqa: E402

VAULT = Path("/home/cgupta/obsidian-notes")
SEARCH = VAULT / "scripts/rag/vault-search"
K = 5

STOP = {
    "the","a","an","and","or","but","if","of","to","in","on","for","with","how",
    "why","what","when","which","that","this","is","are","was","were","do","does",
    "did","i","my","me","it","its","from","at","by","as","be","been","can","could",
    "would","should","get","got","out","up","so","not","no","yes","we","you","did",
}


def grep_search(query: str, limit: int = K) -> tuple[list[str], float]:
    """Baseline: what an agent does with no index -- grep the vault for the
    query's content words, ranked by match count."""
    terms = [t for t in re.findall(r"[A-Za-z0-9_+-]{3,}", query.lower()) if t not in STOP]
    if not terms:
        return [], 0.0
    pattern = "|".join(re.escape(t) for t in terms)
    t0 = time.perf_counter()
    proc = subprocess.run(
        ["grep", "-rIic", "--include=*.md",
         "--exclude-dir=.git", "--exclude-dir=.obsidian", "--exclude-dir=__pycache__",
         "-E", "-e", pattern, "."],
        cwd=VAULT, capture_output=True, text=True,
    )
    dt = time.perf_counter() - t0
    hits = {}
    for line in proc.stdout.splitlines():
        p, _, c = line.rpartition(":")
        if p and c.isdigit() and int(c) > 0:
            hits[p.lstrip("./")] = int(c)
    ranked = [p for p, _ in sorted(hits.items(), key=lambda kv: -kv[1])]
    return ranked[:limit], dt


def rag_search(query: str, limit: int = K) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [str(SEARCH), "--limit", str(limit), "--paths-only", query],
        cwd=VAULT, capture_output=True, text=True,
    )
    dt = time.perf_counter() - t0
    return [l.strip() for l in proc.stdout.splitlines() if l.strip()], dt


def rr(results: list[str], gold: list[str]) -> float:
    for i, r in enumerate(results, 1):
        if r in gold:
            return 1.0 / i
    return 0.0


def main() -> int:
    rows = []
    for i, item in enumerate(QUERIES, 1):
        q, gold, kind = item["q"], item["gold"], item["kind"]
        g_res, g_dt = grep_search(q)
        r_res, r_dt = rag_search(q)
        row = dict(
            q=q, kind=kind, gold=gold,
            grep=dict(results=g_res, rr=rr(g_res, gold),
                      hit=int(any(x in gold for x in g_res)), dt=g_dt),
            rag=dict(results=r_res, rr=rr(r_res, gold),
                     hit=int(any(x in gold for x in r_res)), dt=r_dt),
        )
        rows.append(row)
        print(f"[{i:2}/{len(QUERIES)}] {kind:10} grep hit={row['grep']['hit']} "
              f"rr={row['grep']['rr']:.2f} | rag hit={row['rag']['hit']} "
              f"rr={row['rag']['rr']:.2f}  {q[:52]}", file=sys.stderr)

    out = Path(__file__).resolve().parent / "eval_results.json"
    out.write_text(json.dumps(rows, indent=2))

    def agg(rows, method, kind=None):
        sel = [r for r in rows if kind is None or r["kind"] == kind]
        if not sel:
            return 0.0, 0.0, 0.0
        hit = sum(r[method]["hit"] for r in sel) / len(sel)
        mrr = sum(r[method]["rr"] for r in sel) / len(sel)
        dt = sum(r[method]["dt"] for r in sel) / len(sel)
        return hit, mrr, dt

    print(f"\n{'':12} {'grep hit@5':>11} {'rag hit@5':>10} {'grep MRR':>9} {'rag MRR':>8}")
    for kind in ["paraphrase", "partial", "literal", None]:
        label = kind or "ALL"
        gh, gm, _ = agg(rows, "grep", kind)
        rh, rm, _ = agg(rows, "rag", kind)
        print(f"{label:12} {gh:>10.0%} {rh:>10.0%} {gm:>9.2f} {rm:>8.2f}")
    _, _, gdt = agg(rows, "grep")
    _, _, rdt = agg(rows, "rag")
    print(f"\nmean latency: grep {gdt*1000:.0f} ms | rag {rdt*1000:.0f} ms")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
