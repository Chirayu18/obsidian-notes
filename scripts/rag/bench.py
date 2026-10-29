#!/usr/bin/env python3
"""Benchmark the vault-search keyword arms on the labelled query set.

Uses the 16 queries with ground truth from Projects/PromptTooling/rag-eval-2026-08-13
(paraphrase / partial / literal) and reports recall@5 and MRR for:
  rg, bm25           keyword arm alone
  hybrid+rg          today's ranking (semantic + rg, RRF)
  hybrid+bm25        semantic + BM25, RRF
Gold notes that no longer exist are dropped and reported.

    python3 scripts/rag/bench.py [--k 5]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))
vs = SourceFileLoader("vault_search", str(HERE / "vault-search")).load_module()
spec = importlib.util.spec_from_file_location(
    "eval_queries", VAULT / "Projects/PromptTooling/rag-eval-2026-08-13/eval/eval_queries.py")
eq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eq)


def ranked(arm: str, mode: str, q: str, k: int) -> list[str]:
    vs.KEYWORD_ARM = arm
    if mode == "kw":
        hits, _ = vs.keyword_hits(VAULT, q, k)
        return list(hits)[:k]
    # All tiers: with a single tier search_multi sorts by raw similarity and the
    # keyword arm would not affect the order. Keep notes, in fused-score order.
    res, err = vs.search_multi(VAULT, q, k * 6, None, no_archive=True)
    if err:
        sys.exit(f"hybrid search unavailable: {err}")
    return [r["id"] for r in res if r["tier"] == "notes"][:k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()
    queries = []
    for item in eq.QUERIES:
        q = item["q"] if isinstance(item, dict) else item.q
        gold = item["gold"] if isinstance(item, dict) else item.gold
        kind = item.get("kind", "") if isinstance(item, dict) else getattr(item, "kind", "")
        live = [g for g in gold if (VAULT / g).exists()]
        if len(live) < len(gold):
            print(f"[dropped missing gold] {set(gold) - set(live)}")
        if live:
            queries.append((q, set(live), kind))
    print(f"{len(queries)} queries, k={a.k}\n")
    arms = [("rg", "kw"), ("bm25", "kw"), ("rg", "hybrid"), ("bm25", "hybrid")]
    print(f"{'arm':<14}{'recall@k':>10}{'MRR':>8}   by kind (recall@k)")
    for arm, mode in arms:
        rec, mrr, by = 0.0, 0.0, {}
        for q, gold, kind in queries:
            r = ranked(arm, mode, q, a.k)
            hit = any(p in gold for p in r)
            rr = next((1 / (i + 1) for i, p in enumerate(r) if p in gold), 0.0)
            rec += hit
            mrr += rr
            by.setdefault(kind, []).append(hit)
        n = len(queries)
        kinds = "  ".join(f"{k}:{sum(v)}/{len(v)}" for k, v in sorted(by.items()))
        name = arm if mode == "kw" else f"hybrid+{arm}"
        print(f"{name:<14}{rec / n:>10.2f}{mrr / n:>8.2f}   {kinds}")


if __name__ == "__main__":
    main()
