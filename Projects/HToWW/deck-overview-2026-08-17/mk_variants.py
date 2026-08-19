"""Create the two c-jet-acceptance study workflows from hww_MVA.yaml.

  hww_MVA_nocjet   -- no charm-tag requirement at all: cjets = all good jets
                      (pt>20, |eta|<2.4, tightlepveto, dR>0.4). >=1 JET still required
                      so cjet_cand_* features stay defined.
  hww_MVA_looseWP  -- charm tag relaxed medium -> loose (CvL 0.160->0.054,
                      CvB 0.304->0.182).

Everything else (features, categories, corrections, negrw) is left identical to
hww_MVA so the comparison is clean.
"""
from pathlib import Path
import os
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
src = Path("analysis/workflows/hww_MVA.yaml")
base = src.read_text()

CTAG_LINE = "      - working_points.jet_ctagging(events, 'medium', year)\n"
assert CTAG_LINE in base, "ctag line not found"

# ---- variant 1: no c-tag requirement at all ----
nocjet = base.replace(CTAG_LINE, "")
assert "jet_ctagging" not in nocjet
hdr = """# AUTO-GENERATED from hww_MVA.yaml -- c-jet acceptance study (2026-08-08).
# NO charm-tag requirement: `cjets` is every good jet (pt>20, |eta|<2.4,
# tightlepveto, dR(lep)>0.4). The >=1 requirement is kept so candidate_cjet and the
# cjet_cand_* MVA features stay defined; the network is expected to learn the charm
# boundary itself from the continuous CvL/CvB it already receives as features.
# Motivation: Projects/HToWW/argmax-kinematics-2026-08-07/ -- medium WP keeps only
# 23.1% of signal, and CvL carries the H+c-vs-ggH separation (AUC 0.731) while CvB
# does not (0.551).
"""
Path("analysis/workflows/hww_MVA_nocjet.yaml").write_text(hdr + nocjet)

# ---- variant 2: relaxed WP ----
loose = base.replace(CTAG_LINE,
                     "      - working_points.jet_ctagging(events, 'loose', year)\n")
assert "'loose'" in loose
hdr2 = """# AUTO-GENERATED from hww_MVA.yaml -- c-jet acceptance study (2026-08-08).
# Charm tag RELAXED medium -> loose:
#   medium: CvL>0.160  CvB>0.304
#   loose : CvL>0.054  CvB>0.182   (PNet, 2022postEE)
# Middle point between the current selection and hww_MVA_nocjet.
"""
Path("analysis/workflows/hww_MVA_looseWP.yaml").write_text(hdr2 + loose)

for f in ("hww_MVA_nocjet.yaml", "hww_MVA_looseWP.yaml"):
    p = Path("analysis/workflows") / f
    t = p.read_text()
    print(f"{f}: {len(t.splitlines())} lines, "
          f"jet_ctagging={'YES' if 'jet_ctagging' in t else 'NO'}")
