import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# revert the trigger flags to false, keep toppTWeight
old = """    muon:
      - id: tight
      - iso: tight
      # HLT efficiency SFs (AN-23-102 Table 16). Previously false, which DISABLED the
      # scale factors entirely -- a weighting-correctness bug, not just a missing nuisance.
      - trigger: true
    electron:
      - id: wp80iso
      - reco: true
      - trigger: true"""
new = """    muon:
      - id: tight
      - iso: tight
      # HLT efficiency SFs (AN-23-102 Table 16) remain DISABLED by explicit decision
      # (2026-08-11). Note this means trigger SFs are not applied at all, so the
      # nominal weights carry no trigger correction -- a known, accepted gap.
      - trigger: false
    electron:
      - id: wp80iso
      - reco: true
      - trigger: false"""
assert old in s, "trigger anchor missing"
s = s.replace(old, new)

# drop the trigger shape rows, keep top_pt
old_sh = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt
    # HLT efficiency (AN-23-102 Table 16). Needs weights_config muon/electron trigger: true
    - muon_trigger
    - electron_trigger"""
new_sh = """    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt"""
assert old_sh in s, "shape anchor missing"
s = s.replace(old_sh, new_sh)

p.write_text(s)
print("reverted trigger SFs; top_pt kept")
