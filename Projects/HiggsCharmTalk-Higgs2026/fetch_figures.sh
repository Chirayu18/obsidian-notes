#!/usr/bin/env bash
# Re-download the public CMS figures used by the talk and crop them to their bounding box.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p figures; cd figures
while read -r f u; do [ -s "$f" ] || curl -sfL -o "$f" "$u"; done <<EOF
BTV-25-002_Figure_005.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/BTV-25-002/CMS-BTV-25-002_Figure_005.pdf
BTV-25-002_Figure_022.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/BTV-25-002/CMS-BTV-25-002_Figure_022.pdf
BTV-25-002_Figure_023.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/BTV-25-002/CMS-BTV-25-002_Figure_023.pdf
DP-2025-081_sl14_roc_c_tagging.png https://btv-public.docs.cern.ch/DPNotesRun3/DP-2025-081/plots/sl14_roc_c_tagging.png
DP-2025-081_sl14_roc_c_tagging_qcd.png https://btv-public.docs.cern.ch/DPNotesRun3/DP-2025-081/plots/sl14_roc_c_tagging_qcd.png
DP-2025-081_sl27_evolution_algo.png https://btv-public.docs.cern.ch/DPNotesRun3/DP-2025-081/plots/sl27_evolution_algo.png
HIG-17-028_Figure_006.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-17-028/CMS-HIG-17-028_Figure_006.pdf
HIG-17-028_Figure_007-b.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-17-028/CMS-HIG-17-028_Figure_007-b.pdf
HIG-18-031_Figure_008.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-18-031/CMS-HIG-18-031_Figure_008.pdf
HIG-19-006_Figure_011-a.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-19-006/CMS-HIG-19-006_Figure_011-a.pdf
HIG-19-006_Figure_014-a.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-19-006/CMS-HIG-19-006_Figure_014-a.pdf
HIG-21-008_Figure-aux_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure-aux_001.pdf
HIG-21-008_Figure-aux_050.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure-aux_050.pdf
HIG-21-008_Figure_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure_001.pdf
HIG-21-008_Figure_002-b.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure_002-b.pdf
HIG-21-008_Figure_003.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure_003.pdf
HIG-21-008_Figure_004.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-008/CMS-HIG-21-008_Figure_004.pdf
HIG-21-009_Figure_027.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-009/CMS-HIG-21-009_Figure_027.pdf
HIG-21-012_Figure_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-012/CMS-HIG-21-012_Figure_001.pdf
HIG-21-012_Figure_002-a.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-012/CMS-HIG-21-012_Figure_002-a.pdf
HIG-21-012_Figure_002.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-012/CMS-HIG-21-012_Figure_002.pdf
HIG-23-010_Figure_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-23-010/CMS-HIG-23-010_Figure_001.pdf
HIG-23-010_Figure_006.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-23-010/CMS-HIG-23-010_Figure_006.pdf
HIG-23-011_Figure_009.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-23-011/CMS-HIG-23-011_Figure_009.pdf
HIG-23-013_Figure_006.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-23-013/CMS-HIG-23-013_Figure_006.pdf
HIG-24-009_Figure_005.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-009/CMS-HIG-24-009_Figure_005.pdf
HIG-24-009_Figure_006.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-009/CMS-HIG-24-009_Figure_006.pdf
HIG-24-009_Figure_007.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-009/CMS-HIG-24-009_Figure_007.pdf
HIG-24-009_Figure_008.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-009/CMS-HIG-24-009_Figure_008.pdf
HIG-24-018_Figure_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_001.pdf
HIG-24-018_Figure_002.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_002.pdf
HIG-24-018_Figure_003.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_003.pdf
HIG-24-018_Figure_004.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_004.pdf
HIG-24-018_Figure_005.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_005.pdf
HIG-24-018_Figure_006.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_006.pdf
HIG-24-018_Figure_0B3.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_0B3.pdf
HIG-24-018_Figure_0B6.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_0B6.pdf
HIG-24-018_Figure_B11.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_B11.pdf
HIG-24-018_Figure_B12.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_B12.pdf
HIG-24-018_Figure_B13.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-018/CMS-HIG-24-018_Figure_B13.pdf
HIG-25-003_Figure_008-d.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-25-003/CMS-HIG-25-003_Figure_008-d.pdf
HIG-25-003_Figure_008.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-25-003/CMS-HIG-25-003_Figure_008.pdf
PAS-TOP-26-002_Figure_001.pdf https://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/TOP-26-002/CMS-PAS-TOP-26-002_Figure_001.pdf
PAS-TOP-26-002_Figure_008.pdf https://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/TOP-26-002/CMS-PAS-TOP-26-002_Figure_008.pdf
PAS-TOP-26-003_Figure_009.pdf https://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/TOP-26-003/CMS-PAS-TOP-26-003_Figure_009.pdf
SMP-22-012_Figure_005.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/SMP-22-012/CMS-SMP-22-012_Figure_005.pdf
HIG-21-018_Figure-aux_011.pdf https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-21-018/CMS-HIG-21-018_Figure-aux_011.pdf
EOF
for f in *.pdf; do
  [ "$f" = YR4_SMHiggsBR_120-130.pdf ] && continue   # cropped by html/build.py instead
  read -r w h ox oy < <(gs -q -dNOPAUSE -dBATCH -sDEVICE=bbox "$f" 2>&1 | awk '/HiRes/{x0=$2-2;y0=$3-2;x1=$4+2;y1=$5+2; printf "%.2f %.2f %.2f %.2f\n", x1-x0, y1-y0, -x0, -y0; exit}')
  gs -q -o "$f.tmp" -sDEVICE=pdfwrite -dAutoRotatePages=/None -dDEVICEWIDTHPOINTS="$w" -dDEVICEHEIGHTPOINTS="$h" -dFIXEDMEDIA -c "<</PageOffset [$ox $oy]>> setpagedevice" -f "$f" && mv "$f.tmp" "$f"
done

# Official CMS logo (CMS DocDB 3045). cms-docdb needs the CERN CA, so this fetch may fail
# off-site; if it does, run the same curl on lxplus and scp the files into figures/.
for c in color white; do
  curl -sfL -o "CMSlogo_${c}.png" "https://cms-docdb.cern.ch/cgi-bin/PublicDocDB/RetrieveFile?docid=3045&filename=CMSlogo_${c}_nolabel_1024_May2014.png" \
    || echo "WARNING: CMS logo ($c) not fetched; get it from lxplus (see comment above)"
done
# VUB logo (Wikimedia Commons, File:VUB_RGB.png)
curl -sfL -A "Mozilla/5.0" -o VUB_logo.png "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/VUB_RGB.png/1280px-VUB_RGB.png" \
  || echo "WARNING: VUB logo not fetched"
# SM Higgs branching ratios vs M_H (LHC Higgs XS WG, Yellow Report 4, arXiv:1610.07922), from the arXiv source
if [ ! -s YR4_SMHiggsBR_120-130.pdf ]; then
  t=$(mktemp -d); curl -sfL -o "$t/yr4.tgz" https://arxiv.org/e-print/1610.07922 \
    && tar xzf "$t/yr4.tgz" -C "$t" WG1/BranchingRatios/figs/SMHiggsBR_120-130.pdf \
    && cp "$t/WG1/BranchingRatios/figs/SMHiggsBR_120-130.pdf" YR4_SMHiggsBR_120-130.pdf \
    || echo "WARNING: YR4 BR plot not fetched"
  rm -rf "$t"
fi
