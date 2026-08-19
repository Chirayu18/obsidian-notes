import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()
old = "    # flavor_composition_ggH: {higgsbkg: 1.066}   # <- retired, see above"
new = """    # INTERIM: re-enabled 2026-08-11 so the card keeps a ggH+HF uncertainty until the
    # reprocessing campaign produces the per-event `higgs_plus_c` weight. REMOVE this
    # line (and keep higgs_plus_c in shape_systematics) once the campaign has run --
    # having both would double-count.
    flavor_composition_ggH: {higgsbkg: 1.066}"""
assert old in s
s = s.replace(old, new, 1)

# higgs_plus_c cannot be built yet -> comment it out of the shape list for the interim card
old_sh = """    # ggH/VBF heavy-flavour composition, per-event (replaces flavor_composition_ggH lnN)
    - higgs_plus_c"""
new_sh = """    # ggH/VBF heavy-flavour composition, per-event (replaces flavor_composition_ggH lnN).
    # COMMENTED OUT until the reprocessing campaign produces weight_higgs_plus_c; the
    # interim lnN above covers it meanwhile. Swap the two when the campaign lands.
    # - higgs_plus_c"""
assert old_sh in s
s = s.replace(old_sh, new_sh, 1)

# same for top_pt -- no weight column yet
old_tp = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt"""
new_tp = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight").
    # COMMENTED OUT until the reprocessing campaign produces weight_top_pt.
    # - top_pt"""
assert old_tp in s
s = s.replace(old_tp, new_tp, 1)
p.write_text(s)
print("step 1: ggH lnN restored; top_pt and higgs_plus_c parked until reprocess")
