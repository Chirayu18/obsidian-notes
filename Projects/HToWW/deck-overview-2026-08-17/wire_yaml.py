import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()

# 1) enable top-pT weight + turn trigger SFs ON
old_w = """    ctagging_2d: true    # PNet 2D pseudo-continuous HF-tag SF (CTag2DCorrector) -> CMS_ctag2d_2022
    muon:
      - id: tight
      - iso: tight
      - trigger: false
    electron:
      - id: wp80iso
      - reco: true
      - trigger: false"""
new_w = """    ctagging_2d: true    # PNet 2D pseudo-continuous HF-tag SF (CTag2DCorrector) -> CMS_ctag2d_2022
    # top-pT reweighting, tt only (AN-23-102 Table 16 + line 566). Nominal stays at 1
    # and the full size of the correction is the +-1 sigma interval (AN-24-091 convention),
    # so `rate_tt` is still fitted against an un-reweighted nominal.
    toppTWeight: true
    muon:
      - id: tight
      - iso: tight
      # HLT efficiency SFs (AN-23-102 Table 16). Previously false, which DISABLED the
      # scale factors entirely -- a weighting-correctness bug, not just a missing nuisance.
      - trigger: true
    electron:
      - id: wp80iso
      - reco: true
      - trigger: true"""
assert old_w in s, "weights anchor missing"
s = s.replace(old_w, new_w)

# 2) add the new shape systematics to the combine block
old_sh = """    - electron_reco_RecoAbove75
    - CMS_ctag2d_2022"""
new_sh = """    - electron_reco_RecoAbove75
    - CMS_ctag2d_2022
    # --- added 2026-08-11, all require the reprocessing campaign to have run ---
    # tt-only shape; no-ops on every other process (AN-23-102 Table 16 "top pT reweight")
    - top_pt
    # HLT efficiency (AN-23-102 Table 16). Needs weights_config muon/electron trigger: true
    - muon_trigger
    - electron_trigger"""
assert old_sh in s, "shape anchor missing"
s = s.replace(old_sh, new_sh)

p.write_text(s)
print("patched hww_combine_2dcat.yaml")
