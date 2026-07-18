#!/usr/bin/env bash
# Rebuild the combined printable reader from the cheatsheet + paper page-clips.
# Requires: pdflatex, ghostscript (gs), pdfunite (poppler-utils).
set -euo pipefail
cd "$(dirname "$0")"

pdflatex -interaction=nonstopmode 00_cheatsheet.tex >/dev/null

clip() {  # name firstpage lastpage source.pdf
  gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
     -dFirstPage="$2" -dLastPage="$3" -sOutputFile="clip_$1.pdf" "$4"
}
clip antikt        2  3  antikt_0802.1189.pdf
clip fastjet_excl  14 14 fastjet_manual_1111.6097.pdf
clip fastjet_excl2 20 20 fastjet_manual_1111.6097.pdf
clip bdrs          1  5  bdrs_massdrop_0802.2470.pdf
clip mmdt          24 26 mMDT_1307.0007.pdf
clip softdrop      3  3  softdrop_1402.2657.pdf
clip softdrop2     6  7  softdrop_1402.2657.pdf
clip lund          4  6  lundplane_1807.04758.pdf

pdfunite \
  00_cheatsheet.pdf \
  clip_antikt.pdf \
  clip_fastjet_excl.pdf clip_fastjet_excl2.pdf \
  clip_bdrs.pdf clip_mmdt.pdf clip_softdrop.pdf clip_softdrop2.pdf \
  clip_lund.pdf \
  ../flashjet-substructure-reader.pdf

echo "built ../flashjet-substructure-reader.pdf"
