#!/usr/bin/env python3
"""Build the upload PDF: deck.html up to and including References, i.e. without the
Likely questions slide and the 'If the results are public' section at the end.
Usage: python3 make_upload.py
With --full: drop only the Likely questions slide (higgs2026_higgs_charm_noLQ.pdf)."""
import os, re, subprocess, sys
FULL = "--full" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "deck.html")).read()
a = s.index('<header><h2>Likely questions</h2></header>'); a = s.rindex('<section', 0, a)
if FULL:
    b = s.index('</section>', a) + len('</section>')
else:
    b = s.index('<script>\n// gluon')
s = s[:a] + s[b:]
open(os.path.join(HERE, "deck_upload.html"), "w").write(s)
subprocess.run(["python3", os.path.join(HERE, "build.py"), "deck_upload.html"], check=True, cwd=HERE)
OUT = "higgs2026_higgs_charm_noLQ.pdf" if FULL else "higgs2026_higgs_charm_upload.pdf"
os.replace(os.path.join(HERE, "deck_upload.pdf"), os.path.join(HERE, OUT))
os.remove(os.path.join(HERE, "deck_upload.html"))
print("wrote", OUT)
