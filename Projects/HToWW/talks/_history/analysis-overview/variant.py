import pathlib, re
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# strip whatever commented per_channel block is there, then insert the variant
s = re.sub(r"\n    #\s*per_channel:.*?(?=\n  [a-z_]+:)", "\n", s, count=1, flags=re.S)
s = re.sub(r"\n    per_channel:\n(      CR_\w+:\s*\[[^\]]*\]\n)+", "\n", s, count=1)

anchor = "    edges: [0.0, 0.2, 0.3, 0.35, 0.40, 0.44, 0.48, 0.52, 0.56, 0.60, 1.0]"
block = anchor + """
    # PER-CHANNEL BINNING (make_combine_inputs_v2.py only; the original builder uses one
    # global `edges` for every channel and ignores this key).
    #
    # VARIANT under test 2026-08-12: yield-only for the three TOP-DOMINATED CRs, keeping
    # 10-bin shapes in CR_tt and CR_vjets.
    #
    # Measured top purity (tt + single-top, as a fraction of the channel total):
    #   CR_tt        99.1%    <- keep shape: the primary top CR, pins rate_tt
    #   CR_st        97.6%    <- yield-only: a second slice of the SAME top phase space
    #   CR_higgsbkg  92.9%    <- yield-only: a third slice of it
    #   CR_diboson   83.5%    <- yield-only: mostly top, only 690 actual diboson
    #   CR_vjets     53.7%    <- keep shape: the only genuinely V+jets-enriched CR (3979)
    #
    # Rationale: three of the five CRs are predominantly TOP regions differing only in
    # which top-like class the network picked, so their shapes are largely redundant with
    # CR_tt. Collapsing all five cost 50 units; this keeps the two that carry distinct
    # information. (Single-top is physically tt-like -- AN-23-102's cut-based top CR does
    # not separate them either.)
    per_channel:
      CR_st:       [0.0, 1.0]
      CR_higgsbkg: [0.0, 1.0]
      CR_diboson:  [0.0, 1.0]"""
assert anchor in s
s = s.replace(anchor, block, 1)
p.write_text(s)
print("variant enabled: CR_st / CR_higgsbkg / CR_diboson -> 1 bin; CR_tt + CR_vjets keep 10")
