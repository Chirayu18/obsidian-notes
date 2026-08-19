import pyarrow.parquet as pq

A = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva_labeled/train/H+c.parquet"
B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE/mva_labeled/H+c.parquet"

a = set(pq.read_schema(A).names)
b = set(pq.read_schema(B).names)

oh_a = sorted(c for c in a if "ctag2d" in c)
oh_b = sorted(c for c in b if "ctag2d" in c)

print("TRAINED-ON (hww_combine_fixed) ctag2d cols: %d" % len(oh_a))
for c in oh_a:
    print("   ", c)
print()
print("NEW (hww_combine_2dcat) ctag2d cols: %d" % len(oh_b))
for c in oh_b:
    print("   ", c)
print()
print("ctag2d present in trained-on but MISSING in new:", sorted(set(oh_a) - set(oh_b)))
print("ctag2d extra in new:", sorted(set(oh_b) - set(oh_a)))
print()

# the 15 kinematic inputs the 2dcats config uses (from the v11 feature set)
kin = ["mtll", "mtl2", "dilepton_mass", "met_pt", "dilepton_pt",
       "cjet_cand_pt", "cjet_cand_eta", "lepton1_pt", "lepton2_pt",
       "dphi_ll", "deltaR_ll", "njets", "ncjets", "ht", "mtl1"]
print("kinematic-ish inputs present?")
for k in kin:
    print("   %-18s trained-on=%-5s new=%s" % (k, k in a, k in b))
