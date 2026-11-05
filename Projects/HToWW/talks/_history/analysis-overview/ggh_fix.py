import re, pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()
old = """    # Higgs heavy-flavour composition (AN-23-102 7.1: 50% on the ggH yield). ggH is ~80%
    # of the merged higgsbkg here, so 0.5*0.8 ~= 0.40 effective. PLACEHOLDER until ggH is
    # split out of higgsbkg (then apply the full 1.50 to the ggH component only).
    flavor_composition_ggH: {higgsbkg: 1.40}"""
new = """    # Higgs heavy-flavour composition (AN-23-102 7.1: 50% on the ggH yield).
    # MEASURED 2026-08-11: ggH is 13.1% of the merged higgsbkg SR yield -- NOT ~80% as an
    # earlier comment here claimed (the rest is VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%,
    # ttH/H+b/Htautau 4.6%). Effective size is therefore 0.50*0.131 = 0.066 -> 1.066, not
    # 1.40. The 1.40 was over-penalising ~87% of the group by a ggH-specific uncertainty;
    # correcting it moved the expected limit 1185 -> 1164.
    # STILL A PLACEHOLDER: the right fix is to split ggH out of higgsbkg and apply the full
    # 1.50 to the ggH component alone (AN-23-102 / strategy note section 4), which also
    # enables the 2POI fit. Until then this scoped value is the honest approximation.
    flavor_composition_ggH: {higgsbkg: 1.066}"""
assert old in s, "anchor not found"
p.write_text(s.replace(old, new))
print("patched")
