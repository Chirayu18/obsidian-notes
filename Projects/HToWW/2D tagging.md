---
tags:
  - hww
status: active
related: "[[Archive/HToWW/HToWW]]"
date: 2026-02-23
---

# Untitled

---

## Commands

```bash
 import glob

import os

import numpy as np

import awkward as ak

import matplotlib.pyplot as plt

import matplotlib.colors as colors  # Added to fix LogNorm error

from matplotlib.patches import Rectangle

import mplhep as hep

from scipy.ndimage import gaussian_filter


# Set style

hep.style.use("CMS")

rng_np = np.random.default_rng(42)


# ==========================================

# 0) Settings & File Collection

# ==========================================

basedir = "/eos/user/s/snandaku/higgscharm/outputs/hplusc/2023postBPix/*/base"

files = sorted(glob.glob(os.path.join(basedir, "*.parquet")))


if len(files) == 0:

    raise FileNotFoundError(f"No .parquet files found in: {basedir}")


branches = {

    "pt": "jet_pt",

    "eta": "jet_eta",

    "B": "jet_btagPNetB",

    "CvB": "jet_btagPNetCvB",

    "CvL": "jet_btagPNetCvL", 

    "HF": "jet_hadronFlavour"

}


# ==========================================

# 1) Load inputs and selections

# ==========================================

B_list, CvB_list, CvL_list, HF_list = [], [], [], []


print(f"Found {len(files)} files. Loading...")


for f in files:

    try:

        ds = ak.from_parquet(f, columns=list(branches.values()))

        if len(ds) == 0: continue


        mask = (ds[branches["pt"]] > 25) & (abs(ds[branches["eta"]]) < 2.4)

        

        B_list.append(ak.flatten(ds[branches["B"]][mask]))

        CvB_list.append(ak.flatten(ds[branches["CvB"]][mask]))

        CvL_list.append(ak.flatten(ds[branches["CvL"]][mask]))

        HF_list.append(ak.flatten(ds[branches["HF"]][mask]))

    except Exception:

        continue


B = ak.to_numpy(ak.concatenate(B_list))

CvB = ak.to_numpy(ak.concatenate(CvB_list))

CvL = ak.to_numpy(ak.concatenate(CvL_list))

hf = ak.to_numpy(ak.concatenate(HF_list))


# Coordinates

pBvsC = 1.0 - CvB 

pBplusC = B + (1.0 - B) * CvL 


# Ensure unit square

valid = (pBplusC >= 0) & (pBplusC <= 1) & (pBvsC >= 0) & (pBvsC <= 1)

pBplusC, pBvsC, hf = pBplusC[valid], pBvsC[valid], hf[valid]


totals = {5: np.count_nonzero(hf == 5), 4: np.count_nonzero(hf == 4), 0: np.count_nonzero(hf == 0)}


# ==========================================

# 2) Optimizer

# ==========================================

N_RANDOM = 5000


def build_cats(p):
    y_c_peak = p["y_c_peak"] # Tighter ceiling to reduce b-contamination in C2-C4
    y_sep = y_c_peak         # B-bins start exactly where C-peak ends
    y_low = 1 #p["y_low_top"]   # Shared height for L0, C0, C1
    
    return {
        # High-purity Charm (C2, C3, C4)
        "C4": {"x": (p["xC1"], 1.0),    "y": (0.0, p["yC4"]), "c": (0, .4, 1, .2)},
        "C3": {"x": (p["xC1"], 1.0),    "y": (p["yC4"], p["yC3"]), "c": (0, .5, 1, .18)},
        "C2": {"x": (p["xC1"], 1.0),    "y": (p["yC3"], y_c_peak), "c": (0, .6, 1, .15)},
        
        # Shared low-mid purity region (L0, C0, C1)
        "C1": {"x": (p["xC0"], p["xC1"]), "y": (0.0, y_low), "c": (.2, .7, 1, .12)},
        "C0": {"x": (p["xL"], p["xC0"]),  "y": (0.0, y_low), "c": (.4, .8, 1, .1)},
        "L0": {"x": (0.0, p["xL"]),       "y": (0.0, y_low), "c": (1, .7, 0, .15)},
        
        # Bottom categories (B0-B4)
        "B0": {"x": (p["xC1"], 1.0),    "y": (y_sep, p["yB0"]), "c": (.6, 0, 0, .1)},
        "B1": {"x": (p["xC1"], 1.0),    "y": (p["yB0"], p["yB1"]), "c": (.7, 0, 0, .12)},
        "B2": {"x": (p["xC1"], 1.0),    "y": (p["yB1"], p["yB2"]), "c": (.8, 0, 0, .15)},
        "B3": {"x": (p["xC1"], 1.0),    "y": (p["yB2"], p["yB3"]), "c": (.9, 0, 0, .18)},
        "B4": {"x": (p["xC1"], 1.0),    "y": (p["yB3"], 1.0), "c": (1, 0, 0, .2)},
    }

def get_params():
    # Lower the max ceiling for Charm peak to squeeze out b-jets (Y-correction)
    y_c_peak = rng_np.uniform(0.15, 0.30) 
    y_sep = y_c_peak 
    y_low_top = rng_np.uniform(0.6, 0.98)
    
    # Increase horizontal limits to allow for a wider C0 (X-correction)
    xL = rng_np.uniform(0.01, 0.2)
    xC0 = rng_np.uniform(xL + 0.05, 0.45) # Increased upper bound for C0 width
    xC1 = rng_np.uniform(xC0 + 0.1, 0.75)
    
    # Sort vertical splits
    y_c_pts = sorted(rng_np.uniform(0.01, y_c_peak, size=2))
    yC4, yC3 = y_c_pts[0], y_c_pts[1]
    
    y_b_pts = sorted(rng_np.uniform(y_sep, 1.0, size=4))
    yB0, yB1, yB2, yB3 = y_b_pts[0], y_b_pts[1], y_b_pts[2], y_b_pts[3]
    
    return {"y_c_peak": y_c_peak, "y_low_top": y_low_top, "y_sep": y_sep,
            "xL": xL, "xC0": xC0, "xC1": xC1, 
            "yC4": yC4, "yC3": yC3, "yB0": yB0, "yB1": yB1, "yB2": yB2, "yB3": yB3}

def evaluate(cd, xp, yp, hfl, tot):
    score = 0.0
    cats_temp = np.full(xp.shape, "", dtype=object)
    for k, v in cd.items():
        m = (xp >= v["x"][0]) & (xp < v["x"][1]) & (yp >= v["y"][0]) & (yp < v["y"][1])
        cats_temp[m] = k
        
    for prefix, flav in [("C", 4), ("B", 5), ("L", 0)]:
        for c in [k for k in cd if k.startswith(prefix)]:
            m = (cats_temp == c)
            n_total = np.count_nonzero(m)
            if n_total < 5: continue 
            
            n_sig = np.count_nonzero((hfl == flav) & m)
            purity = n_sig / n_total
            eff = n_sig / tot[flav]
            
            # STRICTOR PURITY PENALTY for high-end Charm bins
            # Using purity**4 forces the optimizer to prefer cleaner bins over larger ones
            power = 4 if (prefix == "C" and c in ["C2", "C3", "C4"]) else 2
            score += eff * (purity ** power)
            
    return score



print("Optimizing...")

best = {"s": -1, "p": None}

for _ in range(N_RANDOM):

    p = get_params(); cd = build_cats(p); s = evaluate(cd, pBplusC, pBvsC, hf, totals)

    if s > best["s"]: best = {"s": s, "p": p}


best_cd = build_cats(best["p"])

# best_cd = {
#     "C4": {"x": (0.7339, 1.0000), "y": (0.0000, 0.0382)},
#     "C3": {"x": (0.7339, 1.0000), "y": (0.0382, 0.1851)},
#     "C2": {"x": (0.7339, 1.0000), "y": (0.1851, 0.2688)},
#     "C1": {"x": (0.4, 0.7339), "y": (0.0000, 0.9000)},
#     "C0": {"x": (0.15, 0.4), "y": (0.0000, 0.9000)},
#     "L0": {"x": (0.0000, 0.15), "y": (0.0000, 0.9000)},
#     "B0": {"x": (0.7339, 1.0000), "y": (0.2688, 0.4057)},
#     "B1": {"x": (0.7339, 1.0000), "y": (0.4057, 0.4068)},
#     "B2": {"x": (0.7339, 1.0000), "y": (0.4068, 0.6788)},
#     "B3": {"x": (0.7339, 1.0000), "y": (0.6788, 0.8406)},
#     "B4": {"x": (0.7339, 1.0000), "y": (0.8406, 1.0000)},
# }


# ==========================================

# 3) Plotting & Results

# ==========================================



fig, ax = plt.subplots(figsize=(12, 11))

# Fixed LogNorm location

h = ax.hist2d(pBplusC, pBvsC, bins=100, range=[[0, 1], [0, 1]], 

              cmap="Greys", norm=colors.LogNorm(), alpha=0.3)


for k, v in best_cd.items():

    ax.add_patch(Rectangle((v["x"][0], v["y"][0]), v["x"][1]-v["x"][0], v["y"][1]-v["y"][0], 

                           facecolor=v["c"], edgecolor='black', lw=2, alpha=0.4))

    ax.text(np.mean(v["x"]), np.mean(v["y"]), k, ha='center', va='center', fontweight='bold', fontsize=12)


ax.set_xlabel(r"PNet Score $P(b+c)$")

ax.set_ylabel(r"Pnet BvsC $P(b/(b+c))$")

hep.cms.text("Simulation Preliminary", ax=ax)

plt.show()


# --- Tables ---

cats_final = np.full(hf.shape, "", dtype=object)

for k, v in best_cd.items():

    m = (pBplusC >= v["x"][0]) & (pBplusC < v["x"][1]) & (pBvsC >= v["y"][0]) & (pBvsC < v["y"][1])

    cats_final[m] = k


print("\n" + "="*85)

print(f"{'Cat':<8} | {'eps_b (%)':<12} {'eps_c (%)':<12} {'eps_l (%)':<12} | {'Purity (%)':<12}")

print("-" * 85)

for cat in ["L0", "C0", "C1", "C2", "C3", "C4", "B0", "B1", "B2", "B3", "B4"]:

    m = (cats_final == cat)

    n_cat = np.count_nonzero(m)

    if n_cat == 0: continue

    eb = 100 * np.count_nonzero((hf == 5) & m) / totals[5] if totals[5] > 0 else 0

    ec = 100 * np.count_nonzero((hf == 4) & m) / totals[4] if totals[4] > 0 else 0

    el = 100 * np.count_nonzero((hf == 0) & m) / totals[0] if totals[0] > 0 else 0

    target = 4 if cat.startswith("C") else (5 if cat.startswith("B") else 0)

    purity = 100 * np.count_nonzero((hf == target) & m) / n_cat

    print(f"{cat:<8} | {eb:<12.2f} {ec:<12.2f} {el:<12.2f} | {purity:<12.2f}")

print("="*85) 
```

---

## Tasks

- [x] Implent this [completion:: 2026-04-15]
- [ ] Do the 2D tagging method I was thinking of 
- [x] Test thingsIt [completion:: 2026-04-15]

---

## Log

