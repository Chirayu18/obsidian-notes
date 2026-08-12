"""Three-way comparison, with measured and modelled parts kept separate.

  A. vanilla   -- no vault, no notes, no index. Cold agent, raw repo only.
  B. vault+grep-- the notes exist; agent greps them.
  C. vault+RAG -- the notes exist; agent queries the index.

B and C are MEASURED (agent_sim.py, 16 queries against the real vault).
A cannot be measured the same way: the notes DO exist, so I cannot un-know
them. A is MODELLED from quantities I did measure, with every input stated.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BYTES_PER_TOKEN = 4.0

# ---------------------------------------------------------------- measured
VAULT_MD_FILES = 191
VAULT_MD_BYTES = 1_400_000          # 1.40 MB -> ~350k tokens
REPO_SRC_FILES = 168
REPO_SRC_BYTES = 7_517_548          # higgscharm, .py/.yaml/.json/.sh
REPO_COMMITS = 856

rows = json.loads((HERE / "agent_results.json").read_text())
N_Q = len(rows)
MEASURED = {
    "grep": dict(
        solved=sum(r["norag"]["found"] for r in rows),
        calls=sum(r["norag"]["calls"] for r in rows),
        tokens=sum(r["norag"]["read_bytes"] for r in rows) / BYTES_PER_TOKEN,
    ),
    "rag": dict(
        solved=sum(r["rag"]["found"] for r in rows),
        calls=sum(r["rag"]["calls"] for r in rows),
        tokens=sum(r["rag"]["read_bytes"] for r in rows) / BYTES_PER_TOKEN,
    ),
}

# ---------------------------------------------------------------- modelled
# A vanilla agent asked "why did the limit come out wrong?" has no note saying
# "autoMCStats + negative weights". To answer it must reconstruct the finding.
#
# Every number below is an assumption, stated so it can be argued with.

ORIENT_FRAC = 0.15      # fraction of repo source read while orienting
ORIENT_TOKENS = REPO_SRC_BYTES * ORIENT_FRAC / BYTES_PER_TOKEN
ORIENT_CALLS = 25       # ls / find / grep / read during orientation

# Re-deriving one non-obvious finding means: read the builder, read the parquet
# writer, inspect metadata, run a comparison, notice a 2.4x discrepancy.
#
# Anchored in the real record rather than guessed: the autoMCStats thread runs
# 2026-06-17 (LIMIT-ISSUE) -> 2026-07-12 (phase3 handoff) -- ~4 weeks, 5 notes.
# 2026-07-31-sumw-normalization-trap.md alone is 277 lines of conclusions.
# 180k tokens is a DEFLATED estimate of one such investigation: it is roughly
# one long session, where the real thing took weeks of human work. Chosen to
# be conservative -- the vanilla number is understated, not inflated.
REDERIVE_CALLS = 60
REDERIVE_TOKENS = 180_000

# ...and some findings are NOT re-derivable from code alone. "We decided to
# keep the 2D ctag SF as one nuisance" is a judgement call with no artifact.
UNDERIVABLE_FRAC = 0.35


def main() -> None:
    print("=" * 68)
    print("MEASURED — 16 queries against the real vault")
    print("=" * 68)
    for k, label in (("grep", "B. vault + grep"), ("rag", "C. vault + RAG ")):
        m = MEASURED[k]
        print(f"{label}  solved {m['solved']}/{N_Q}   "
              f"{m['calls']:>3} calls   {m['tokens']/1000:>6.0f}k tokens")

    print()
    print("=" * 68)
    print("MODELLED — A. vanilla (no vault), per equivalent question")
    print("=" * 68)
    per_q_vanilla_tokens = ORIENT_TOKENS / N_Q + REDERIVE_TOKENS
    per_q_vanilla_calls = ORIENT_CALLS / N_Q + REDERIVE_CALLS
    van_tokens = ORIENT_TOKENS + REDERIVE_TOKENS * N_Q
    van_calls = ORIENT_CALLS + REDERIVE_CALLS * N_Q
    van_solved = round(N_Q * (1 - UNDERIVABLE_FRAC))

    print(f"  orientation (once): {ORIENT_TOKENS/1000:.0f}k tokens "
          f"({ORIENT_FRAC:.0%} of {REPO_SRC_BYTES/1e6:.1f} MB source), {ORIENT_CALLS} calls")
    print(f"  re-derive per question: {REDERIVE_TOKENS/1000:.0f}k tokens, {REDERIVE_CALLS} calls")
    print(f"  -> per question: ~{per_q_vanilla_tokens/1000:.0f}k tokens, "
          f"~{per_q_vanilla_calls:.0f} calls")
    print(f"  -> 16 questions: ~{van_tokens/1000:.0f}k tokens, {van_calls:.0f} calls")
    print(f"  -> solvable at all: ~{van_solved}/{N_Q} "
          f"({UNDERIVABLE_FRAC:.0%} are judgement calls with no code artifact)")

    print()
    print("=" * 68)
    print("RATIOS (vanilla is modelled; treat as order-of-magnitude)")
    print("=" * 68)
    rag_tok = MEASURED["rag"]["tokens"]
    grep_tok = MEASURED["grep"]["tokens"]
    print(f"  vanilla / RAG  tokens: {van_tokens/rag_tok:>6.0f}x")
    print(f"  vanilla / grep tokens: {van_tokens/grep_tok:>6.0f}x")
    print(f"  grep    / RAG  tokens: {grep_tok/rag_tok:>6.1f}x   [both measured]")

    out = dict(
        measured=MEASURED, n_queries=N_Q,
        vanilla=dict(tokens=van_tokens, calls=van_calls, solved=van_solved,
                     per_q_tokens=per_q_vanilla_tokens),
        inputs=dict(vault_md_files=VAULT_MD_FILES, vault_md_bytes=VAULT_MD_BYTES,
                    repo_src_files=REPO_SRC_FILES, repo_src_bytes=REPO_SRC_BYTES,
                    repo_commits=REPO_COMMITS, orient_frac=ORIENT_FRAC,
                    rederive_tokens=REDERIVE_TOKENS, rederive_calls=REDERIVE_CALLS,
                    underivable_frac=UNDERIVABLE_FRAC),
    )
    (HERE / "vanilla_results.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {HERE/'vanilla_results.json'}")


if __name__ == "__main__":
    main()
