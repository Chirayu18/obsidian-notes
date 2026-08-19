"""Aggregate hww_ctag_compare cutflows across all partitions and processes.

Four overlapping categories over ONE untagged jet collection, so every category shares
the same base chain and the WP/kinematic cut is the only difference:

  base              -> >=1 good jet, no c-tag         (8 selections)
  base_medium_cjet  -> + medium PNet WP (CvL>0.160, CvB>0.304)
  base_loose_cjet   -> + loose  PNet WP (CvL>0.054, CvB>0.182)
  base_kin_nocjet   -> + mTl2>30 & mTll>60 & mll<=72, NO c-tag

Reports weighted yields per process group, so the H+c vs ggH question (does loosening
admit more of the shape-degenerate competitor than signal?) can be answered directly.
"""
import glob
import sys
from collections import defaultdict

from coffea.util import load

BASE = "/eos/user/c/cgupta/higgscharm/outputs/hww_ctag_compare/2022preEE"
CATS = ["base", "base_medium_cjet", "base_loose_cjet", "base_kin_nocjet"]
# last cut in each category's chain = that category's final yield
FINAL = {
    "base": "atleast_one_cjet",
    "base_medium_cjet": "cjet_medium_wp",
    "base_loose_cjet": "cjet_loose_wp",
    "base_kin_nocjet": "dilepton_mass_signal",
}

# map dataset -> physics group (v11 6-class scheme + ggH broken out separately,
# since ggH is the shape-degenerate competitor the WP question turns on)
def group_of(ds):
    if ds.startswith("HplusCharm"):
        return "H+c (signal)"
    if ds.startswith("HplusBottom"):
        return "H+b"
    if ds.startswith("GluGluHto2Wto2L2Nu"):
        return "ggH (H->WW)"
    if ds.startswith(("GluGluH", "VBFH", "ZH_", "GluGluZH", "WplusH", "WminusH", "ttH")):
        return "other Higgs bkg"
    if ds.startswith("TT"):
        return "tt"
    if ds.startswith(("TW", "Tbar", "TBbar", "TQbar", "TbarQ", "TbarB", "TBbarQ")):
        return "single top"
    if ds.startswith(("WW", "WZ", "ZZ")):
        return "diboson"
    if ds.startswith(("DYto", "WtoLNu", "WG")):
        return "V+jets"
    if ds.startswith(("Muon", "EGamma", "Data")):
        return "DATA"
    return "other/" + ds


def main():
    # group -> cat -> summed weighted yield
    tot = defaultdict(lambda: defaultdict(float))
    nfiles = defaultdict(int)
    missing = []

    for f in sorted(glob.glob(BASE + "/*/*.coffea")):
        ds = f.split("/")[-2]
        # strip the _N partition suffix to get the dataset name
        base_ds = ds
        while base_ds and base_ds.rsplit("_", 1)[-1].isdigit():
            base_ds = base_ds.rsplit("_", 1)[0]
        g = group_of(base_ds)
        try:
            m = load(f)["metadata"]
        except Exception as e:  # noqa: BLE001
            missing.append((f, str(e)[:60]))
            continue
        nfiles[g] += 1
        for c in CATS:
            cf = m.get(c, {}).get("cutflow", {})
            key = FINAL[c]
            if key in cf:
                tot[g][c] += float(cf[key])

    order = ["H+c (signal)", "ggH (H->WW)", "other Higgs bkg", "H+b",
             "tt", "single top", "diboson", "V+jets", "DATA"]
    groups = [g for g in order if g in tot] + sorted(
        g for g in tot if g not in order)

    print("hww_ctag_compare  2022preEE  weighted yields")
    print("(one untagged jet collection; categories differ only by the final cut)\n")
    hdr = "%-18s %6s %12s %12s %12s %12s" % (
        "group", "files", "base", "medium WP", "loose WP", "kin (no tag)")
    print(hdr)
    print("-" * len(hdr))
    for g in groups:
        r = tot[g]
        print("%-18s %6d %12.1f %12.1f %12.1f %12.1f" % (
            g, nfiles[g], r["base"], r["base_medium_cjet"],
            r["base_loose_cjet"], r["base_kin_nocjet"]))

    print("\n\nRATIOS vs medium WP (the current production selection)")
    hdr2 = "%-18s %12s %12s %12s" % ("group", "base/med", "loose/med", "kin/med")
    print(hdr2)
    print("-" * len(hdr2))
    for g in groups:
        r = tot[g]
        m = r["base_medium_cjet"]
        if m <= 0:
            continue
        print("%-18s %12.2fx %11.2fx %11.2fx" % (
            g, r["base"] / m, r["base_loose_cjet"] / m, r["base_kin_nocjet"] / m))

    # the headline question: does loosening admit ggH faster than signal?
    s = tot.get("H+c (signal)", {})
    h = tot.get("ggH (H->WW)", {})
    if s.get("base_medium_cjet", 0) > 0 and h.get("base_medium_cjet", 0) > 0:
        print("\n\nH+c / ggH ENRICHMENT  (higher = charm tag doing its job)")
        print("%-18s %14s %14s" % ("selection", "H+c/ggH", "vs medium"))
        print("-" * 48)
        ref = None
        for c in CATS:
            if h.get(c, 0) > 0:
                e = s.get(c, 0) / h[c]
                if ref is None and c == "base_medium_cjet":
                    ref = e
                rel = ("%.2fx" % (e / ref)) if ref else "-"
                print("%-18s %14.4f %14s" % (c, e, rel))

    if missing:
        print("\nUNREADABLE FILES: %d" % len(missing))
        for f, e in missing[:5]:
            print("   ", f.split("/")[-1], e)


if __name__ == "__main__":
    sys.exit(main())
