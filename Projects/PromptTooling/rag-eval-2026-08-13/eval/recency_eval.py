"""Second benchmark: does an UPDATED result outrank the one it replaced?

The 16-query set cannot answer this -- every gold note in it is under 58 days
old, so there are no stale/fresh pairs. Tuning recency against it therefore
only ever penalises recency, which is how a 400-day half-life looked "optimal".

This set is the complement: pairs of real notes about the same quantity where
one supersedes the other. Success = the CURRENT note ranks above the STALE one.

Reported alongside the topical benchmark, never instead of it -- a setting that
wins here by crushing topical accuracy is not an improvement.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAG = Path("/home/cgupta/obsidian-notes/scripts/rag")
sys.path.insert(0, str(RAG))
sys.path.insert(0, str(RAG / "vendor"))

import semantic_search as ss  # noqa: E402
import sources  # noqa: E402

VAULT = Path("/home/cgupta/obsidian-notes")
K = 60

# (query, current_note, stale_note) -- real pairs from the vault where the
# same quantity was revisited and the later note is the one you'd want.
PAIRS = [
    dict(
        q="what is the expected upper limit on the H+c signal strength",
        current="Projects/HToWW/strategy-2026-08-10/2026-08-11-card-rebuild-1160.md",
        stale="Projects/HToWW/lxplus-2026-06-17/bhive-docs/combine_findings_v11_v32.md",
    ),
    dict(
        q="current state of the combine card and what limit it gives",
        current="Projects/HToWW/strategy-2026-08-10/2026-08-11-action-items-to-finish.md",
        stale="Projects/HToWW/2026-06-17-LIMIT-ISSUE.md",
    ),
    dict(
        q="systematics list for the analysis",
        current="Projects/HToWW/2026-07-24-systematics-master-list.md",
        stale="Projects/HToWW/lxplus-2026-06-17/2026-06-17-systematics-reference.md",
    ),
    dict(
        q="how the MVA is trained and what inputs it uses",
        current="Projects/HToWW/leptonmva-2026-08-12/lepton-mva-onnx.md",
        stale="Projects/HToWW/lxplus-2026-06-17/bhive-docs/MVA.md",
    ),
]


def semantic_order(docs, qvec):
    scored = []
    for ident, e in docs.items():
        v = e.get("vecs") or []
        if not v:
            continue
        scored.append((max(ss.cosine(qvec, x) for x in v), ident))
    scored.sort(key=lambda t: -t[0])
    return scored


def keyword_order(query, limit=5):
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader("vs", str(RAG / "vault-search"))
    spec = importlib.util.spec_from_loader("vs", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    kw, _ = m.keyword_hits(VAULT, query, limit)
    return list(kw)


def ranked_ids(docs, sem, lex, half, floor, sup, now):
    sem_rank = {i: r for r, (_, i) in enumerate(sem)}
    lex_rank = {p: r for r, p in enumerate(lex)}
    idents = set(list(sem_rank)[:60]) | (set(lex_rank) & set(docs))
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
    return [i for _, i in out]


def evaluate(docs, orders, half, floor, sup, now):
    wins = 0
    detail = []
    for p in PAIRS:
        ids = ranked_ids(docs, orders[p["q"]][0], orders[p["q"]][1],
                         half, floor, sup, now)
        pos = {v: i for i, v in enumerate(ids)}
        c, s = pos.get(p["current"]), pos.get(p["stale"])
        ok = c is not None and (s is None or c < s)
        wins += ok
        detail.append((ok, c, s, p["q"][:44]))
    return wins / len(PAIRS), detail


def main():
    idx = json.loads((VAULT / ".vault-rag-index.json").read_text())
    docs = idx["docs"]
    now = time.time()
    missing = [n for p in PAIRS for n in (p["current"], p["stale"]) if n not in docs]
    if missing:
        print("NOT INDEXED:", *missing, sep="\n  ", file=sys.stderr)
    orders = {}
    for p in PAIRS:
        v = ss.embed(p["q"], model=idx.get("model"))
        orders[p["q"]] = (semantic_order(docs, v), keyword_order(p["q"]))

    print(f"{'half':>6}{'floor':>7}{'freshness-win':>15}")
    for half, floor in [(120, .35), (240, .50), (400, .65), (700, .35), (3000, .95)]:
        rate, _ = evaluate(docs, orders, half, floor, 0.55, now)
        print(f"{half:>6}{floor:>7.2f}{rate:>14.0%}")

    print("\ndetail at half=240 floor=0.50:")
    _, det = evaluate(docs, orders, 240, .50, 0.55, now)
    for ok, c, s, q in det:
        print(f"  {'OK ' if ok else 'MISS'}  current@{c}  stale@{s}   {q}")


if __name__ == "__main__":
    main()
