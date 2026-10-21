"""Render whole agent answers as beamer frames with the evidence highlighted.

Input: example_answers.json (the stored final answers, copied verbatim from
cae-run/judge-input/*.jsonl, in slide order). Output: sec-answers.tex, \\input
by the deck. Highlights: blue = text that supports a key point, orange = a
wrong statement (must_not). A label ending in "judge missed" marks a place where
the nugget judge got it wrong. Blank lines are dropped and long lines wrapped;
the text itself is unchanged.
"""
import json
import textwrap

WIDTH = 108          # characters per line at 6.6pt
LINES = 23           # lines per frame

KEY = {  # (config, question, rep) -> slide metadata
    ("luna-changed", "gmn-control-region-1", 2): dict(
        scores=r"FC \con{0.22} \quad rubric 5 \quad nugget \pos{pass}: kp1--kp5, no must\_not",
        spans=[("Use a **`gmN`** nuisance parameter", "kp1"),
               ("`20` is the observed control-region count", "kp2"),
               ("`0.30` is the extrapolation factor", "kp3"),
               (r"\(20 \times 0.30 = 6.0\)", "kp4"),
               ("crStat       gmN     20      -       0.30", "kp5")]),
    ("qwen-changed", "gmn-control-region-1", 0): dict(
        scores=r"FC 0.87 \quad rubric 5 \quad nugget \pos{pass}: kp1--kp6, no must\_not \quad \grey{(5 tool calls)}",
        spans=[("Use the **`gmN`** (Gamma) uncertainty type", "kp1"),
               ("**immediately after the `gmN`", "kp2"),
               ("Put **`α`** (the extrapolation factor", "kp3"),
               ("must equal **`N·α`**", "kp4"),
               ("WW_norm  gmN  4    -   0.16    -     -", "kp5"),
               ("`1/√5` ≈ 45%", "kp6")]),
    ("qwen-changed", "gmn-control-region-1", 1): dict(
        scores=r"FC 0.78 \quad rubric 5 \quad nugget \pos{pass}: kp1--kp6, no must\_not \quad \grey{(7 tool calls; opening lines are narration)}",
        spans=[("the recommended modifier is **`gmN`**", "kp1"),
               ("Put **N** immediately after the `gmN` keyword.", "kp2"),
               ("Put **α** in the relevant (bin, process) column", "kp3"),
               ("must equal **N·α**", "kp4"),
               ("WW_norm  gmN  4  -  0.16  -  -", "kp5"),
               ("1/√(4+1) = 45%", "kp6")]),
    ("terra-vanilla", "gmn-control-region-1", 2): dict(
        scores=r"FC 0.50 \quad rubric 5 \quad nugget \con{fail}: kp1--kp5, but must\_not mn3 present",
        spans=[("gamma-distributed (`gmN`)", "kp1"),
               ("`N` is the integer CR count", "kp2"),
               ("`alpha` is entered in the column of the background process", "kp3"),
               (r"rate is \(N\alpha\)", "kp4"),
               ("bkg_stat  gmN  N  -  alpha", "kp5"),
               ("bkg_stat      gmN  -    0.12", "mn3")]),
    ("terra-changed", "gmn-control-region-1", 2): dict(
        scores=r"FC 0.62 \quad rubric 5 \quad nugget \pos{pass} \con{(wrong: judge missed mn3)}: example rate 10.0, but $25\times0.12=3.0$",
        spans=[("Use a `gmN` nuisance parameter", "kp1"),
               ("bkg_stat  gmN  N  -  alpha", "kp2"),
               (r"set the nominal signal-region background rate to \(N\alpha\)", "kp4"),
               ("and `0.12` is the", "kp3"),
               ("rate                  10.0", "mn3 judge missed")]),
    ("qwen-changed", "gmn-control-region-1", 2): dict(
        scores=r"FC 0.00 \quad rubric 1 \quad nugget \con{fail}: 0/4 vital \quad \grey{(no tool calls; the whole answer is a made-up skill file)}",
        spans=[('<skill_content name="combine">', "invented, no tool was called")]),
    ("luna-changed", "agent-shape-counting-1", 1): dict(
        scores=r"FC 0.89 \quad rubric 5 \quad nugget \pos{pass}: kp1--kp4 \quad \grey{(opening lines are narration)}",
        spans=[("`counting` is a counting-only channel and has no `shapes` mapping", "kp1"),
               ("KeyError: \"Shape map has no entry for channel 'counting'\"", "kp3"),
               ("shapes * * FAKE", "kp2"),
               ("or use `combineCards.py -S`", "kp4")]),
    ("qwen-changed", "agent-shape-counting-1", 0): dict(
        scores=r"FC 0.85 \quad rubric 5 \quad nugget \pos{pass}: kp1--kp4 \quad \grey{(8 tool calls, reproduced in the shell)}",
        spans=[("`realistic-counting-experiment.txt` is a counting datacard (no `shapes` line)", "kp1"),
               ("KeyError: \"Shape map has no entry for channel 'counting'\"", "kp3"),
               ("add the `-S` option to", "kp2"),
               ("by inserting a `shapes * *", "kp4")]),
    ("qwen-changed", "agent-shape-counting-1", 1): dict(
        scores=r"FC \con{0.48} \quad rubric 2 \quad nugget \con{fail}: 0/2 vital, mn1 present \quad \grey{(no tool calls)}",
        spans=[("These two datacard formats are fundamentally incompatible", "mn1"),
               ("can only combine datacards of the **same type**", "mn1"),
               ("by creating a ROOT file", "mn1")]),
    ("terra-changed", "agent-shape-counting-1", 2): dict(
        scores=r"FC 0.80 \quad rubric 5 \quad nugget \con{fail} \con{(wrong: judge missed kp2)}: the \texttt{-S} fix is there",
        spans=[("This supplies templates for the `shapes` channel only.", "kp1"),
               ("KeyError: \"Shape map has no entry for channel 'counting'\"", "kp3"),
               ("Create the combination with `-S`", "kp2 judge missed"),
               ("by using `combineCards.py -S`", "kp4")]),
    ("luna-changedv1", "agent-shape-counting-1", 1): dict(
        scores=r"FC 0.87 \quad rubric 5 \quad nugget \con{fail} \con{(wrong: judge missed kp2)}: the \texttt{-S} / FAKE fix is there",
        spans=[("mixes a shape-based channel (`shapes`) with a counting-only", "kp1"),
               ("KeyError: \"Shape map has no entry for channel 'counting'\"", "kp3"),
               ("adding a `FAKE` shapes directive, or regenerate", "kp2 judge missed"),
               ("Alternatively, add this line to the counting card", "kp4")]),
    ("luna-vanilla", "agent-shape-counting-1", 0): dict(
        scores=r"FC 0.07 \quad rubric 1 \quad nugget \con{fail}: 0/2 vital \quad \grey{(run ended by a bash permission auto-reject; only narration left)}",
        spans=[]),
    ("luna-changedv1", "agent-shape-counting-1", 0): dict(
        scores=r"FC 0.07 \quad rubric 1 \quad nugget \con{fail}: 0/2 vital \quad \grey{(external\_directory reject after a path typo; only narration left)}",
        spans=[]),
    ("qwen-changed", "agent-shape-counting-1", 2): dict(
        scores=r"no answer \quad FC and rubric: skipped by score.py \quad nugget \con{fail} (scored 0) \quad \grey{(65 tool calls, the same command 45 times, timeout at 400 s)}",
        spans=[]),
}

CHARS = {"’": "'", "—": "--", "…": "...", "→": r"\ensuremath{\rightarrow}",
         "×": r"\texttimes{}", "·": r"\textperiodcentered{}", "α": r"\ensuremath{\alpha}",
         "σ": r"\ensuremath{\sigma}", "√": r"\ensuremath{\surd}", "≈": r"\ensuremath{\approx}"}


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


# (font command, characters per line, lines per frame); the smaller font is used
# only when it saves a frame.
FONTS = [(r"\ansfont", WIDTH, LINES), (r"\ansfontsmall", 118, 27)]


def wrap(text: str, width: int = WIDTH) -> list[str]:
    lines = []
    for raw in text.split("\n"):
        if raw.strip():
            lines += textwrap.wrap(raw, width, break_long_words=True,
                                   replace_whitespace=False) or [""]
    return lines


def mark(line: str, spans) -> tuple[str, set]:
    hits = sorted((line.find(s), line.find(s) + len(s), s, lab) for s, lab in spans if s in line)
    out, pos, used = [], 0, set()
    for a, b, s, lab in hits:
        if a < pos:
            continue
        if lab.startswith("kp"):
            cmd = r"\hlmiss" if "missed" in lab else r"\hlkp"
        else:
            cmd = r"\hlmn"
        out += [esc(line[pos:a]), f"{cmd}{{{esc(lab)}}}{{{esc(line[a:b])}}}"]
        pos = b
        used.add(s)
    out.append(esc(line[pos:]))
    return "".join(out), used


def frame(title: str, scores: str, body: list[str], font: str = r"\ansfont") -> str:
    return ("\\begin{frame}[fragile]{" + title + "}\n"
            "  \\vspace{2pt}\\begingroup\\small " + scores + "\\par\\endgroup\n"
            "\\begin{Verbatim}[commandchars=\\\\\\{\\},fontsize=" + font + ",frame=single,rulecolor=\\color{cmsgrey}]\n"
            + "\n".join(body) + "\n\\end{Verbatim}\n\\end{frame}\n")


MODEL = {"qwen": "Qwen 3.8 27B", "luna": "GPT-5.6 luna", "terra": "GPT-5.6 terra"}
CONFIG = {"vanilla": "shipped config (bash: ask)",
          "changedv1": "bash deny + read-only allow-list",
          "changed": "bash deny + read-only allow-list + no web fetch/search"}
CONFSHORT = {"vanilla": "shipped config", "changedv1": "read-only config", "changed": "read-only + no web"}
SHORT = {"gmn-control-region-1": "gmN question", "agent-shape-counting-1": "Shape + counting question"}

QUESTIONS = [
    ("gmn-control-region-1",
     r"""One of my backgrounds is estimated from the number of events observed in a control region,
multiplied by an extrapolation factor into the signal region. Which uncertainty type should I use
in the datacard for its statistical uncertainty, and how do I write it?""",
     [("kp1", "vital", r"use the \texttt{gmN} uncertainty type"),
      ("kp2", "vital", r"control-region count $N$ written after the keyword"),
      ("kp3", "vital", r"extrapolation factor $\alpha$ in the process column"),
      ("kp4", "vital", r"rate $= N\alpha$"),
      ("kp5", "okay", r"a concrete datacard line"),
      ("kp6", "okay", r"relative uncertainty $\approx 1/\sqrt{N+1}$"),
      ("mn1", r"must\_not", r"recommends \texttt{lnN}/\texttt{lnU} instead"),
      ("mn2", r"must\_not", r"number after \texttt{gmN} is $\alpha$ or the yield"),
      ("mn3", r"must\_not", r"example card inconsistent (rate $\neq N\alpha$, or no $N$)")],
     [("qwen-changed", 0), ("qwen-changed", 1), ("qwen-changed", 2),
      ("luna-changed", 2), ("terra-vanilla", 2), ("terra-changed", 2)]),
    ("agent-shape-counting-1",
     r"""I combined the two attached datacards with
\texttt{combineCards.py shapes=simple-shapes-TH1.txt counting=realistic-counting-experiment.txt > combined.txt}.
That worked, but running \texttt{combine -M FitDiagnostics combined.txt} on the result fails. What is the problem?
\grey{(attached: simple-shapes-TH1.txt, simple-shapes-TH1.root, realistic-counting-experiment.txt)}""",
     [("kp1", "vital", r"counting card has no \texttt{shapes} line, so no mapping for that channel"),
      ("kp2", "vital", r"fix: \texttt{combineCards.py -S}, or \texttt{shapes * * FAKE} in the counting card"),
      ("kp3", "okay", r"error ``Shape map has no entry for channel 'counting'\,'' at workspace building"),
      ("kp4", "okay", r"mentions both fixes"),
      ("mn1", r"must\_not", r"shape and counting cards cannot be combined at all"),
      ("mn2", r"must\_not", r"blames another cause (name clash, ROOT path, \ldots)")],
     [("qwen-changed", 0), ("qwen-changed", 1), ("qwen-changed", 2),
      ("luna-vanilla", 0), ("luna-changedv1", 0), ("luna-changedv1", 1), ("luna-changed", 1),
      ("terra-changed", 2)]),
]


def question_frame(qid, text, kps, runs):
    tag = {"vital": r"\pos{vital}", "okay": r"\grey{okay}", r"must\_not": r"\con{must\_not}"}
    rows = "\n".join(f"      {k} & {tag[t]} & {d} \\\\" for k, t, d in kps)
    return (r"""\begin{frame}{""" + SHORT[qid] + r""": the question and its key points}
  \vspace{2pt}
  \small\textbf{Question} \grey{(\texttt{""" + qid.replace("_", r"\_") + r"""})}\\
  {\footnotesize """ + text + r"""}
  \vspace{4pt}
  \begin{center}\footnotesize
    \begin{tabular}{ll>{\raggedright\arraybackslash}p{0.7\textwidth}}
      \toprule
""" + rows + r"""
      \bottomrule
    \end{tabular}
  \end{center}
  \footnotesize\grey{Key points written once from the gold answer; the judge sees only these lines.
  Next: """ + str(len(runs)) + r""" answers to this question, in full.}
\end{frame}
""")


def main():
    answers = {(a["config"], a["id"], a["rep"]): a for a in json.load(open("example_answers.json"))}
    frames = [r"""\begin{frame}{Whole answers: how to read the next slides}
  \vspace{4pt}
  \small
  \begin{itemize}
    \item For each question: the question and its key points, then every answer this talk refers to,
      word for word as stored by the harness (blank lines dropped, long lines wrapped)
    \item Title: question, model, agent config, run number; line below: RAGAS FC recall, rubric (1--5), nugget verdict
    \item \hlkp{kp}{blue}: supports a key point \quad \hlmn{mn}{orange}: wrong statement (must\_not)
    \item \hlmiss{kp judge missed}{grey}, \hlmn{mn judge missed}{orange}: the judge got it wrong
  \end{itemize}
  \vspace{4pt}
  \footnotesize\grey{Configs: shipped = combine-assistant 0.5.4 as released (bash \texttt{ask});
  read-only = bash \texttt{deny} plus a read-only allow-list; no web = read-only plus web fetch/search denied.}
\end{frame}
"""]
    for qid, text, kps, runs in QUESTIONS:
        frames.append(question_frame(qid, text, kps, runs))
        for cfg, rep in runs:
            a = answers[(cfg, qid, rep)]
            meta = KEY[(cfg, qid, rep)]
            model, conf = cfg.split("-", 1)
            if model == "qwen":
                conf = "changedv1"   # Qwen "changed" runs (2026-10-14 11:12/11:26) predate the web-fetch deny (12:53)
            title = f"{SHORT[qid]}: {MODEL[model]}, {CONFSHORT[conf]}, run {rep + 1} of 3"
            sub = meta["scores"]
            best = None
            for font, width, per in FONTS:
                lines = wrap(a["answer"], width) or ["(empty answer)"]
                nfr = -(-len(lines) // per)
                if best is None or nfr < best[0]:
                    best = (nfr, font, width, per, lines)
            _, font, width, per, lines = best
            body, found = [], set()
            for ln in lines:
                m, used = mark(ln, meta["spans"])
                body.append(m)
                found |= used
            missing = [s for s, _ in meta["spans"] if s not in found]
            if missing:
                print("WARN span not found:", title, missing)
            chunks = [body[i:i + per] for i in range(0, len(body), per)]
            for k, chunk in enumerate(chunks):
                cont = f" (page {k + 1} of {len(chunks)})" if len(chunks) > 1 else ""
                frames.append(frame(title + cont, sub, chunk, font))
    open("sec-answers.tex", "w").write(
        "% Generated by gen_answers.py from example_answers.json. Do not edit by hand.\n\n"
        + "\n".join(frames))
    print(f"wrote sec-answers.tex: {len(frames)} frames")


if __name__ == "__main__":
    main()
