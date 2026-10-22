#!/usr/bin/env python3
"""Build the upload PDF: deck.html without the 'If the results are public' section,
the altnote tags and the Likely questions slide. Usage: python3 make_upload.py"""
import os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "deck.html")).read()
# alternate section: from its divider up to the Backup divider
a = s.index('<section class="slide divider"><div class="line"></div><h1>If the results are public</h1>')
b = s.index('<section class="slide divider"><div class="line"></div><h1>Backup</h1>')
s = s[:a] + s[b:]
s = re.sub(r'\n\s*<span class="altnote">[^<]*</span>', '', s)
# likely questions slide
a = s.index('<header><h2>Likely questions</h2></header>'); a = s.rindex('<section', 0, a)
b = s.index('</section>', a) + len('</section>')
s = s[:a] + s[b:]
s = s.replace('data-n="34"', 'data-n="33"')
open(os.path.join(HERE, "deck_upload.html"), "w").write(s)
subprocess.run(["python3", os.path.join(HERE, "build.py"), "deck_upload.html"], check=True, cwd=HERE)
os.replace(os.path.join(HERE, "deck_upload.pdf"), os.path.join(HERE, "higgs2026_higgs_charm_upload.pdf"))
os.remove(os.path.join(HERE, "deck_upload.html"))
print("wrote higgs2026_higgs_charm_upload.pdf")
