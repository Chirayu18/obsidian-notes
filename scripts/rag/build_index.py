"""Build/refresh the multi-source index (notes + papers + code).

Separate from the vendored note index: this one carries a tier and mtime per
entry, chunks long documents, and prunes entries whose source file is gone.

    python3 scripts/rag/build_index.py            # incremental
    python3 scripts/rag/build_index.py --full     # ignore cache, re-embed all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import sources  # noqa: E402
import semantic_search as ss  # noqa: E402

INDEX_FILE = ".vault-rag-index.json"
FORMAT = 3  # bump when the stored shape changes, to force a clean rebuild
CHUNK_CHARS = 1200
MAX_CHUNKS = 12


def vault_root() -> Path:
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    return Path(env).expanduser().resolve() if env else HERE.parents[1]


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()[:16]


def chunk(text: str, size: int = CHUNK_CHARS, limit: int = MAX_CHUNKS) -> list[str]:
    """Split on paragraph boundaries, packing up to `size` chars per chunk.

    Embedding models cap out around 512 tokens; oversized input is silently
    truncated or errors, so long documents must be split and scored per chunk.
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    cur = ""
    for p in paras:
        if len(cur) + len(p) + 2 <= size:
            cur = f"{cur}\n\n{p}" if cur else p
        else:
            if cur:
                chunks.append(cur)
            # A single paragraph longer than `size` is hard-split.
            while len(p) > size:
                chunks.append(p[:size])
                p = p[size:]
            cur = p
        if len(chunks) >= limit:
            break
    if cur and len(chunks) < limit:
        chunks.append(cur)
    return chunks[:limit]


def _embed_doc(text: str, header: str) -> list[list[float]]:
    vecs = []
    for c in chunk(text):
        body = f"{header}\n\n{c}" if header else c
        try:
            v = ss.embed(body)
        except Exception:
            continue
        if v:
            vecs.append(v)
    return vecs


def collect(vault: Path) -> tuple[list[dict], list[str]]:
    """Enumerate every indexable source. Returns (docs, warnings)."""
    docs: list[dict] = []
    warnings: list[str] = []

    # --- notes ---------------------------------------------------------
    try:
        from vault_ops import _SKIP_DIRS as skip
    except ImportError:
        skip = {".git", ".obsidian", "node_modules", "__pycache__"}
    for md in sorted(vault.rglob("*.md")):
        rel = md.relative_to(vault).as_posix()
        if any(part in skip for part in md.relative_to(vault).parts[:-1]):
            continue
        if rel.startswith("scripts/rag/"):
            continue  # our own docs are noise in results
        docs.append({"id": rel, "tier": "notes", "path": str(md)})

    # --- papers --------------------------------------------------------
    for pdf in sources.iter_pdfs(vault):
        docs.append({
            "id": pdf.relative_to(vault).as_posix(),
            "tier": "papers", "path": str(pdf),
        })

    # --- code ----------------------------------------------------------
    roots, note = sources.code_roots_available()
    if note:
        warnings.append(note)
    for f in sources.iter_code_files(roots):
        # Code lives outside the vault, so the id is an absolute-ish marker
        # that still reads sensibly in results.
        try:
            rel = f.relative_to(Path(os.environ.get("LXPLUS_MOUNT", "~/mnt/lxplus")).expanduser())
            ident = f"lxplus:{rel.as_posix()}"
        except ValueError:
            ident = f"code:{f.as_posix()}"
        docs.append({"id": ident, "tier": "code", "path": str(f)})

    return docs, warnings


def build(vault: Path, full: bool = False, verbose: bool = True) -> dict:
    index_path = vault / INDEX_FILE
    cache: dict = {}
    if index_path.exists() and not full:
        try:
            cache = json.loads(index_path.read_text())
        except Exception:
            cache = {}
    # Vectors from a different model live in a different space; mixing them
    # would make every similarity meaningless.
    reusable = (
        cache.get("format") == FORMAT and cache.get("model") == ss.EMBED_MODEL
    )
    old = cache.get("docs", {}) if reusable else {}

    docs, warnings = collect(vault)
    new: dict = {}
    embedded = reused = failed = 0

    for d in docs:
        p = Path(d["path"])
        try:
            st = p.stat()
        except OSError:
            continue
        prev = old.get(d["id"])
        # mtime+size is the cheap change test; over sshfs it avoids reading
        # every code file on every run.
        sig = f"{int(st.st_mtime)}:{st.st_size}"
        if prev and prev.get("sig") == sig and prev.get("vecs"):
            entry = dict(prev)
            entry["mtime"] = st.st_mtime
            new[d["id"]] = entry
            reused += 1
            continue

        if d["tier"] == "papers":
            text = sources.extract_pdf_text(p)
        else:
            text = sources.read_code(p)
        if not text.strip():
            failed += 1
            continue

        header = f"{d['tier']}: {d['id']}"
        vecs = _embed_doc(text, header)
        if not vecs:
            failed += 1
            continue
        new[d["id"]] = {
            "tier": d["tier"], "path": d["path"], "sig": sig,
            "mtime": st.st_mtime, "vecs": vecs, "hash": _hash(text),
            "title": p.stem,
        }
        embedded += 1
        if verbose and embedded % 25 == 0:
            print(f"  embedded {embedded}...", file=sys.stderr)

    pruned = len(old) - sum(1 for k in old if k in new)
    out = {
        "format": FORMAT, "model": ss.EMBED_MODEL,
        "built": time.time(), "docs": new,
    }
    index_path.write_text(json.dumps(out), encoding="utf-8")

    if verbose:
        by_tier: dict[str, int] = {}
        for e in new.values():
            by_tier[e["tier"]] = by_tier.get(e["tier"], 0) + 1
        tiers = ", ".join(f"{k} {v}" for k, v in sorted(by_tier.items()))
        print(
            f"[rag] {len(new)} docs ({tiers}) -- {embedded} embedded, "
            f"{reused} cached, {pruned} pruned, {failed} empty/skipped",
            file=sys.stderr,
        )
        for w in warnings:
            print(f"[rag] {w}", file=sys.stderr)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build the multi-source RAG index")
    ap.add_argument("--full", action="store_true", help="Ignore cache, re-embed everything")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    vault = vault_root()
    if not ss.ollama_available():
        print(
            f"[rag] no embedding backend at {ss.OLLAMA_URL} -- cannot build. "
            f"Start Ollama, then: ollama pull {ss.EMBED_MODEL}",
            file=sys.stderr,
        )
        return 3
    build(vault, full=args.full, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
