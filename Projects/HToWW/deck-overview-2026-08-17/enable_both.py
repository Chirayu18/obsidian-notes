import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# ---- 1) per-channel binning: all five CRs -> yield-only (AN-24-091 Table 10) ----
old_bin = """  binning:
    edges: [0.0, 0.2, 0.3, 0.35, 0.40, 0.44, 0.48, 0.52, 0.56, 0.60, 1.0]"""
new_bin = """  binning:
    edges: [0.0, 0.2, 0.3, 0.35, 0.40, 0.44, 0.48, 0.52, 0.56, 0.60, 1.0]
    # PER-CHANNEL BINNING (make_combine_inputs_v2.py only; the original builder uses a
    # single global `edges` for every channel and ignores this key).
    # All five background CRs are collapsed to ONE bin = yield-only, keeping the 10-bin
    # shape in the SR. Two independent precedents:
    #   * AN-23-102 line 662 -- the top CR is deliberately yield-only
    #   * AN-24-091 Table 10 (Run 3 HH->bbWW) -- EVERY CR is literally 1 bin, SRs 10/6/3
    # Rationale: CR_tt is 87.9% pure over 1.56M events, so there is no useful shape there,
    # and a 10-bin shape in an argmax-defined CR is the artificial-constraint failure mode
    # of AN-23-102 section 7.2.1. It also removes the argmax channel-migration artifact
    # from five of the six channels (see 2026-08-11-jes-jer-bug-fixed).
    per_channel:
      CR_higgsbkg: [0.0, 1.0]
      CR_tt:       [0.0, 1.0]
      CR_st:       [0.0, 1.0]
      CR_diboson:  [0.0, 1.0]
      CR_vjets:    [0.0, 1.0]"""
assert old_bin in s, "binning anchor missing"
s = s.replace(old_bin, new_bin, 1)

# ---- 2) decouple datacard processes from MVA classes; split ggH out ----
old_pm_note = """    # NOTE 2026-08-11: splitting ggH out of higgsbkg here does NOT work and must not be
    # attempted by editing process_map alone. make_combine_inputs.py derives the datacard
    # processes from `combine.classes` (the 6 MVA output classes), NOT from process_map --
    # see lines ~389-391. A process_map key with no matching class is silently ignored, so
    # a `ggH:` entry DELETES those samples from the card (verified: SR total fell
    # 20664 -> 20561, exactly the ~103 ggH/ggZH events, and the flavor_composition_ggH row
    # became all dashes).
    # Doing the split properly requires either (a) a 7th MVA class, i.e. retraining, or
    # (b) decoupling datacard processes from argmax classes in make_combine_inputs.py.
    higgsbkg: [H+b, VBF, ZH, ggH, ggZH, ttHnonBB, ttHtoBB]"""
new_pm_note = """    # ggH SPLIT OUT 2026-08-11, enabled by `combine.processes` above and
    # make_combine_inputs_v2.py. The ORIGINAL builder derives datacard processes from
    # `combine.classes` and silently ignores unmatched process_map keys -- with it, this
    # split DELETES ggH/ggZH from the card (verified: SR total 20664 -> 20561 and the
    # flavor_composition_ggH row went all-dashes, build still exiting 0).
    # v2 validates the two lists against each other and raises instead.
    # Splitting lets the AN's real 50% apply to ggH alone rather than the 1.066 average a
    # merged group forces, and is the prerequisite for the 2POI fit.
    ggH:      [ggH, ggZH]
    higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]"""
assert old_pm_note in s, "process_map anchor missing"
s = s.replace(old_pm_note, new_pm_note, 1)

# declare the decoupled process list just above process_map
old_head = "  process_map:"
new_head = """  # DATACARD PROCESSES, decoupled from the MVA classes (make_combine_inputs_v2.py only;
  # the original builder ignores this key and uses `classes`). Channels stay one-per-class
  # -- that is what argmax means -- but a datacard process is just a row and need not be a
  # class, which is what lets ggH be split out WITHOUT retraining.
  processes: [hplusc, ggH, higgsbkg, tt, st, diboson, vjets]
  process_map:"""
assert old_head in s
s = s.replace(old_head, new_head, 1)

# ---- 3) rescope the lnN rows now that ggH is its own process ----
for a, b in [
    ("""    # Scaled to ggH's 13.1% share of the merged group (0.50*0.131 -> 1.066). This is an
    # approximation forced by the grouping; the real fix is the per-event `higgs_plus_c`
    # shape from the reprocessing campaign, which keys on gen-jet flavour and does not
    # care how processes are grouped.
    flavor_composition_ggH: {higgsbkg: 1.066}""",
     """    # Now that ggH is its own datacard process, the AN's FULL 50% applies to it alone --
    # no more 1.066 averaging over a merged group that is 87% not-ggH.
    # (When the reprocessing campaign lands, replace this with the per-event
    # `higgs_plus_c` shape and DELETE this line, or the two will double-count.)
    flavor_composition_ggH: {ggH: 1.50}"""),
    ("    xsec_higgsbkg:       {higgsbkg: 1.05}",
     "    xsec_higgsbkg:       {higgsbkg: 1.05, ggH: 1.05}"),
    ("    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}",
     "    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01, ggH: 1.01}"),
    ("    BR_Htautau:          {higgsbkg: 1.01}",
     "    BR_Htautau:          {higgsbkg: 1.01, ggH: 1.01}"),
    ("    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}",
     "    lumi_13p6TeV:        {hplusc: 1.014, higgsbkg: 1.014, ggH: 1.014, st: 1.014, diboson: 1.014, vjets: 1.014}"),
]:
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

p.write_text(s)
print("enabled: per-channel binning (5 CRs -> 1 bin) + ggH split")
