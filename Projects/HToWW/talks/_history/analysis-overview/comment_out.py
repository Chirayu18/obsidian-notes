import pathlib, re

HDR = """# ---------------------------------------------------------------------------------
# DISABLED 2026-08-12 -- TBbarQ / TbarBQ commented out entirely.
#
# They are the INCLUSIVE t-channel single-top samples and duplicate the phase space of
# the decay-split TQbarto2Q/TQbartoLNu (top) and TbarQto2Q/TbarQtoLNu (antitop) samples
# that ARE used. They carried xsec: 0.0 so they already contributed ZERO yield -- this
# just stops fetching and processing them.
#
# Verified 2026-08-12: the decay-split samples already sum to the full t-channel rates --
#   top     TQbarto2Q 97.614 + TQbartoLNu 47.372 = 144.99 pb  (13.6 TeV value ~145 pb)
#   antitop TbarQto2Q 58.703 + TbarQtoLNu 28.488 =  87.19 pb  (13.6 TeV value  ~87 pb)
#   ratio 1.66 = expected LHC top/antitop asymmetry; 2Q:LNu ~ 67:33 = W branching
#
# DO NOT re-enable with a real cross section -- that would DOUBLE-COUNT single top.
# (The s-channel samples TBbartoLplusNuBbar / TbarBtoLminusNuB are a DIFFERENT process
# and remain active with non-zero cross sections.)
# ---------------------------------------------------------------------------------"""

OLD_NOTE_START = '# NOTE: xsec deliberately 0.0 -- DO NOT "fix" this.'

for y in ["2022postEE", "2022preEE", "2023preBPix", "2023postBPix"]:
    p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/%s_nanov12.yaml" % y)
    lines = p.read_text().split("\n")
    out, i, n = [], 0, 0
    while i < len(lines):
        # drop the NOTE block added earlier (it is superseded by HDR)
        if lines[i].startswith(OLD_NOTE_START):
            while i < len(lines) and lines[i].startswith("#"):
                i += 1
            continue
        m = re.match(r"^(TBbarQ|TbarBQ):$", lines[i])
        if m:
            out.append(HDR)
            out.append("# " + lines[i])
            i += 1
            # comment the indented body of this entry
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].strip() == ""):
                if lines[i].strip() == "":
                    break
                out.append("# " + lines[i])
                i += 1
            n += 1
            continue
        out.append(lines[i])
        i += 1
    p.write_text("\n".join(out))
    print("%s: commented out %d entries" % (p.name, n))
