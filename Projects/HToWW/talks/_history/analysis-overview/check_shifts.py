"""Verify the JES/JER (and lepton) shape templates in the rebuilt 2dcat card.

The bug being checked for: inference had scored only 19/57 samples into the object-shift
directories, so merged groups (vjets, higgsbkg) summed a partial subset. Signature was
vjets -71% and higgsbkg -99% for BOTH Up and Down (same sign -- impossible for a +-1 sigma
scale shift), while single-sample groups (tt, st) moved a physical ~1.5% and diboson was
frozen identical to nominal (it had hit the nominal-copy fallback).

After the fix (all 12 shift dirs now at 44 samples) a healthy template must show:
  * Up and Down on OPPOSITE sides of nominal (or at least not both hugely negative)
  * magnitudes of a few percent, not -71% / -99%
  * no group exactly equal to nominal (that means the fallback fired = still missing)
"""
import sys
import ROOT

ROOT.gROOT.SetBatch(True)

F = sys.argv[1] if len(sys.argv) > 1 else (
    "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/"
    "higgscharm/outputs/combine/v11_hplusc_2dcat.root"
)

f = ROOT.TFile.Open(F)
if not f or f.IsZombie():
    sys.exit("cannot open %s" % F)

# discover channels (top-level dirs) and the systematics present
chans = [k.GetName() for k in f.GetListOfKeys()
         if f.Get(k.GetName()).InheritsFrom("TDirectory")]
if not chans:
    chans = [""]

print("file: %s" % F)
print("channels: %s\n" % ", ".join(chans))

SHIFTS = ["CMS_scale_j_2022", "CMS_res_j_2022",
          "CMS_scale_e_2022", "CMS_res_e_2022",
          "CMS_scale_m_2022", "CMS_res_m_2022"]

bad = []
for ch in chans:
    d = f.Get(ch) if ch else f
    names = set(k.GetName() for k in d.GetListOfKeys())
    # nominal templates = names with no Up/Down suffix
    noms = sorted(n for n in names
                  if not n.endswith("Up") and not n.endswith("Down")
                  and not n.startswith("data"))
    if not noms:
        continue
    print("=" * 78)
    print("CHANNEL %s" % ch)
    print("=" * 78)
    for syst in SHIFTS:
        rows = []
        for p in noms:
            hn = d.Get(p)
            hu = d.Get("%s_%sUp" % (p, syst))
            hd = d.Get("%s_%sDown" % (p, syst))
            if not hn or not hu or not hd:
                continue
            n, u, dn = hn.Integral(), hu.Integral(), hd.Integral()
            if n == 0:
                continue
            du = 100.0 * (u - n) / n
            dd = 100.0 * (dn - n) / n
            flag = ""
            if abs(du) < 1e-9 and abs(dd) < 1e-9:
                flag = "  <== FROZEN (== nominal, fallback fired)"
                bad.append((ch, syst, p, "frozen"))
            elif du * dd > 0 and (abs(du) > 5 or abs(dd) > 5):
                flag = "  <== SAME SIGN, large (unphysical)"
                bad.append((ch, syst, p, "same-sign"))
            elif abs(du) > 30 or abs(dd) > 30:
                flag = "  <== HUGE"
                bad.append((ch, syst, p, "huge"))
            rows.append((p, n, du, dd, flag))
        if not rows:
            continue
        print("\n  %s" % syst)
        print("    %-14s %12s %9s %9s" % ("process", "nominal", "Up %", "Down %"))
        for p, n, du, dd, flag in rows:
            print("    %-14s %12.2f %+8.2f%% %+8.2f%%%s" % (p, n, du, dd, flag))

print("\n" + "=" * 78)
if bad:
    print("PROBLEMS FOUND: %d" % len(bad))
    for ch, syst, p, why in bad:
        print("   %-12s %-20s %-12s %s" % (ch, syst, p, why))
else:
    print("ALL SHIFT TEMPLATES LOOK PHYSICAL "
          "(opposite-sign, few-percent, none frozen)")
print("=" * 78)
