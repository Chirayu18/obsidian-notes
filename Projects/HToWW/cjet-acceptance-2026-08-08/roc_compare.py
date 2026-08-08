"""ROC comparison: reference (current 2dcat selection) vs variant 3 (no tag + kin).

Both models are postEE-only and share config/hyperparameters, so any AUC difference is
attributable to the SELECTION alone.

The number that decides the study is hplusc-vs-higgsbkg: ggH is shape-degenerate with
the signal, so if dropping the charm tag destroys that separation, the extra acceptance
is worthless. hplusc-vs-tt matters too (tt is the volume driver).
"""
import sys, glob
from pathlib import Path
import numpy as np

BASE = Path("/eos/user/c/cgupta/EPR_task/b-hive/output")
CLASSES = ["hplusc","higgsbkg","tt","st","diboson","vjets"]
RUNS = {
    "reference (medium WP)": "hwwcom_multiclass_2dcats_ref",
    "variant 3 (no tag+kin)": "hwwcom_multiclass_2dcats_nocjetkin",
}

def find_dir(task, model):
    hits = glob.glob(f"{BASE}/{task}/HPlusCHToWW_2dcats/*/*/{model}/**/test_attack_nominal",
                     recursive=True)
    return sorted(hits)[-1] if hits else None

def auc_from_scores(pred, truth, sig=0, bkg=None):
    """AUC for class `sig` vs class `bkg` (or vs all others), using the sig score."""
    if bkg is None:
        m_s, m_b = (truth == sig), (truth != sig)
    else:
        m_s, m_b = (truth == sig), (truth == bkg)
    s, b = pred[m_s, sig], pred[m_b, sig]
    if len(s) == 0 or len(b) == 0:
        return float("nan"), len(s), len(b)
    bs = np.sort(b)
    # P(random signal scored above random background), ties at 0.5
    lo = np.searchsorted(bs, s, side="left")
    hi = np.searchsorted(bs, s, side="right")
    return float(((lo + hi) / 2).mean() / len(bs)), len(s), len(b)

results = {}
for label, model in RUNS.items():
    d = find_dir("InferenceTask", model)
    if d is None:
        print(f"[{label}] inference output not found yet"); continue
    try:
        pred = np.load(f"{d}/prediction.npy")
        truth = np.load(f"{d}/truth.npy")
    except Exception as e:
        print(f"[{label}] load failed: {e}"); continue
    if truth.ndim > 1:
        truth = np.argmax(truth, axis=1)
    print(f"\n=== {label} ===")
    print(f"  dir: {d}")
    print(f"  test events: {len(truth):,}")
    print("  class counts:", {CLASSES[i]: int((truth==i).sum()) for i in range(len(CLASSES))})
    r = {}
    a, ns, nb = auc_from_scores(pred, truth, 0, None)
    r["vs_all"] = a
    print(f"  AUC hplusc vs ALL      = {a:.4f}   (S={ns:,} B={nb:,})")
    for j, cname in enumerate(CLASSES):
        if j == 0: continue
        a, ns, nb = auc_from_scores(pred, truth, 0, j)
        r[cname] = a
        star = "  <-- the ggH degeneracy" if cname == "higgsbkg" else ""
        print(f"  AUC hplusc vs {cname:<9s}= {a:.4f}   (S={ns:,} B={nb:,}){star}")
    results[label] = r

if len(results) == 2:
    (la, ra), (lb, rb) = list(results.items())
    print("\n" + "="*64)
    print(f"{'comparison':<22s} {'reference':>10s} {'variant 3':>10s} {'delta':>9s}")
    print("-"*64)
    for k in ["vs_all"] + [c for c in CLASSES[1:]]:
        if k in ra and k in rb:
            d = rb[k] - ra[k]
            flag = "  <--" if k == "higgsbkg" else ""
            print(f"hplusc vs {k:<12s} {ra[k]:>10.4f} {rb[k]:>10.4f} {d:>+9.4f}{flag}")
    print("="*64)
    print("\nAUC higher = better separation. The higgsbkg row is the one that decides")
    print("whether the extra acceptance from dropping the charm tag is usable.")
