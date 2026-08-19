import pathlib, re, sys

NOTE = """# NOTE: xsec deliberately 0.0 -- DO NOT "fix" this.
# TBbarQ / TbarBQ are the INCLUSIVE t-channel single-top samples and cover exactly the
# same phase space as the decay-split TQbarto2Q/TQbartoLNu (top) and TbarQto2Q/TbarQtoLNu
# (antitop) samples that ARE used. Giving them a real cross section would DOUBLE-COUNT
# single top.
# Verified 2026-08-12: the decay-split samples already sum to the full t-channel rates --
#   top     TQbarto2Q 97.614 + TQbartoLNu 47.372 = 144.99 pb  (13.6 TeV value ~145 pb)
#   antitop TbarQto2Q 58.703 + TbarQtoLNu 28.488 =  87.19 pb  (13.6 TeV value  ~87 pb)
#   ratio 1.66 = the expected LHC top/antitop asymmetry; 2Q:LNu ~ 67:33 = W branching
# (The s-channel samples TBbartoLplusNuBbar / TbarBtoLminusNuB are a DIFFERENT process
# and are correctly non-zero.)
# These two are still fetched+processed but contribute zero yield; they could be dropped
# from the fileset entirely to save EOS space and CPU."""

changed = []
for y in ["2022postEE", "2022preEE", "2023preBPix", "2023postBPix"]:
    p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/%s_nanov12.yaml" % y)
    if not p.exists():
        print("skip (missing):", p.name); continue
    s = p.read_text()
    if "DO NOT \"fix\" this" in s:
        print("already annotated:", p.name); continue
    n = 0
    for key in ("TBbarQ", "TbarBQ"):
        # anchor on the top-level key at column 0
        pat = re.compile(r"^%s:$" % re.escape(key), re.M)
        m = pat.search(s)
        if not m:
            print("  !! %s not found in %s" % (key, p.name)); continue
        s = s[:m.start()] + NOTE + "\n" + s[m.start():]
        n += 1
    p.write_text(s)
    changed.append((p.name, n))

for name, n in changed:
    print("annotated %s (%d entries)" % (name, n))
