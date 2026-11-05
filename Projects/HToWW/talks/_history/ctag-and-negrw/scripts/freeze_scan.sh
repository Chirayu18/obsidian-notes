#!/bin/bash
# Group-by-group freeze scan on the current datacard, grouped to match AN-23-102 Table 17.
# |dr|/r for a group = sqrt(max(0, sigma_full^2 - sigma_frozen^2)) / r, using the
# 68% band half-width from AsymptoticLimits as sigma.
set -e
TXT="${1:?usage: freeze_scan.sh <datacard.txt> <tag>}"
TAG="${2:-fz}"
cd /afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4/src
eval "$(scramv1 runtime -sh)"
cd "$(dirname "$TXT")"
B=$(basename "$TXT")
WS="${TAG}.ws.root"
text2workspace.py "$B" -o "$WS" >/dev/null 2>&1

# extract median + 16/84 to build a symmetric-ish sigma
run(){  # $1 = name, $2... = extra args
  local nm="$1"; shift
  combine -M AsymptoticLimits "$WS" --run blind -t -1 -n "${TAG}${nm}" "$@" 2>&1 | \
    awk '/Expected 16.0/{lo=$NF} /Expected 50.0/{md=$NF} /Expected 84.0/{hi=$NF} END{print md, lo, hi}'
}

echo "group|median|lo68|hi68"
echo "FULL|$(run _full)"
echo "STATONLY|$(run _stat --freezeParameters allConstrainedNuisances)"
echo "MCSTAT|$(run _mcs --freezeParameters 'rgx{prop_bin.*}')"
echo "SIGNAL_THEORY|$(run _sig --freezeParameters xsec_hplusc_PDF,xsec_hplusc_4FS_5FS,BR_HtoWW)"
echo "BKG_HIGGS|$(run _bh --freezeParameters xsec_higgsbkg,flavor_composition_ggH)"
echo "OTHER_BKG|$(run _ob --freezeParameters xsec_st,xsec_diboson,xsec_vjets,alphaS_PDF)"
echo "THEORY_SHAPE|$(run _th --freezeParameters 'rgx{scalevar.*},rgx{ps_.*}')"
echo "PILEUP|$(run _pu --freezeParameters pileup)"
echo "LEPTON|$(run _lep --freezeParameters 'rgx{muon_.*},rgx{electron_.*},rgx{CMS_scale_[em]_2022},rgx{CMS_res_[em]_2022}')"
echo "JES_JER|$(run _jet --freezeParameters CMS_scale_j_2022,CMS_res_j_2022)"
echo "CHARMTAG|$(run _ct --freezeParameters CMS_ctag2d_2022)"
echo "NEGRW|$(run _nrw --freezeParameters CMS_negrw_vjets)"
echo "TTNORM|$(run _ttn --freezeParameters rate_tt)"
echo "LUMI|$(run _lum --freezeParameters lumi_13p6TeV)"
