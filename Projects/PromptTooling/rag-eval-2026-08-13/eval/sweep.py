"""Sweep recency half-life / floor against the query set.

Tuning on the same 16 queries I report on risks overfitting, so this reports
the whole surface rather than picking the argmax: a setting is only worth
taking if it sits on a broad plateau, not a spike.

Reuses the cached index; only the ranking parameters change, so no re-embedding.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAG = Path("/home/cgupta/obsidian-notes/scripts/rag")
sys.path.insert(0, str(RAG))
sys.path.insert(0, str(RAG / "vendor"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import semantic_search as ss  # noqa: E402
import sources  # noqa: E402
from eval_queries import QUERIES  # noqa: E402

VAULT = Path("/home/cgupta/obsidian-notes")
K = 60
TOPK = 5


def load():
    idx = json.loads((VAULT / ".vault-rag-index.json").read_text())
    return idx, idx["docs"]


def embed_queries(idx):
    """Embed once; the sweep only changes ranking parameters."""
    out = {}
    for item in QUERIES:
        out[item["q"]] = ss.embed(item["q"], model=idx.get("model"))
    return out


def semantic_order(docs, qvec):
    scored = []
    for ident, e in docs.items():
        vecs = e.get("vecs") or []
        if not vecs:
            continue
        scored.append((max(ss.cosine(qvec, v) for v in vecs), ident))
    scored.sort(key=lambda t: -t[0])
    return scored


def keyword_order(query):
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader("vs", str(RAG / "vault-search"))
    spec = importlib.util.spec_from_loader("vs", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    kw, _ = m.keyword_hits(VAULT, query, TOPK)
    return list(kw)


def rank(docs, sem, lex, half, floor, sup, now):
    sem_rank = {i: r for r, (_, i) in enumerate(sem)}
    lex_rank = {p: r for r, p in enumerate(lex)}
    idents = set(list(sem_rank)[:40]) | (set(lex_rank) & set(docs))
    out = []
    for ident in idents:
        e = docs[ident]
        rrf = 0.0
        if ident in sem_rank:
            rrf += 1.0 / (K + sem_rank[ident])
        if ident in lex_rank:
            rrf += 1.0 / (K + lex_rank[ident])
        stamp = e.get("date") or e.get("mtime") or now
        age = max(0.0, (now - stamp) / 86400.0)
        rec = floor + (1.0 - floor) * (0.5 ** (age / half))
        if e.get("status") == "superseded":
            rec *= sup
        w = sources.TIER_WEIGHT.get(e.get("tier", "notes"), 0.5)
        out.append((rrf * w * rec, ident))
    out.sort(key=lambda t: -t[0])
    return [i for _, i in out[:TOPK]]


def score(docs, qvecs, lexes, half, floor, sup, now):
    hit = mrr = 0.0
    for item in QUERIES:
        res = rank(docs, qvecs[item["q"]], lexes[item["q"]], half, floor, sup, now)
        gold = set(item["gold"])
        if any(r in gold for r in res):
            hit += 1
        for i, r in enumerate(res, 1):
            if r in gold:
                mrr += 1.0 / i
                break
    n = len(QUERIES)
    return hit / n, mrr / n


def main():
    idx, docs = load()
    now = time.time()
    print("embedding queries...", file=sys.stderr)
    # Precompute the semantic ORDER once per query -- the sweep only varies
    # ranking parameters, so cosine work never needs repeating.
    qvecs = {}
    for item in QUERIES:
        v = ss.embed(item["q"], model=idx.get("model"))
        qvecs[item["q"]] = semantic_order(docs, v)
    lexes = {item["q"]: keyword_order(item["q"]) for item in QUERIES}

    halves = [60, 120, 240, 400, 700, 1200, 3000]
    floors = [0.20, 0.35, 0.50, 0.65, 0.80, 0.95]
    print(f"\n{'half-life':>10} " + " ".join(f"{f:>11.2f}" for f in floors))
    print(" " * 10 + " ".join(f"{'hit/MRR':>11}" for _ in floors))
    best = []
    for h in halves:
        cells = []
        for f in floors:
            hit, mrr = score(docs, qvecs, lexes, h, f, 0.55, now)
            cells.append(f"{hit:.2f}/{mrr:.2f}")
            best.append((mrr, hit, h, f))
        print(f"{h:>10} " + " ".join(f"{c:>11}" for c in cells))

    best.sort(reverse=True)
    print("\ntop 6 by MRR:")
    for mrr, hit, h, f in best[:6]:
        print(f"  half={h:>5}  floor={f:.2f}  hit@5={hit:.2f}  MRR={mrr:.3f}")


if __name__ == "__main__":
    main()
