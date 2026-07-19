"""2D c-tagging categories (official SFbc-2D / AN-25-222 scheme) from PNet scores.

The BTV 2D flavour-tagging calibration partitions a (HFvLF, BvC) plane into 11
categories L0, C0-C4, B0-B4 with frozen bin edges. Both axes are exact functions
of the PNet CvsL / CvsB discriminants via the 3-simplex (b, c, L = uds+g):

    CvsL = P_c/(P_c+P_L),  CvsB = P_c/(P_c+P_b),  P_b+P_c+P_L = 1

    =>  BvC   (y) = 1 - CvB
        HFvLF (x) = P_b + P_c = 1 - P_L = CvL / (CvL + CvB*(1 - CvL))

(Verified symbolically, on 2M synthetic triplets to 4e-16, and against the stored
Jet_btagPNetB on 30k NanoAODv12 jets to ~3e-5 = float-storage rounding.)

See Projects/HToWW/CTAG.md in the notes vault for the full derivation and the
MVA retrain results.
"""

import numpy as np
import awkward as ak

# Official frozen edges (SFbc-2D docs, 2026.06.29)
X_HFVLF_EDGES = [0.0, 0.250, 0.452, 0.808, 1.000]
Y_BVC_EDGES = [0.0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1.0]

# Category order -> integer id used by the IntCategory axis
CTAG2D_CATEGORIES = ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]
CTAG2D_ID = {name: i for i, name in enumerate(CTAG2D_CATEGORIES)}


def ctag2d_axes(cvsl, cvsb):
    """Return (HFvLF, BvC) axis values from PNet CvsL / CvsB."""
    den = cvsl + cvsb * (1.0 - cvsl)
    hfvlf = ak.where(den != 0, cvsl / den, np.nan)
    bvc = 1.0 - cvsb
    return hfvlf, bvc


def ctag2d_category(cvsl, cvsb, fill_value=-1):
    """Integer 2D-CTAG category (0..10) per jet; `fill_value` where undefined.

    Layout follows the SFbc-2D figure:
      HFvLF < 0.808            -> L0 | C0 | C1   (split at 0.250, 0.452)
      HFvLF >= 0.808           -> stacked in BvC: C4,C3,C2 at low BvC,
                                  then B0..B4 rising to purest b at B4.
    """
    x, y = ctag2d_axes(cvsl, cvsb)
    xe, ye = X_HFVLF_EDGES, Y_BVC_EDGES

    cat = ak.full_like(x, fill_value, dtype=np.int8)
    good = ~ak.is_none(x, axis=-1) & (x == x) & (y == y)  # finite check
    left = good & (x < xe[3])
    right = good & (x >= xe[3])

    def put(mask, name):
        return ak.where(mask, np.int8(CTAG2D_ID[name]), cat)

    cat = put(left & (x < xe[1]), "L0")
    cat = put(left & (x >= xe[1]) & (x < xe[2]), "C0")
    cat = put(left & (x >= xe[2]), "C1")

    cat = put(right & (y < ye[1]), "C4")
    cat = put(right & (y >= ye[1]) & (y < ye[2]), "C3")
    cat = put(right & (y >= ye[2]) & (y < ye[3]), "C2")
    cat = put(right & (y >= ye[3]) & (y < ye[4]), "B0")
    cat = put(right & (y >= ye[4]) & (y < ye[5]), "B1")
    cat = put(right & (y >= ye[5]) & (y < ye[6]), "B2")
    cat = put(right & (y >= ye[6]) & (y < ye[7]), "B3")
    cat = put(right & (y >= ye[7]), "B4")
    return cat


def ctag2d_onehot(cvsl, cvsb, name):
    """One-hot (0/1) indicator for a single category `name` — MVA input form."""
    return ak.values_astype(ctag2d_category(cvsl, cvsb) == CTAG2D_ID[name], np.int8)
