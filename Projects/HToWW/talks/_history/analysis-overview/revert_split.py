import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

old = """    ggH:      [ggH, ggZH]
    higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]"""
new = """    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]"""
assert old in s
s = s.replace(old, new, 1)

# the split comment is now wrong -- replace with the finding
old_c = """    # higgsbkg SPLIT 2026-08-11. Was one merged group of 7 samples, which made the
    # ggH+heavy-flavour uncertainty impossible to scope: ggH is only 13.1% of the merged
    # SR yield (VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%, rest 4.6%), so a flat lnN either
    # over-penalised the other 87% or had to be watered down to an average.
    # Splitting lets the AN's 50% apply to ggH alone, and is the prerequisite for the
    # 2POI fit (AN-23-102 v10 splits bkg-H into bkg-H+c / bkg-H+notc "due to shape
    # differences"). Config-only -- the argmax channels are unchanged, this only regroups
    # datacard rows."""
new_c = """    # NOTE 2026-08-11: splitting ggH out of higgsbkg here does NOT work and must not be
    # attempted by editing process_map alone. make_combine_inputs.py derives the datacard
    # processes from `combine.classes` (the 6 MVA output classes), NOT from process_map --
    # see lines ~389-391. A process_map key with no matching class is silently ignored, so
    # a `ggH:` entry DELETES those samples from the card (verified: SR total fell
    # 20664 -> 20561, exactly the ~103 ggH/ggZH events, and the flavor_composition_ggH row
    # became all dashes).
    # Doing the split properly requires either (a) a 7th MVA class, i.e. retraining, or
    # (b) decoupling datacard processes from argmax classes in make_combine_inputs.py."""
assert old_c in s
s = s.replace(old_c, new_c, 1)

# restore the lnN scoping to higgsbkg
for a, b in [
    ("""    # Now scoped to the ggH process itself, so the AN's FULL 50% applies rather than the
    # 1.066 average that a merged group forced. (When the reprocessing campaign lands,
    # replace this with the per-event `higgs_plus_c` shape and delete this line.)
    flavor_composition_ggH: {ggH: 1.50}""",
     """    # Scaled to ggH's 13.1% share of the merged group (0.50*0.131 -> 1.066). This is an
    # approximation forced by the grouping; the real fix is the per-event `higgs_plus_c`
    # shape from the reprocessing campaign, which keys on gen-jet flavour and does not
    # care how processes are grouped.
    flavor_composition_ggH: {higgsbkg: 1.066}"""),
    ("    xsec_higgsbkg:       {higgsbkg: 1.05, ggH: 1.05}",
     "    xsec_higgsbkg:       {higgsbkg: 1.05}"),
    ("    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01, ggH: 1.01}",
     "    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}"),
    ("    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, ggH: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}",
     "    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}"),
]:
    assert a in s, a[:60]
    s = s.replace(a, b, 1)

p.write_text(s)
print("REVERTED the higgsbkg split; lnN rescoped to higgsbkg")
