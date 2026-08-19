import sys

p = "analysis/workflows/hww_ctag_compare.yaml"
s = open(p).read()

# ---- 1. event-level charm-tag WP selections -------------------------------
old_sel = '    transverse_mass_signal: ak.all((objects["mTl2"] > 30) & (objects["mTll"] > 60), axis=1)'
new_sel = '''    # Event-level charm-tag WPs. `cjets` is UNTAGGED in this workflow (good jets only),
    # so the WP is applied as an event selection rather than an object cut -- that is
    # what lets medium, loose and no-tag coexist as categories over one collection.
    # Thresholds mirror working_points/utils.py::get_ctag_mask (pnet tagger, nanov12):
    #   medium: CvL > 0.160, CvB > 0.304
    #   loose : CvL > 0.054, CvB > 0.182
    cjet_medium_wp: ak.any((objects["cjets"].btagPNetCvL > 0.160) & (objects["cjets"].btagPNetCvB > 0.304), axis=1)
    cjet_loose_wp: ak.any((objects["cjets"].btagPNetCvL > 0.054) & (objects["cjets"].btagPNetCvB > 0.182), axis=1)
''' + old_sel

assert s.count(old_sel) == 1, "sel anchor count=%d" % s.count(old_sel)
s = s.replace(old_sel, new_sel)

# ---- 2. four categories ---------------------------------------------------
COMMON = """      - atleast_one_goodvertex
      - lumimask
      - met_filters
      - trigger
      - met_45
      - one_ll_pair
      - one_muon_one_electron
      - atleast_one_cjet"""

old_cat = """  categories:
    base:
""" + COMMON + """
      # kinematic selections moved INTO the base category for this variant: they buy
      # back the tt/DY volume that dropping the charm tag re-admits. Both are already
      # defined above (mTl2>30 & mTll>60, and mll<=72).
      - transverse_mass_signal
      - dilepton_mass_signal"""

new_cat = """  # FOUR categories evaluated over ONE untagged jet collection. They deliberately
  # OVERLAP (medium is a subset of loose; kin overlaps both) -- the point is a
  # like-for-like comparison of how much SIGNAL and how much CR population each
  # option keeps, not a partition of the data.
  categories:
    base:
""" + COMMON + """
    base_medium_cjet:
""" + COMMON + """
      - cjet_medium_wp
    base_loose_cjet:
""" + COMMON + """
      - cjet_loose_wp
    base_kin_nocjet:
""" + COMMON + """
      - transverse_mass_signal
      - dilepton_mass_signal"""

assert s.count(old_cat) == 1, "cat anchor count=%d" % s.count(old_cat)
s = s.replace(old_cat, new_cat)

# ---- 3. yield study: no JES/JER shift trees -------------------------------
s = s.replace("  object_shifts: true", "  object_shifts: false")

open(p, "w").write(s)
print("PATCHED OK")
