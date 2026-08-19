from analysis.corrections.correctionlib_files import correction_files as cf
for k in ("electron_id","electron_reco","electron_hlt","electron_ss"):
    if k in cf:
        v = cf[k].get("2022postEE", "(no 2022postEE key)")
        print(f"  {k:15s} {v}")
