import re, shutil, datetime, sys

P = "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/filesets/2022postEE_nanov12.yaml"
bak = P + ".bak_pre_wjets_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(P, bak)
print("backup:", bak)

src = open(P).read()

# Locate the inclusive block and replace it in place, preserving surrounding text.
old = """WtoLNu_2Jets:
  era: mc
  query: WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: V+Jets 
  key: v+jets
  xsec: 67710.0
"""
if old not in src:
    print("FATAL: inclusive block not found verbatim"); sys.exit(1)

new = """# W+jets: jet-binned NLO aMCatNLO (0J/1J/2J), replacing the inclusive
# WtoLNu-2Jets sample (xsec 67710 pb, 281.5M events).
#
# AN-23-102 sec 2.3 rejects the inclusive NLO sample: "not used in this study
# since it has 5 times smaller size than LO and with large fraction of negative
# weights". The jet-binned samples are the AN's NLO choice.
#
# Cross sections from XSDB (13.6 TeV, Run3Summer22EE), retrieved 2026-08-13.
# Sum = 68821 pb vs the inclusive 67710 pb (+1.6%, normal NLO merging spread).
# NOTE XSDB labels these accuracy="LO" and matrix_generator="Pythia8"; both are
# wrong (auto-populated). amcatnloFXFX is NLO -- confirmed by the 10-35%
# negative-weight fractions, impossible at LO. cross_section is the reliable field.
#
# Every 0J event has LHE_Vpt < 100 GeV (measured), so these three are
# self-contained: no LHE_Vpt cut needed and no overlap with the PTLNu-* samples,
# which cover W-pT > 100 GeV and are NOT included here (see the full AN stitch).
#
# Measured effective statistics (n_eff/N x nevents / xsec):
#   inclusive    1.91 /fb     jet-binned combined  29.82 /fb  ->  15.6x gain
WtoLNu_2Jets_0J:
  era: mc
  query: WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3/NANOAODSIM
  process: V+Jets
  key: v+jets
  xsec: 55760.0
WtoLNu_2Jets_1J:
  era: mc
  query: WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: V+Jets
  key: v+jets
  xsec: 9529.0
WtoLNu_2Jets_2J:
  era: mc
  query: WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM
  process: V+Jets
  key: v+jets
  xsec: 3532.0
"""
open(P, "w").write(src.replace(old, new))
print("written")

# --- verify by YAML round-trip ---
import yaml
d = yaml.safe_load(open(P))
b = yaml.safe_load(open(bak))
print(f"entries: {len(b)} -> {len(d)}")
added = set(d) - set(b); removed = set(b) - set(d)
print("added  :", sorted(added))
print("removed:", sorted(removed))
changed = [k for k in set(d) & set(b) if d[k] != b[k]]
print("changed existing entries:", changed if changed else "NONE")
tot = sum(v["xsec"] for k, v in d.items() if v.get("key") == "v+jets")
print(f"v+jets xsec sum: {tot} pb")
for k, v in d.items():
    if v.get("key") == "v+jets":
        print(f"   {k:22s} {v['xsec']:>9} pb")
