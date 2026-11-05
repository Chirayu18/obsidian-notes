import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

old = """  process_map:
    hplusc:   [H+c]
    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]"""
new = """  process_map:
    hplusc:   [H+c]
    # higgsbkg SPLIT 2026-08-11. Was one merged group of 7 samples, which made the
    # ggH+heavy-flavour uncertainty impossible to scope: ggH is only 13.1% of the merged
    # SR yield (VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%, rest 4.6%), so a flat lnN either
    # over-penalised the other 87% or had to be watered down to an average.
    # Splitting lets the AN's 50% apply to ggH alone, and is the prerequisite for the
    # 2POI fit (AN-23-102 v10 splits bkg-H into bkg-H+c / bkg-H+notc "due to shape
    # differences"). Config-only -- the argmax channels are unchanged, this only regroups
    # datacard rows.
    ggH:      [ggH, ggZH]
    higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]"""
assert old in s
s = s.replace(old, new, 1)

# scope the ggH+HF uncertainty to the ggH process now that it exists
old_ggh = """    flavor_composition_ggH: {higgsbkg: 1.066}"""
new_ggh = """    # Now scoped to the ggH process itself, so the AN's FULL 50% applies rather than the
    # 1.066 average that a merged group forced. (When the reprocessing campaign lands,
    # replace this with the per-event `higgs_plus_c` shape and delete this line.)
    flavor_composition_ggH: {ggH: 1.50}"""
assert old_ggh in s
s = s.replace(old_ggh, new_ggh, 1)

# the other higgsbkg-scoped lnN rows must also cover the new ggH process
for old_row, new_row in [
    ("    xsec_higgsbkg:       {higgsbkg: 1.05}",
     "    xsec_higgsbkg:       {higgsbkg: 1.05, ggH: 1.05}"),
    ("    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}",
     "    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01, ggH: 1.01}"),
    ("    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}",
     "    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, ggH: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}"),
]:
    assert old_row in s, old_row
    s = s.replace(old_row, new_row, 1)

p.write_text(s)
print("step 3: higgsbkg split into ggH + higgsbkg; lnN rows rescoped")
