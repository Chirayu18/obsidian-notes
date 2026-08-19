"""Make variants 1 and 2 SIGNAL-ONLY (H+c). Variant 3 keeps all MC."""
import re
from pathlib import Path
import os
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
W = Path("analysis/workflows")

for f in ("hww_2dcat_nocjet.yaml", "hww_2dcat_looseWP.yaml"):
    p = W / f
    s = p.read_text()
    # replace the whole datasets: block (up to the next top-level key) with signal only
    m = re.search(r"^datasets:\n(?:[ #].*\n|\n)*", s, flags=re.M)
    assert m, f"datasets block not found in {f}"
    new_block = (
        "datasets:\n"
        "  # SIGNAL ONLY for this acceptance test (2026-08-08): we only need how much\n"
        "  # H+c each c-jet selection recovers. Backgrounds are unchanged by the WP\n"
        "  # question at this stage and would cost hours of queue for nothing.\n"
        "  mc:\n"
        "    - hc\n"
    )
    s = s[:m.start()] + new_block + s[m.end():]
    p.write_text(s)
    # report
    blk = re.search(r"^datasets:\n(?:[ #].*\n|\n)*", s, flags=re.M).group(0)
    print(f"--- {f} ---")
    print("\n".join(l for l in blk.splitlines() if not l.strip().startswith("#")))
