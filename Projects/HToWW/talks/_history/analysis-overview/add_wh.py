import re, sys

path = 'analysis/filesets/2022postEE_nanov12.yaml'
src = open(path).read()

anchor = """WminusH_Wto2Q_Hto2Wto2L2Nu:
  era: mc
  query: WminusH_Wto2Q_Hto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-minlo-jhugen-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: WH
  key: whtoww
  xsec: 0.008719124529
"""

if anchor not in src:
    sys.exit("ANCHOR NOT FOUND -- aborting, no change made")

addition = anchor + """# --- Added 2026-08-12: the two missing W-decay/charge combinations. -------------
# The config previously had only WplusH(W->lnu) and WminusH(W->qq): one charge from
# each W decay mode, an arbitrary pairing that dropped the physically-matched
# partners. All four combinations exist in Run3Summer22EENanoAODv12 (verified via
# dasgoclient), so this was a config gap, not a sample-availability limit.
#
# WminusH_WtoLNu is the important one: leptonic W-H is the 3-lepton final state,
# the WH mode most likely to enter an e-mu selection, and by charge symmetry it
# contributes at a comparable rate to the WplusH(W->lnu) already included.
#
# xsec provenance: the two pre-existing values decompose consistently as
#   sigma(W+-H) x BR(H->WW->2l2nu) x BR(W->lnu | W->qq)
# with BR(W->lnu)=0.3258, BR(W->qq)=0.6741 (PDG), giving
#   sigma(W+H)=0.020335 pb, sigma(W-H)=0.012934 pb, ratio W+/W- = 1.572
# which is the expected 1.5-1.6 for pp at 13.6 TeV. The two values below are that
# same decomposition applied to the missing modes, so they share the existing
# normalisation convention rather than being an independent estimate.
WminusH_WtoLNu_Hto2Wto2L2Nu:
  era: mc
  query: WminusH_WtoLNu_Hto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-minlo-jhugen-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: WH
  key: whtoww
  xsec: 0.004214050
WplusH_Wto2Q_Hto2Wto2L2Nu:
  era: mc
  query: WplusH_Wto2Q_Hto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-minlo-jhugen-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: WH
  key: whtoww
  xsec: 0.013707745
# ------------------------------------------------------------------------------
"""

src = src.replace(anchor, addition, 1)
open(path, 'w').write(src)
print("EDIT APPLIED")
