import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# 1) enable the weight
old = "    toppTWeight: true"
new = """    toppTWeight: true
    # Higgs + heavy-flavour composition, ported from HiggsDNA's Higgs_plus_HF_syst.
    # Per-event +-50% on ggH/VBF events containing >=1 heavy-flavour GEN jet
    # (pt>25, |eta|<2.5). Replaces the mis-scoped flat `flavor_composition_ggH`
    # lnN -- see the lnN block below.
    higgsHFWeight: true
    higgsHFFlavour: c"""
assert old in s
s = s.replace(old, new, 1)

# 2) retire the lnN, pointing at the replacement
old_lnn = """    # Higgs heavy-flavour composition (AN-23-102 7.1: 50% on the ggH yield).
    # MEASURED 2026-08-11: ggH is 13.1% of the merged higgsbkg SR yield -- NOT ~80% as an
    # earlier comment here claimed (the rest is VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%,
    # ttH/H+b/Htautau 4.6%). Effective size is therefore 0.50*0.131 = 0.066 -> 1.066, not
    # 1.40. The 1.40 was over-penalising ~87% of the group by a ggH-specific uncertainty;
    # correcting it moved the expected limit 1185 -> 1164.
    # STILL A PLACEHOLDER: the right fix is to split ggH out of higgsbkg and apply the full
    # 1.50 to the ggH component alone (AN-23-102 / strategy note section 4), which also
    # enables the 2POI fit. Until then this scoped value is the honest approximation.
    flavor_composition_ggH: {higgsbkg: 1.066}"""
new_lnn = """    # Higgs heavy-flavour composition (AN-23-102 7.1 / Table 16: 50% on the ggH yield).
    # RETIRED as an lnN 2026-08-11 -- superseded by the per-event `higgsHFWeight`
    # (analysis/corrections/higgs_hf.py, ported from HiggsDNA's Higgs_plus_HF_syst),
    # which appears in the card as the `higgs_plus_c` SHAPE nuisance.
    #
    # Why the lnN was wrong: it sat on the whole merged higgsbkg group, but ggH is only
    # 13.1% of that group's SR yield (VBF 29.0%, ggZH 23.3%, ZH 21.0%, WH 9.1%, rest 4.6%).
    # A flat lnN therefore either over-penalises the other 87% (the original 1.40) or has
    # to be watered down to an effective average (the 1.066 stopgap, worth 1185 -> 1164) --
    # and either way it cannot produce the shape effect a real HF uncertainty has.
    # The per-event version keys on gen-jet flavour, so the grouping stops mattering.
    # NOTE: only active once the reprocessing campaign has produced the new weight column;
    # until then neither this nor higgs_plus_c is in the card.
    # flavor_composition_ggH: {higgsbkg: 1.066}   # <- retired, see above"""
assert old_lnn in s
s = s.replace(old_lnn, new_lnn, 1)

# 3) add the shape nuisance
old_sh = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt"""
new_sh = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt
    # ggH/VBF heavy-flavour composition, per-event (replaces flavor_composition_ggH lnN)
    - higgs_plus_c"""
assert old_sh in s
s = s.replace(old_sh, new_sh, 1)

p.write_text(s)
print("patched yaml: higgsHFWeight on, lnN retired, higgs_plus_c shape added")
