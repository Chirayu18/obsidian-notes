---
name: an-repo-latex-broken-on-master
description: The H+c AN repo does not compile on master - raw # in a URL in Efficiencies.tex line 80
metadata:
  type: project
---

The private AN repo `Analysis-Note-Run-3-H-c-H-to-WW-Copy-` **fails `pdflatex` on
`master`**, independently of any of our additions. Verified 2026-08-21 by stashing all
new work and compiling clean master: same 6 errors.

Root cause: `Efficiencies.tex` line 80 has an unescaped `#` inside a bare URL —
`https://muon-wiki.docs.cern.ch/guidelines/corrections/#tracking-efficiency`.
LaTeX reads `#` as a macro parameter character, which then cascades into three
`Illegal parameter number in definition of \Hy@tempa` errors from hyperref and a
`Missing } inserted`. Fatal: no PDF is produced.

Fix would be `\#` or wrapping the URL in `\url{}` — but this is an EXISTING section
and the standing instruction is "don't touch any existing things and sections in the
AN", so it was left alone and reported instead.

**How to verify new AN sections compile** without touching that file: build a harness
document from main.tex's preamble plus only the new `\input` lines (drop the existing
section inputs), append the `thebibliography` block so `\cite` resolves, and run
`pdflatex` twice for cross-references. Our nine sections compile at 0 errors /
0 undefined refs / 25 pages this way.

Also note this AN's preamble defines **none** of the usual CMS macros — `\MADGRAPH`,
`\MCATNLO`, `\PYTHIA`, `\GEANTfour`, `\PARTICLENET`, `\POWHEG`, `\COMBINE` are all
undefined. Write generator names as plain text. `\code{}` and `\SI{}` DO exist.

Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-combine-pipeline|hww-combine-pipeline]]
