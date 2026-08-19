import sys
from PIL import Image
import numpy as np
bad=[]
for f in sorted(sys.argv[1:]):
    a=np.array(Image.open(f).convert("L"))
    strip=a[-6:,:]
    if (strip<200).sum()>50: bad.append((f,(strip<200).sum()))
for f,n in bad: print(f"CLIPPED {f}  {n}px")
print("clean" if not bad else f"{len(bad)} page(s) clipped")
