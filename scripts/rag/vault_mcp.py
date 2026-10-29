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

Data-class filter: when launched by the `ai` orchestrator, AI_ORCH_CLASS is inherited.
  restricted -> everything is visible (the model is CERN-hosted or local)
  cms        -> notes matching the restricted patterns are withheld
  public     -> notes matching restricted OR CMS patterns are withheld (the model may be NIM)
Without AI_ORCH_CLASS (a plain Claude Code session) the class defaults to "cms".
Patterns come from ~/ai-orchestrator/config.toml and the private patterns file it names.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tomllib
from importlib.machinery import SourceFileLoader
from pathlib import Path

from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", HERE.parents[1])).resolve()
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))
vs = SourceFileLoader("vault_search", str(HERE / "vault-search")).load_module()

ORCH_CONFIG = Path(os.environ.get("AI_ORCH_CONFIG", Path.home() / "ai-orchestrator/config.toml"))
CLASS = os.environ.get("AI_ORCH_CLASS", "cms")
READABLE = {".md", ".txt"}


def _patterns() -> dict[str, tuple[list[str], list[str]]]:
    """{class: (content_patterns, path_patterns)} for restricted and cms."""
    out = {"restricted": ([], []), "cms": ([], [])}
    try:
        cfg = tomllib.loads(ORCH_CONFIG.read_text())
    except Exception:
        return out
    for cls in out:
        rules = cfg.get("policy", {}).get(cls, {})
        content = list(rules.get("prompt_patterns", []))
        pf = rules.get("prompt_patterns_file")
        if pf and Path(pf).expanduser().exists():
            content += [l.strip() for l in Path(pf).expanduser().read_text().splitlines()
                        if l.strip() and not l.startswith("#")]
        out[cls] = (content, list(rules.get("path_patterns", [])))
    return out


PATTERNS = _patterns()


def note_class(rel: str, text: str) -> str:
    """Strictest class a note belongs to: frontmatter `sensitivity:` wins, then patterns."""
    m = re.search(r"^sensitivity:\s*(\S+)", text[:2000], re.MULTILINE)
    if m:
        v = m.group(1).strip("'\"").lower()
        if v in ("restricted", "private", "cms-restricted"):
            return "restricted"
        if v in ("cms", "cms-internal", "internal"):
            return "cms"
        if v == "public":
            return "public"
    for cls in ("restricted", "cms"):
        content, paths = PATTERNS[cls]
        if any(re.search(p, rel) for p in paths) or any(re.search(p, text, re.IGNORECASE) for p in content):
            return cls
    return "public"


def visible(rel: str, text: str) -> bool:
    order = ["restricted", "cms", "public"]
    return order.index(note_class(rel, text)) >= order.index(CLASS)


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
    out, withheld = [], 0
    for r in res:
        rel = r["id"]
        p = VAULT / rel
        text = p.read_text(errors="replace") if p.suffix in READABLE and p.exists() else ""
        if text and not visible(rel, text):
            withheld += 1
            continue
        out.append({"path": rel, "tier": r.get("tier"), "status": r.get("status") or "active",
                    "superseded_by": r.get("superseded_by") or "",
                    "snippet": vs.snippet(VAULT, rel, query) if text else ""})
        if len(out) >= limit:
            break
    if withheld:
        out.append({"note": f"{withheld} result(s) withheld for data class '{CLASS}'"})
    return out


@mcp.tool()
def read_note(path: str) -> str:
    """Return the full text of one vault note (path relative to the vault root)."""
    p = _safe_path(path)
    text = p.read_text(errors="replace")
    rel = str(p.relative_to(VAULT))
    if not visible(rel, text):
        return f"[withheld: '{rel}' is above data class '{CLASS}' for this session]"
    return text


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
