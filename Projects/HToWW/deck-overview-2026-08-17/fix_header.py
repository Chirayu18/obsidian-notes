p = "analysis/workflows/hww_ctag_compare.yaml"
s = open(p).read()

old = """# AUTO-GENERATED from hww_combine_2dcat.yaml -- c-jet acceptance study (2026-08-08).
# VARIANT 3: no charm-tag requirement, PLUS
#   (a) -1 sentinel for the candidate-c-jet features when no c-jet is present
#       (ak.fill_none(..., -1) on hadronFlavour / CvL / CvB / pt), and
#   (b) the mll/mTll/mTl2 signal selections added to the base category
#       (transverse_mass_signal: mTl2>30 & mTll>60; dilepton_mass_signal: mll<=72).
# These kinematic cuts keep 84.5% of signal while removing 73% of background, so they
# offset the extra tt/DY volume admitted by dropping the charm tag.
# NOTE: with dilepton_mass_signal in base, the high-mll CR is empty by construction --
# expected for this test, which is about training acceptance, not the CR fit."""

new = """# c-tag OPTION COMPARISON -- 2022preEE (2026-08-09).
#
# Question: which c-jet handling keeps the most signal WITHOUT emptying the control
# regions? The kinematic cuts (hww_2dcat_nocjet_kin) recover signal but put mll<=72 and
# the mT cuts in `base`, which depopulates the CRs -- the thing we actually need to keep.
#
# So: ONE untagged jet collection, FOUR overlapping categories evaluated side by side:
#   base             -- >=1 good jet, no c-tag, no kinematic cuts (the denominator)
#   base_medium_cjet -- + medium PNet WP  (CvL>0.160, CvB>0.304)  = the current analysis
#   base_loose_cjet  -- + loose  PNet WP  (CvL>0.054, CvB>0.182)
#   base_kin_nocjet  -- + mTl2>30 & mTll>60 & mll<=72, no c-tag
# Categories OVERLAP by construction (medium is a subset of loose); this is a
# comparison, not a partition.
#
# preEE rather than postEE: 11 of the postEE signal NanoAODs are currently unreadable
# on IIHE (see stuck_signal_UNREADABLE.txt), while preEE v4 reads cleanly.
#
# object_shifts: false -- this is a yield/occupancy count, JES/JER shift trees are not
# needed and would multiply the job count."""

assert s.count(old) == 1, "header anchor count=%d" % s.count(old)
s = s.replace(old, new)
open(p, "w").write(s)
print("HEADER OK")
