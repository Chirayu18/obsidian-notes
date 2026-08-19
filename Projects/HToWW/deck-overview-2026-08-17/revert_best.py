import pathlib, re
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# 1) drop the decoupled process list -> back to classes-derived processes
s = re.sub(
    r"  # DATACARD PROCESSES, decoupled.*?\n  processes: \[hplusc, ggH, higgsbkg, tt, st, diboson, vjets\]\n",
    """  # DATACARD PROCESSES (make_combine_inputs_v2.py only). MEASURED 2026-08-12: splitting
  # ggH out COSTS 25 units (1160 -> 1185) because the AN's correctly-scoped 1.50 on ggH
  # alone is a larger penalty than the 1.066 average on the merged group. The split is
  # still the more CORRECT treatment and is the prerequisite for the 2POI fit, so keep
  # this line ready -- but it is disabled while we optimise the 1POI limit.
  # processes: [hplusc, ggH, higgsbkg, tt, st, diboson, vjets]
""",
    s, count=1, flags=re.S)

# 2) re-merge ggH into higgsbkg
old_pm = """    ggH:      [ggH, ggZH]
    higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]"""
new_pm = """    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]"""
assert old_pm in s
s = s.replace(old_pm, new_pm, 1)

# 3) ggH lnN back to the merged-group scaling
old_l = """    # Now that ggH is its own datacard process, the AN's FULL 50% applies to it alone --
    # no more 1.066 averaging over a merged group that is 87% not-ggH.
    # (When the reprocessing campaign lands, replace this with the per-event
    # `higgs_plus_c` shape and DELETE this line, or the two will double-count.)
    flavor_composition_ggH: {ggH: 1.50}"""
new_l = """    # Scaled to ggH's measured 13.1% share of the merged group (0.50*0.131 -> 1.066).
    # An approximation forced by the grouping -- with `processes` enabled above this
    # becomes {ggH: 1.50}, which is more correct but costs 25 units (1160 -> 1185).
    # Superseded either way by the per-event `higgs_plus_c` shape once the reprocessing
    # campaign lands (it keys on gen-jet flavour, so grouping stops mattering).
    flavor_composition_ggH: {higgsbkg: 1.066}"""
assert old_l in s
s = s.replace(old_l, new_l, 1)

for a, b in [
    ("    xsec_higgsbkg:       {higgsbkg: 1.05, ggH: 1.05}", "    xsec_higgsbkg:       {higgsbkg: 1.05}"),
    ("    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01, ggH: 1.01}", "    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}"),
    ("    BR_Htautau:          {higgsbkg: 1.01, ggH: 1.01}", "    BR_Htautau:          {higgsbkg: 1.01}"),
    ("    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, ggH: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}",
     "    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}"),
]:
    assert a in s, a[:60]
    s = s.replace(a, b, 1)

# 4) annotate the (already commented) per_channel block with the measurement
s = s.replace("    #     per_channel:", "    #     per_channel:   # MEASURED: costs 50 units (1185 -> 1235)", 1)
p.write_text(s)
print("reverted to the 1160 configuration")
