"""Three c-jet acceptance study workflows, all derived from hww_combine_2dcat.yaml.

  1) hww_2dcat_nocjet     -- no charm-tag requirement at all
  2) hww_2dcat_looseWP    -- charm tag medium -> loose
  3) hww_2dcat_nocjet_kin -- no charm tag, cjet features get -1 when absent,
                             PLUS the mll/mTll/mTl2 signal selections in base
"""
from pathlib import Path
import os
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
W = Path("analysis/workflows")
base = (W / "hww_combine_2dcat.yaml").read_text()

CTAG = "      - working_points.jet_ctagging(events, 'medium', year)\n"
assert CTAG in base

def repoint(s, tag):
    s = s.replace("outputs/combine/v11_hplusc_2dcat.root",  f"outputs/combine/v11_hplusc_{tag}.root")
    s = s.replace("outputs/combine/v11_hplusc_2dcat.txt",   f"outputs/combine/v11_hplusc_{tag}.txt")
    s = s.replace("v11_hplusc_2dcat.workspace.root",        f"v11_hplusc_{tag}.workspace.root")
    return s

# ---------------- 1) no c-tag ----------------
v1 = base.replace(CTAG, "")
assert "jet_ctagging" not in v1
v1 = repoint(v1, "nocjet")
h1 = """# AUTO-GENERATED from hww_combine_2dcat.yaml -- c-jet acceptance study (2026-08-08).
# VARIANT 1: NO charm-tag requirement at all. `cjets` = every good jet
# (pt>20, |eta|<2.4, tightlepveto, dR(lep)>0.4). `atleast_one_cjet` therefore means
# ">=1 good JET", so candidate_cjet and the cjet_cand_* features stay defined.
# Motivation: Projects/HToWW/argmax-kinematics-2026-08-07/ -- the medium WP keeps only
# 23.1% of signal; CvL carries the H+c-vs-ggH separation (AUC 0.731), CvB does not (0.551).
"""
(W / "hww_2dcat_nocjet.yaml").write_text(h1 + v1)

# ---------------- 2) loose WP ----------------
v2 = base.replace(CTAG, "      - working_points.jet_ctagging(events, 'loose', year)\n")
assert "'loose'" in v2
v2 = repoint(v2, "looseWP")
h2 = """# AUTO-GENERATED from hww_combine_2dcat.yaml -- c-jet acceptance study (2026-08-08).
# VARIANT 2: charm tag RELAXED medium -> loose.
#   medium: CvL>0.160  CvB>0.304
#   loose : CvL>0.054  CvB>0.182   (PNet, 2022postEE)
"""
(W / "hww_2dcat_looseWP.yaml").write_text(h2 + v2)

# ---------------- 3) no c-tag + kinematic cuts + (-1) sentinels ----------------
v3 = base.replace(CTAG, "")
assert "jet_ctagging" not in v3

# -1 sentinel for the four candidate-c-jet features when no c-jet is present
SUBS = [
 ("      expression: ak.pad_none(objects['candidate_cjet'], target=1).hadronFlavour\n",
  "      expression: ak.fill_none(ak.pad_none(objects['candidate_cjet'], target=1).hadronFlavour, -1)\n"),
 ("      expression: ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvL\n",
  "      expression: ak.fill_none(ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvL, -1)\n"),
 ("      expression: ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvB\n",
  "      expression: ak.fill_none(ak.pad_none(objects['candidate_cjet'], target=1).btagPNetCvB, -1)\n"),
 ("      expression: objects['candidate_cjet'].pt\n",
  "      expression: ak.fill_none(ak.pad_none(objects['candidate_cjet'], target=1).pt, -1)\n"),
]
for old, new in SUBS:
    assert old in v3, f"missing: {old!r}"
    v3 = v3.replace(old, new)

# add the kinematic signal selections to the base category
OLDCAT = """  categories:
    base:
      - atleast_one_goodvertex
      - lumimask
      - met_filters
      - trigger
      - met_45
      - one_ll_pair
      - one_muon_one_electron
      - atleast_one_cjet
"""
NEWCAT = """  categories:
    base:
      - atleast_one_goodvertex
      - lumimask
      - met_filters
      - trigger
      - met_45
      - one_ll_pair
      - one_muon_one_electron
      - atleast_one_cjet
      # kinematic selections moved INTO the base category for this variant: they buy
      # back the tt/DY volume that dropping the charm tag re-admits. Both are already
      # defined above (mTl2>30 & mTll>60, and mll<=72).
      - transverse_mass_signal
      - dilepton_mass_signal
"""
assert OLDCAT in v3
v3 = v3.replace(OLDCAT, NEWCAT)
v3 = repoint(v3, "nocjet_kin")
h3 = """# AUTO-GENERATED from hww_combine_2dcat.yaml -- c-jet acceptance study (2026-08-08).
# VARIANT 3: no charm-tag requirement, PLUS
#   (a) -1 sentinel for the candidate-c-jet features when no c-jet is present
#       (ak.fill_none(..., -1) on hadronFlavour / CvL / CvB / pt), and
#   (b) the mll/mTll/mTl2 signal selections added to the base category
#       (transverse_mass_signal: mTl2>30 & mTll>60; dilepton_mass_signal: mll<=72).
# These kinematic cuts keep 84.5% of signal while removing 73% of background, so they
# offset the extra tt/DY volume admitted by dropping the charm tag.
# NOTE: with dilepton_mass_signal in base, the high-mll CR is empty by construction --
# expected for this test, which is about training acceptance, not the CR fit.
"""
(W / "hww_2dcat_nocjet_kin.yaml").write_text(h3 + v3)

for f in ("hww_2dcat_nocjet.yaml", "hww_2dcat_looseWP.yaml", "hww_2dcat_nocjet_kin.yaml"):
    t = (W / f).read_text()
    print(f"{f:<30s} ctag={'YES' if 'jet_ctagging' in t else 'NO ':<3s} "
          f"fill_none(-1)={t.count('-1)')} "
          f"kin_in_base={'YES' if '- transverse_mass_signal' in t else 'NO'}")
