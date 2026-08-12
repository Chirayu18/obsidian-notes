"""Plots for the RAG evaluation deck."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = Path("/home/cgupta/obsidian-notes/Projects/PromptTooling/rag-eval-2026-08-13/img")
OUT.mkdir(parents=True, exist_ok=True)

GREP = "#8c8c8c"
RAG = "#2166ac"
HL = "#b2182b"
OK = "#1a7f37"

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 160,
    "savefig.bbox": "tight",
})


def load():
    return json.loads((HERE / "eval_results.json").read_text())


def agg(rows, method, kind=None):
    sel = [r for r in rows if kind is None or r["kind"] == kind]
    if not sel:
        return 0.0, 0.0
    return (sum(r[method]["hit"] for r in sel) / len(sel),
            sum(r[method]["rr"] for r in sel) / len(sel))


def plot_hit_by_kind(rows):
    kinds = ["paraphrase", "partial", "literal"]
    labels = ["Paraphrase\n(no shared terms)", "Partial\n(one shared term)", "Literal\n(exact term)"]
    g = [agg(rows, "grep", k)[0] * 100 for k in kinds]
    r = [agg(rows, "rag", k)[0] * 100 for k in kinds]
    n = [sum(1 for x in rows if x["kind"] == k) for k in kinds]

    x = np.arange(len(kinds))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    b1 = ax.bar(x - w / 2, g, w, label="grep only", color=GREP)
    b2 = ax.bar(x + w / 2, r, w, label="vault-search (RAG)", color=RAG)
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                f"{b.get_height():.0f}%", ha="center", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\nn={c}" for l, c in zip(labels, n)])
    ax.set_ylabel("hit@5  (% of queries)")
    ax.set_ylim(0, 118)
    ax.set_title("Did the right note appear in the top 5?", fontweight="bold")
    ax.legend(frameon=False, loc="upper left", ncols=2)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "hit_by_kind.png")
    plt.close(fig)


def plot_mrr(rows):
    kinds = ["paraphrase", "partial", "literal", None]
    labels = ["paraphrase", "partial", "literal", "ALL"]
    g = [agg(rows, "grep", k)[1] for k in kinds]
    r = [agg(rows, "rag", k)[1] for k in kinds]
    x = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.bar(x - w / 2, g, w, label="grep only", color=GREP)
    ax.bar(x + w / 2, r, w, label="vault-search (RAG)", color=RAG)
    for i, (a, b) in enumerate(zip(g, r)):
        ax.text(i - w / 2, a + .02, f"{a:.2f}", ha="center", fontsize=9)
        ax.text(i + w / 2, b + .02, f"{b:.2f}", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("MRR  (1.0 = always rank 1)")
    ax.set_ylim(0, max(max(g), max(r)) * 1.35)
    ax.set_title("Mean Reciprocal Rank — how far down the list?", fontweight="bold")
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "mrr.png")
    plt.close(fig)


def plot_per_query(rows):
    """Where each method lands per query -- shows wins AND losses honestly."""
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ys = np.arange(len(rows))
    for i, r in enumerate(rows):
        grr, rrr = r["grep"]["rr"], r["rag"]["rr"]
        ax.plot([grr, rrr], [i, i], color="#cccccc", lw=1.4, zorder=1)
        ax.scatter([grr], [i], color=GREP, s=42, zorder=2,
                   label="grep" if i == 0 else None)
        ax.scatter([rrr], [i], color=RAG, s=42, zorder=3,
                   label="vault-search" if i == 0 else None)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['q'][:44]}{'…' if len(r['q'])>44 else ''}" for r in rows],
                       fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("reciprocal rank of the correct note   (0 = not found, 1.0 = top hit)")
    ax.set_xlim(-0.04, 1.08)
    ax.axvline(0, color="#dddddd", lw=1)
    ax.set_title("Per-query outcome", fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    fig.savefig(OUT / "per_query.png")
    plt.close(fig)


def plot_latency(rows):
    g = np.array([r["grep"]["dt"] for r in rows]) * 1000
    r = np.array([r["rag"]["dt"] for r in rows]) * 1000
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.barh(["grep only", "vault-search\n(RAG)"], [g.mean(), r.mean()],
            color=[GREP, RAG], height=.5)
    ax.text(g.mean() * 1.05, 0, f"{g.mean():.0f} ms", va="center", fontsize=10)
    ax.text(r.mean() * 1.02, 1, f"{r.mean():.0f} ms", va="center", fontsize=10)
    ax.set_xlabel("mean query latency (ms, log scale)")
    ax.set_xscale("log")
    ax.set_xlim(1, r.mean() * 3)
    ax.set_title("Cost of a query", fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    fig.savefig(OUT / "latency.png")
    plt.close(fig)


def plot_index_cost():
    """Index build economics -- measured, see deck notes."""
    ops = ["Cold build\n(309 docs)", "Prune 66\nstale docs", "One note\nchanged", "Nothing\nchanged"]
    secs = [311, 1.7, 2.8, 1.7]
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    bars = ax.bar(ops, secs, color=[HL, RAG, RAG, OK], width=.55)
    for b, s in zip(bars, secs):
        lab = f"{s/60:.1f} min" if s > 90 else f"{s:.1f} s"
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.15, lab,
                ha="center", fontsize=10)
    ax.set_yscale("log")
    ax.set_ylim(.8, 1400)
    ax.set_ylabel("wall clock (s, log scale)")
    ax.set_title("Index maintenance cost — the incremental path is what runs daily",
                 fontweight="bold", fontsize=11)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "index_cost.png")
    plt.close(fig)


def plot_corpus():
    tiers = ["notes", "papers", "code"]
    counts = [185, 19, 105]
    weights = [1.0, 0.7, 0.5]
    colors = [RAG, "#7fb3d5", "#a9cce3"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.4, 3.2))
    a1.bar(tiers, counts, color=colors, width=.55)
    for i, c in enumerate(counts):
        a1.text(i, c + 5, str(c), ha="center", fontsize=10)
    a1.set_ylabel("documents indexed")
    a1.set_title("Corpus (309 docs / 1828 chunks)", fontweight="bold", fontsize=10.5)
    a1.grid(axis="y", alpha=.25)
    a2.bar(tiers, weights, color=colors, width=.55)
    for i, w in enumerate(weights):
        a2.text(i, w + .03, f"×{w}", ha="center", fontsize=10)
    a2.set_ylim(0, 1.2)
    a2.set_ylabel("tier weight on final score")
    a2.set_title("Notes rank first by construction", fontweight="bold", fontsize=10.5)
    a2.grid(axis="y", alpha=.25)
    fig.savefig(OUT / "corpus.png")
    plt.close(fig)


def plot_agent_cost():
    """The comparison that matters: what it costs the agent, not hit@5."""
    rows = json.loads((HERE / "agent_results.json").read_text())
    n = len(rows)
    solved = [sum(r[m]["found"] for r in rows) for m in ("norag", "rag")]
    calls = [sum(r[m]["calls"] for r in rows) for m in ("norag", "rag")]
    toks = [sum(r[m]["read_bytes"] for r in rows) / 4 / 1000 for m in ("norag", "rag")]

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.2))
    panels = [
        (solved, f"queries solved (of {n})", "higher is better", None),
        (calls, "tool calls", "lower is better", None),
        (toks, "context read (k tokens)", "lower is better", None),
    ]
    for ax, (vals, title, sub, _) in zip(axes, panels):
        bars = ax.bar(["no RAG", "RAG"], vals, color=[GREP, RAG], width=.55)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.03,
                    f"{v:.0f}", ha="center", fontsize=11, fontweight="bold")
        ax.set_title(title, fontweight="bold", fontsize=10.5)
        ax.set_xlabel(sub, fontsize=8.5, color="#666666")
        ax.set_ylim(0, max(vals) * 1.25)
        ax.grid(axis="y", alpha=.25)
    axes[2].annotate(f"{toks[0]/toks[1]:.1f}× less", xy=(1, toks[1] * 1.18),
                     xytext=(0.30, toks[0] * .55), fontsize=10.5, color=OK,
                     fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color=OK, lw=1.4,
                                     connectionstyle="arc3,rad=-0.25"))
    fig.suptitle("Cost to the agent of answering from the vault",
                 fontweight="bold", fontsize=12.5, y=1.04)
    fig.savefig(OUT / "agent_cost.png")
    plt.close(fig)


def plot_context_per_query():
    rows = json.loads((HERE / "agent_results.json").read_text())
    ys = np.arange(len(rows))
    a = [r["norag"]["read_bytes"] / 1024 for r in rows]
    b = [r["rag"]["read_bytes"] / 1024 for r in rows]
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    h = .38
    ax.barh(ys - h / 2, a, h, color=GREP, label="no RAG")
    ax.barh(ys + h / 2, b, h, color=RAG, label="RAG")
    for i, r in enumerate(rows):
        if not r["norag"]["found"]:
            ax.text(a[i] + 2, i - h / 2, "✗", va="center", fontsize=9, color=HL)
        if not r["rag"]["found"]:
            ax.text(b[i] + 2, i + h / 2, "✗", va="center", fontsize=9, color=HL)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['q'][:34]}{'…' if len(r['q'])>34 else ''}" for r in rows],
                       fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("context read to answer (KB of file content)")
    ax.set_title("Wrong files opened along the way", fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=.25)
    fig.savefig(OUT / "context_per_query.png")
    plt.close(fig)


def plot_three_way():
    """vanilla vs vault+grep vs vault+RAG. Modelled bar is hatched."""
    v = json.loads((HERE / "vanilla_results.json").read_text())
    labels = ["A. vanilla\n(no vault)", "B. vault\n+ grep", "C. vault\n+ RAG"]
    toks = [v["vanilla"]["tokens"] / 1000,
            v["measured"]["grep"]["tokens"] / 1000,
            v["measured"]["rag"]["tokens"] / 1000]
    solved = [v["vanilla"]["solved"], v["measured"]["grep"]["solved"],
              v["measured"]["rag"]["solved"]]
    n = v["n_queries"]
    colors = [HL, GREP, RAG]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.6))
    bars = a1.bar(labels, toks, color=colors, width=.55)
    bars[0].set_hatch("///")
    bars[0].set_alpha(.85)
    for b, t in zip(bars, toks):
        a1.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.25,
                f"{t:,.0f}k", ha="center", fontsize=10.5, fontweight="bold")
    a1.set_yscale("log")
    a1.set_ylim(50, toks[0] * 6)
    a1.set_ylabel("context to answer 16 questions\n(k tokens, log scale)")
    a1.set_title("Cost", fontweight="bold", fontsize=11)
    a1.grid(axis="y", alpha=.25)
    a1.text(0, toks[0] * 2.6, "modelled", ha="center", fontsize=8, color=HL, style="italic")

    b2 = a2.bar(labels, solved, color=colors, width=.55)
    b2[0].set_hatch("///")
    b2[0].set_alpha(.85)
    a2.axhline(n, color="#999999", ls=":", lw=1.2)
    a2.text(2.45, n + .25, f"all {n}", fontsize=8.5, color="#666666", ha="right")
    for b, s in zip(b2, solved):
        a2.text(b.get_x() + b.get_width() / 2, b.get_height() + .3,
                str(s), ha="center", fontsize=11, fontweight="bold")
    a2.set_ylim(0, n * 1.25)
    a2.set_ylabel(f"questions answered (of {n})")
    a2.set_title("Capability", fontweight="bold", fontsize=11)
    a2.grid(axis="y", alpha=.25)
    fig.suptitle("Vanilla agent vs vault vs vault+RAG",
                 fontweight="bold", fontsize=12.5, y=1.03)
    fig.savefig(OUT / "three_way.png")
    plt.close(fig)


def plot_knowledge_floor():
    """The point the token ratio hides: some answers aren't in the code."""
    fig, ax = plt.subplots(figsize=(8.4, 2.1))
    cats = ["In the code\n(re-derivable, expensively)",
            "Only in your notes\n(judgement calls, dead ends)"]
    vals = [65, 35]
    left = 0
    for c, val, col in zip(cats, vals, [GREP, HL]):
        ax.barh([0], [val], left=left, color=col, height=.5)
        ax.text(left + val / 2, 0, f"{val}%", ha="center", va="center",
                color="white", fontweight="bold", fontsize=13)
        left += val
    ax.set_xlim(0, 100)
    ax.set_ylim(-.55, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("share of the 16 benchmark questions", fontsize=9)
    for i, (c, col) in enumerate(zip(cats, [GREP, HL])):
        ax.text([32, 82][i], .48, c, ha="center", fontsize=9, color=col,
                fontweight="bold")
    ax.set_title("A third of the questions have no answer in the source code",
                 fontweight="bold", fontsize=10.5, pad=26)
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", alpha=.2)
    fig.savefig(OUT / "knowledge_floor.png")
    plt.close(fig)


def main():
    rows = load()
    plot_three_way()
    plot_knowledge_floor()
    plot_agent_cost()
    plot_context_per_query()
    plot_hit_by_kind(rows)
    plot_mrr(rows)
    plot_per_query(rows)
    plot_latency(rows)
    plot_index_cost()
    plot_corpus()
    print(f"wrote {len(list(OUT.glob('*.png')))} plots -> {OUT}")
    for p in sorted(OUT.glob("*.png")):
        print("  ", p.name)


if __name__ == "__main__":
    sys.exit(main())
