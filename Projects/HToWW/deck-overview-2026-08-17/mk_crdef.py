from pathlib import Path
import os
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
src = Path("analysis/workflows/hww_combine_fixed.yaml")
s = src.read_text()

s = s.replace("    root:     outputs/combine/v11_hplusc_v4.root",
              "    root:     outputs/combine/v11_hplusc_crdef.root")
s = s.replace("    datacard: outputs/combine/v11_hplusc_v4.txt",
              "    datacard: outputs/combine/v11_hplusc_crdef.txt")
s = s.replace("    workspace: v11_hplusc_v4.workspace.root",
              "    workspace: v11_hplusc_crdef.workspace.root")

anchor = "  # weight-based shape nuisances"
block = '''  # ------------------------------------------------------------------
  # Redefined control regions (2026-08-08). Applied ON TOP of the argmax
  # channel assignment, using columns already present in the scored MVA
  # parquets -- NO workflow re-run is needed.
  #
  # Motivation (Projects/HToWW/argmax-kinematics-2026-08-07/):
  #   The old top CR was mTl2>30 & mTll<=60, i.e. exactly the region where the
  #   v11 model never assigns argmax=signal (66 events, max P(hplusc)=0.358).
  #   It was also the LEAST pure of the candidates scanned: 80.4% true tt.
  #   argmax=tt & mll>100 gives 94.1% true-tt purity at 1.4x the yield.
  #
  #   CR_higgsbkg is bounded at mll<=100 so the two CRs stay disjoint.
  #
  # The SR is left untouched (argmax=hplusc, already mll<=100 by the model's
  # own upper wall) so SR and CRs remain disjoint by construction.
  channel_cuts:
    CR_tt:       "dilepton_mass > 100"
    CR_higgsbkg: "(dilepton_mass > 72) & (dilepton_mass <= 100)"
'''
assert anchor in s
s = s.replace(anchor, block + anchor, 1)
Path("analysis/workflows/hww_combine_crdef.yaml").write_text(s)
print("wrote hww_combine_crdef.yaml")
