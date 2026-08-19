import sys
from PIL import Image
import numpy as np
bad=[]
for f in sorted(sys.argv[1:]):
    a=np.array(Image.open(f).convert("L"))
    h,w=a.shape
    strip=a[-14:,:]                       # 14px window, not 6
    dark=(strip<200).sum()
    if dark>6402*0.9: continue            # full-bleed section divider
    if dark>40: bad.append((f,dark))
for f,n in bad: print(f"CLIPPED {f}  {n}px")
print("clean" if not bad else f"{len(bad)} page(s) clipped")
sys.exit(1 if bad else 0)
