"""Source registry: what gets indexed, at what priority, and how it's read.

Three tiers, searched together but ranked by priority so recent notes win ties:

  notes  (1.0) -- the vault's own markdown. Recency-weighted.
  papers (0.7) -- PDFs under References/, text extracted via pdftotext.
  code   (0.5) -- lxplus analysis repos, read over the sshfs mount.

Priority multiplies the fused score, so a note and a code file of equal
relevance rank note-first, which is what "latest notes indexed first" means
in a single blended ranking.
"""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

# --- tier weights -----------------------------------------------------------
TIER_WEIGHT = {"notes": 1.0, "papers": 0.7, "code": 0.5}

# Recency. Tuned by sweeping half-life x floor against the 16-query topical
# benchmark (scripts live in Projects/PromptTooling/rag-eval-2026-08-13/eval/).
# 240/0.50 sits in the interior of a broad plateau at hit@5 0.94 / MRR ~0.74;
# the previous 120/0.35 sat on the steep edge and cost 0.16 MRR by pushing
# correct-but-older notes down.
#
# Deliberately NOT more aggressive. A separate benchmark (recency_eval.py) shows
# recency cannot fix a stale-outranks-current case at ANY setting: when the old
# note is the better topical match it wins by ~50 ranks, and a multiplier on RRF
# scores cannot close that. Marking the old note `status: superseded` is what
# fixes it -- see SUPERSEDED_PENALTY. Recency is a tiebreak, not a truth signal.
RECENCY_HALFLIFE_DAYS = 240.0
RECENCY_FLOOR = 0.50

# A note explicitly marked superseded is not merely old -- it has been replaced.
# Age cannot express that: a June limit number is stale while a June methodology
# note is still authoritative. This is the only signal that distinguishes them.
#
# 0.55, not lower: RRF scores sit in a narrow band, so a harsher penalty does
# not demote a superseded note, it erases it (measured: 0.25 pushed a verbatim
# text match below rank 25). Demoted-but-reachable is the goal -- results are
# tagged [SUPERSEDED -> successor], so a stale conclusion cannot be misread as
# current even when it legitimately ranks.
SUPERSEDED_PENALTY = 0.55

CODE_EXTS = {".py", ".cc", ".h", ".C", ".cpp", ".sh", ".yaml", ".yml", ".json", ".cfg", ".md"}

# Directories never worth indexing: build output, caches, VCS internals, and
# the large generated payloads that live alongside analysis code.
CODE_SKIP_DIRS = {
    ".git", "__pycache__", ".cache", "node_modules", ".ipynb_checkpoints",
    "build", "dist", ".eggs", "venv", ".venv", "site-packages",
    "condor_logs", "logs", "log", "outputs", "output", "plots", "figures",
    # Per-dataset condor job trees: partitions.json is a generated list of
    # XRootD paths, and the .sub/.sh beside it are templated per dataset.
    "condor", "out", "img",
}
# Generated/vendored files that add noise without adding recall.
CODE_SKIP_RE = re.compile(
    r"(^|/)(setup\.py|conftest\.py)$|\.min\.(js|css)$|_pb2\.py$"
    # Generated data, not source: job-splitting output, correctionlib tables,
    # dataset dumps. Embedding these buries real code under XRootD URLs and
    # float arrays, and they churn constantly so they force re-embedding.
    r"|(^|/)partitions?[_.][^/]*\.json$"
    r"|(^|/)partitions\.json$"
    r"|(^|/)analysis/data/.*\.json$"
    r"|(^|/)(dataset_discovery|fileset)[^/]*\.json$"
    r"|(^|/)filesets/.*\.json$"
    r"|(^|/)\.sites_map\.json$"
)

MAX_CODE_BYTES = 400_000   # skip generated blobs masquerading as source
MAX_PDF_CHARS = 120_000    # ~40 pages of prose; enough for an analysis note


def _lxplus_code_roots() -> list[Path]:
    """lxplus analysis dirs, reached over the sshfs mount.

    Ollama runs on the laptop, so code must be read through the mount rather
    than indexed on lxplus itself. Overridable via VAULT_CODE_ROOTS
    (colon-separated) for testing or when the mount moves.
    """
    env = os.environ.get("VAULT_CODE_ROOTS")
    if env:
        return [Path(p).expanduser() for p in env.split(":") if p.strip()]
    mount = Path(os.environ.get("LXPLUS_MOUNT", "~/mnt/lxplus")).expanduser()
    names = ["higgscharm", "flashjet_condor", "negrw_condor", "Codes",
             "negrw_model", "leptonmva_model"]
    return [mount / n for n in names]


def code_roots_available() -> tuple[list[Path], str]:
    """Reachable code roots, plus a note about what was skipped.

    A dead sshfs mount must degrade to "no code indexed", never to a hang or
    a wiped code tier -- stat() on a stale mount can block, so we probe the
    mount point once rather than walking into it blindly.
    """
    roots = _lxplus_code_roots()
    if not roots:
        return [], ""
    mount = Path(os.environ.get("LXPLUS_MOUNT", "~/mnt/lxplus")).expanduser()
    if not os.environ.get("VAULT_CODE_ROOTS"):
        try:
            if subprocess.run(["mountpoint", "-q", str(mount)], timeout=10).returncode != 0:
                return [], f"lxplus mount not active at {mount} -- code tier skipped"
        except (subprocess.SubprocessError, OSError):
            return [], f"could not probe {mount} -- code tier skipped"
    # is_dir() is not enough: a dead sshfs connection still answers as a
    # mountpoint, and its children raise EACCES/EIO. Probing readability is what
    # distinguishes "mount is up" from "mount is a corpse" -- and getting this
    # wrong silently PRUNED all 105 code docs, because unreadable reads exactly
    # like deleted to the incremental indexer.
    live, missing, unreadable = [], [], []
    for r in roots:
        if not r.is_dir():
            missing.append(r.name)
            continue
        try:
            next(iter(os.scandir(r)), None)
        except OSError:
            unreadable.append(r.name)
            continue
        live.append(r)
    notes = []
    if missing:
        notes.append(f"missing code roots: {', '.join(missing)}")
    if unreadable:
        notes.append(f"UNREADABLE code roots (stale mount?): {', '.join(unreadable)}")
    return live, "; ".join(notes)


def iter_code_files(roots: list[Path]):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in CODE_SKIP_DIRS and not d.startswith(".")]
            for fn in filenames:
                p = Path(dirpath) / fn
                if p.suffix not in CODE_EXTS or CODE_SKIP_RE.search(p.as_posix()):
                    continue
                try:
                    if p.stat().st_size > MAX_CODE_BYTES:
                        continue
                except OSError:
                    continue
                yield p


def iter_pdfs(vault: Path):
    refs = vault / "References"
    if not refs.is_dir():
        return
    for p in sorted(refs.rglob("*.pdf")):
        if p.is_file():
            yield p


def extract_pdf_text(path: Path) -> str:
    """PDF text via pdftotext. Empty string on failure (scanned/encrypted)."""
    try:
        proc = subprocess.run(
            ["pdftotext", "-q", "-nopgbrk", str(path), "-"],
            capture_output=True, text=True, timeout=120,
        )
    except (subprocess.SubprocessError, OSError):
        return ""
    text = proc.stdout
    # Collapse the ragged whitespace pdftotext leaves behind; it wastes the
    # embedding model's limited context on layout artifacts.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:MAX_PDF_CHARS].strip()


def read_code(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_STATUS_RE = re.compile(r"^status:\s*(.+?)\s*$", re.MULTILINE)
_DATE_RE = re.compile(r"^date:\s*(\d{4})-(\d{2})-(\d{2})", re.MULTILINE)
_SUPERSEDED_BY_RE = re.compile(r"^superseded_by:\s*(.+?)\s*$", re.MULTILINE)


def note_metadata(text: str) -> dict:
    """Pull status / date / superseded_by out of a note's frontmatter.

    `date:` is preferred over mtime for recency: a git checkout, a sync, or a
    typo fix rewrites mtime and would otherwise make an old note look new.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}
    fm = m.group(1)
    out: dict = {}
    s = _STATUS_RE.search(fm)
    if s:
        out["status"] = s.group(1).strip().strip("\"'").lower()
    d = _DATE_RE.search(fm)
    if d:
        try:
            import datetime as _dt
            out["date"] = _dt.datetime(
                int(d.group(1)), int(d.group(2)), int(d.group(3))
            ).timestamp()
        except ValueError:
            pass
    sb = _SUPERSEDED_BY_RE.search(fm)
    if sb:
        out["superseded_by"] = sb.group(1).strip().strip("\"'")
    return out


def recency_factor(mtime: float, now: float | None = None) -> float:
    """Newer files score higher, bounded below by RECENCY_FLOOR."""
    now = now if now is not None else time.time()
    age_days = max(0.0, (now - mtime) / 86400.0)
    decay = 0.5 ** (age_days / RECENCY_HALFLIFE_DAYS)
    return RECENCY_FLOOR + (1.0 - RECENCY_FLOOR) * decay


def freshness(entry: dict, now: float | None = None) -> float:
    """Combined age + supersession multiplier for a ranked document.

    Uses the note's own `date:` when present, falling back to mtime.
    """
    now = now if now is not None else time.time()
    stamp = entry.get("date") or entry.get("mtime") or now
    f = recency_factor(stamp, now)
    if entry.get("status") == "superseded":
        f *= SUPERSEDED_PENALTY
    return f
