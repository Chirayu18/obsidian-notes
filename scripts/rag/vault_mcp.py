#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.2,<2"]
# ///
"""MCP server exposing the Obsidian vault to any agent harness (omp, Claude Code, Codex).

Tools:
  search_notes(query, limit, tier, include_archive)  hybrid search (bge-m3 + BM25, RRF,
                                                      tier weights, recency, superseded demotion)
  read_note(path)                                     full text of one vault note
  related_decisions(topic)                            notes recording decisions/corrections on a topic
  propose_memory_update(title, content, task_id)      writes a PROPOSAL under Proposals/ for the
                                                      user to accept; never edits existing notes

"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", HERE.parents[1])).resolve()
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))
vs = SourceFileLoader("vault_search", str(HERE / "vault-search")).load_module()

READABLE = {".md", ".txt"}


def _safe_path(path: str) -> Path:
    p = (VAULT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if VAULT not in p.parents and p != VAULT:
        raise ValueError("path is outside the vault")
    if p.suffix not in READABLE:
        raise ValueError("only .md and .txt notes can be read")
    return p


mcp = FastMCP("vault")


@mcp.tool()
def search_notes(query: str, limit: int = 8, tier: str | None = None, include_archive: bool = False) -> list[dict]:
    """Search the user's Obsidian research vault (notes, decisions, investigations, papers, code).

    Use before answering questions about past work, decisions, pipelines or results.
    tier: "notes", "papers" or "code" to restrict; default searches all, notes ranked first.
    Results carry status (e.g. superseded) so stale conclusions are not mistaken for current.
    """
    tiers = [tier] if tier else None
    res, err = vs.search_multi(VAULT, query, max(limit * 3, 20), tiers, no_archive=not include_archive)
    if err:  # no Ollama / no index: BM25 alone over notes
        hits, _ = vs.keyword_hits(VAULT, query, limit * 3)
        res = [{"id": rel, "tier": "notes", "score": s, "status": "", "superseded_by": ""} for rel, s in hits.items()]
    out = []
    for r in res:
        rel = r["id"]
        p = VAULT / rel
        text = p.suffix in READABLE and p.exists()
        out.append({"path": rel, "tier": r.get("tier"), "status": r.get("status") or "active",
                    "superseded_by": r.get("superseded_by") or "",
                    "snippet": vs.snippet(VAULT, rel, query) if text else ""})
        if len(out) >= limit:
            break
    return out


@mcp.tool()
def read_note(path: str) -> str:
    """Return the full text of one vault note (path relative to the vault root)."""
    return _safe_path(path).read_text(errors="replace")


@mcp.tool()
def related_decisions(topic: str, limit: int = 6) -> list[dict]:
    """Find notes recording decisions, corrections or final choices about a topic."""
    hits = search_notes(f"{topic} decision chosen final why", limit=limit * 3, tier="notes")
    keep = [h for h in hits if "path" in h and re.search(
        r"decision|decided|final|chosen|correction|superseded|plan", h["path"] + " " + h.get("snippet", ""), re.I)]
    return keep[:limit] or hits[:limit]


@mcp.tool()
def propose_memory_update(title: str, content: str, task_id: str = "") -> str:
    """Propose a durable note (a decision, result or lesson) for the user to approve.

    Writes Proposals/YYYY-MM-DD-<slug>.md with status: proposed. Never edits existing notes;
    the user accepts a proposal by moving it into a project folder.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "proposal"
    day = dt.date.today().isoformat()
    d = VAULT / "Proposals"
    d.mkdir(exist_ok=True)
    p = d / f"{day}-{slug}.md"
    i = 2
    while p.exists():
        p = d / f"{day}-{slug}-{i}.md"
        i += 1
    p.write_text(f"---\ntags: [proposal]\nstatus: proposed\ndate: {day}\nsource: agent\n"
                 f"task: {task_id or os.environ.get('AI_ORCH_TASK', '')}\n---\n\n# {title}\n\n{content.strip()}\n")
    return f"proposed: {p.relative_to(VAULT)} (awaiting the user's approval)"


if __name__ == "__main__":
    mcp.run()
