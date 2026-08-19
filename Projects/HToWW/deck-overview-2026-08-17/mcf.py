from analysis.corrections.correctionlib_files import correction_files as cf
for k in sorted(cf):
    if any(t in k for t in ("muon","electron","pileup","jet","ctag","btag")):
        v = cf[k].get("2022postEE", "(no 2022postEE key)") if isinstance(cf[k], dict) else cf[k]
        print(f"  {k:18s} {v}")
