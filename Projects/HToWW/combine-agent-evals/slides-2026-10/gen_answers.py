"""Render whole agent answers as beamer frames with the evidence highlighted.

Input: example_answers.json (the stored final answers, copied verbatim from
cae-run/judge-input/*.jsonl). Output: sec-answers.tex, \\input by the deck.
Highlights: blue = text that supports a key point (label kpN), orange = a
must_not statement (label mnN). Blank lines are dropped and long lines wrapped;
the text itself is unchanged.
"""
import json
import textwrap

WIDTH = 98           # characters per line at \scriptsize
LINES = 19           # lines per frame

META = {
    ("luna-changed", "gmn-control-region-1", 2): dict(
        title="GPT-5.6 luna, changed config, gmn run 2",
        scores=r"FC \con{0.22} \quad rubric 5 \quad nugget \pos{pass}: kp1--kp5 supported, no must\_not",
        spans=[("Use a **`gmN`** nuisance parameter", "kp1"),
               ("`20` is the observed control-region count", "kp2"),
               ("`0.30` is the extrapolation factor", "kp3"),
               (r"\(20 \times 0.30 = 6.0\)", "kp4"),
               ("crStat       gmN     20      -       0.30", "kp5")]),
    ("terra-vanilla", "gmn-control-region-1", 2): dict(
        title="GPT-5.6 terra, vanilla config, gmn run 2",
        scores=r"FC 0.50 \quad rubric 5 \quad nugget \con{fail}: kp1--kp5 supported, but must\_not mn3 present",
        spans=[("gamma-distributed (`gmN`)", "kp1"),
               ("`N` is the integer CR count", "kp2"),
               ("`alpha` is entered in the column of the background process", "kp3"),
               (r"rate is \(N\alpha\)", "kp4"),
               ("bkg_stat  gmN  N  -  alpha", "kp5"),
               ("bkg_stat      gmN  -    0.12", "mn3")]),
    ("qwen-changed", "agent-shape-counting-1", 1): dict(
        title="Qwen 3.8, changed config, shape + counting run 1",
        scores=r"FC \con{0.48} \quad rubric 2 \quad nugget \con{fail}: 0/2 vital points, must\_not mn1 present \quad \grey{(answered with no tool calls)}",
        spans=[("These two datacard formats are fundamentally incompatible", "mn1"),
               ("can only combine datacards of the **same type**", "mn1"),
               ("by creating a ROOT file", "mn1")]),
    ("luna-changed", "agent-shape-counting-1", 1): dict(
        title="GPT-5.6 luna, changed config, shape + counting run 1",
        scores=r"FC 0.89 \quad rubric 5 \quad nugget \pos{pass}: kp1--kp4 supported, no must\_not \quad \grey{(opening lines: narration, joined into the answer by the harness)}",
        spans=[("`counting` is a counting-only channel and has no `shapes` mapping", "kp1"),
               ("KeyError: \"Shape map has no entry for channel 'counting'\"", "kp3"),
               ("shapes * * FAKE", "kp2"),
               ("or use `combineCards.py -S`", "kp4")]),
}

CHARS = {"’": "'", "—": "--", "×": r"\texttimes{}", "α": r"\ensuremath{\alpha}"}


def esc(s: str) -> str:
    out = []
    for ch in s:
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "{}":
            out.append("\\" + ch)
        else:
            out.append(CHARS.get(ch, ch))
    return "".join(out)


def wrap(text: str) -> list[str]:
    lines = []
    for raw in text.split("\n"):
        if not raw.strip():
            continue
        lines += textwrap.wrap(raw, WIDTH, break_long_words=True, replace_whitespace=False,
                               drop_whitespace=True) or [""]
    return lines


def mark(line: str, spans) -> tuple[str, set]:
    """Escape one line, wrapping every span occurrence in \\hlkp/\\hlmn."""
    hits = []
    for s, lab in spans:
        i = line.find(s)
        if i >= 0:
            hits.append((i, i + len(s), lab))
    hits.sort()
    out, pos, used = [], 0, set()
    for a, b, lab in hits:
        if a < pos:
            continue
        out.append(esc(line[pos:a]))
        cmd = r"\hlmn" if lab.startswith("mn") else r"\hlkp"
        out.append(f"{cmd}{{{lab}}}{{{esc(line[a:b])}}}")
        pos = b
        used.add((line[a:b], lab))
    out.append(esc(line[pos:]))
    return "".join(out), used


def main():
    answers = json.load(open("example_answers.json"))
    frames = []
    for a in answers:
        meta = META[(a["config"], a["id"], a["rep"])]
        lines = wrap(a["answer"])
        found = set()
        body = []
        for ln in lines:
            m, used = mark(ln, meta["spans"])
            body.append(m)
            found |= used
        missing = [s for s, lab in meta["spans"] if not any(s == f[0] for f in found)]
        if missing:
            print("WARN span not found (check wrapping):", meta["title"], missing)
        chunks = [body[i:i + LINES] for i in range(0, len(body), LINES)]
        for k, chunk in enumerate(chunks):
            cont = f" ({k + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            frames.append(
                "\\begin{frame}[fragile]{Whole answer: " + meta["title"] + cont + "}\n"
                "  \\vspace{2pt}\\begingroup\\small " + meta["scores"] + "\\par\\endgroup\n"
                "  {\\footnotesize\\grey{Final answer as stored by the harness; blank lines dropped, long lines wrapped. "
                "\\hlkp{kp}{blue}: supports a key point, \\hlmn{mn}{orange}: must\\_not statement.}}\n"
                "\\begin{Verbatim}[commandchars=\\\\\\{\\},fontsize=\\scriptsize,frame=single,rulecolor=\\color{cmsgrey}]\n"
                + "\n".join(chunk) + "\n\\end{Verbatim}\n\\end{frame}\n")
    open("sec-answers.tex", "w").write(
        "% Generated by gen_answers.py from example_answers.json. Do not edit by hand.\n\n"
        + "\n".join(frames))
    print(f"wrote sec-answers.tex: {len(frames)} frames")


if __name__ == "__main__":
    main()
