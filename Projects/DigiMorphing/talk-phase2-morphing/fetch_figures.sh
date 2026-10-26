#!/bin/bash
# Restore figures/ (gitignored). Plots from EOS via lxplus; logos from the Higgs 2026 deck;
# workshop crops re-made from References/DigiMorphing/tkdpg-workshop-2026-10 (CERN-restricted, local only).
set -e
cd "$(dirname "$0")"; mkdir -p figures
~/bin/lxplus-ssh 'cd /eos/user/c/cgupta/phase2morph/plots && tar cf - *.png' | tar xf - -C figures
cp ../../HiggsCharmTalk-Higgs2026/figures/{CMSlogo_color,CMSlogo_white,VUB_logo}.png figures/
W=../../../References/DigiMorphing/tkdpg-workshop-2026-10; T=$(mktemp -d)
pdftoppm -png -r 200 -f 12 -l 12 $W/2026_10_14_bartosik_v1.pdf $T/b
pdftoppm -png -r 200 -f 4 -l 4 $W/TRK-Oct-2026_TrackerDPGWorkshop.pdf $T/s
python3 -I - "$T" <<'PY'
import sys; from PIL import Image; T=sys.argv[1]
b=Image.open(f"{T}/b-12.png"); w,h=b.size
b=b.crop((int(w*0.06),int(h*0.39),int(w*0.50),int(h*0.92))); w,h=b.size
b.crop((0,0,int(w*0.80),int(h*0.61))).save("figures/bartosik_dual_quad.png")
s=Image.open(f"{T}/s-04.png"); w,h=s.size
s.crop((0,int(h*0.17),w,int(h*0.735))).save("figures/schulz_run3_timeline.png")
PY
rm -rf "$T"
python3 -I -c "
from PIL import Image
im=Image.open('figures/display_3.png'); w,h=im.size; im.crop((0,int(h*0.27),w,h)).save('figures/display_3_crop.png')"
