import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# 1) PDF + alphaS as SHAPES (weights already exist: weight_lhe_pdfUp/Down, weight_lhe_alphaSUp/Down)
old_sh = """    - CMS_ctag2d_2022"""
new_sh = """    - CMS_ctag2d_2022
    # PDF and alphaS as per-event SHAPES rather than flat lnN. The weights are already in
    # the parquets (weight_lhe_pdf{Up,Down}, weight_lhe_alphaS{Up,Down}) -- lhepdf.py builds
    # the full 100-replica NNPDF31 Hessian envelope and the alphaS pair, and we were then
    # collapsing all of it to a flat number. HiggsDNA treats alphaS as a shape from
    # LHEPdfWeight[:,-1]/[:,-2]; hh2bbww carries a `pdf` shape shift. Retires the
    # xsec_hplusc_PDF (1.06) and alphaS_PDF (1.03) lnN rows below.
    - lhe_pdf
    - lhe_alphaS"""
assert old_sh in s
s = s.replace(old_sh, new_sh, 1)

# 2) retire the two lnN rows they replace
old_pdf = """    xsec_hplusc_PDF:     {hplusc: 1.06}"""
new_pdf = """    # RETIRED 2026-08-11 -> now the per-event `lhe_pdf` SHAPE (see shape_systematics).
    # Was a flat 1.06 on hplusc only; the shape covers every process and carries the
    # actual replica-to-replica structure.
    # xsec_hplusc_PDF:     {hplusc: 1.06}"""
assert old_pdf in s
s = s.replace(old_pdf, new_pdf, 1)

old_as = """    alphaS_PDF:          {hplusc: 1.03, higgsbkg: 1.03, st: 1.03, diboson: 1.03, vjets: 1.03}"""
new_as = """    # RETIRED 2026-08-11 -> now the per-event `lhe_alphaS` SHAPE (see shape_systematics).
    # Was the maximum of the AN's quoted 1-3% range applied flat to five processes.
    # alphaS_PDF:          {hplusc: 1.03, higgsbkg: 1.03, st: 1.03, diboson: 1.03, vjets: 1.03}"""
assert old_as in s
s = s.replace(old_as, new_as, 1)

# 3) BR(H->tautau) 1%, AN-23-102 Table 16 -- we have H->tautau samples and no nuisance
old_br = """    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}"""
new_br = """    BR_HtoWW:            {hplusc: 1.01, higgsbkg: 1.01}
    # AN-23-102 Table 16 lists BR(H->tautau) 1% alongside BR(H->WW). Our higgsbkg group
    # contains GluGluHto2Tau / VBFHToTauTau / W(+-)HTo2Tau / ttHtoTauTau, so the nuisance
    # applies there. Added 2026-08-11 (was missing).
    BR_Htautau:          {higgsbkg: 1.01}"""
assert old_br in s
s = s.replace(old_br, new_br, 1)

p.write_text(s)
print("step 2: lhe_pdf + lhe_alphaS as shapes; PDF/alphaS lnN retired; BR_Htautau added")
