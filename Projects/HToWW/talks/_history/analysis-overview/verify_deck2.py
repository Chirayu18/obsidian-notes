"""Verify deck-2 claims: SF values, category population, B recovery."""
import numpy as np, correctionlib, pandas as pd, glob
SF="/eos/cms/store/group/phys_higgs/cmshgg/ingredients/2022/2D_HF_Tagging/flavTaggingSF_2022postEE.json.gz"
c=correctionlib.CorrectionSet.from_file(SF)["ParticleNetAK4_pseudocontinuous"]

print("=== deck claim: wp ids L0=0, C0..C4=40..44, B0..B4=50..54 ===")
for wp,nm in ((0,"L0"),(40,"C0"),(44,"C4"),(50,"B0"),(54,"B4")):
    try:
        v=c.evaluate("central",4,wp,1.0,60.); print(f"   wp={wp:2d} ({nm}) c-flavour SF = {v:.3f}  OK")
    except Exception as e: print(f"   wp={wp} FAILED {str(e)[:50]}")
print("\n=== deck claim: there is NO bare up/down ===")
for s in ("up","down","up_Total","down_Total","central"):
    try: c.evaluate(s,4,40,1.0,60.); print(f"   '{s}' -> EXISTS")
    except Exception: print(f"   '{s}' -> absent")
print("\n=== deck claim: abseta inclusive (value irrelevant) ===")
vals=[c.evaluate("central",5,50,e,60.) for e in (0.1,1.0,2.4)]
print(f"   b/B0 SF at |eta| 0.1/1.0/2.4 = {vals}  identical={len(set(vals))==1}")
print("\n=== deck claim: pt bins [20,35,50,70,90,120] ===")
print("   b/B0 SF vs pt:", {p: round(c.evaluate("central",5,50,1.0,p),4) for p in (15,25,40,60,80,100,200)})
