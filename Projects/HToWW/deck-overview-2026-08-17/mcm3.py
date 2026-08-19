import json, subprocess, sys

DS = ["WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
      "WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
      "WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8",
      "WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"]
URL = "https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/produces/"

for d in DS:
    out = subprocess.run(["curl", "-s", "-L", "--max-time", "60",
                          "-b", "/tmp/mcm.txt", URL + d],
                         capture_output=True, text=True).stdout
    try:
        j = json.loads(out)
    except Exception:
        print(f"{d}\n   non-JSON: {out[:120]}")
        continue
    r = j.get("results")
    rs = r if isinstance(r, list) else ([r] if r else [])
    print(f"=== {d}   ({len(rs)} request(s))")
    for x in rs:
        gp = x.get("generator_parameters") or []
        g = gp[-1] if gp else {}
        print(f"   prepid = {x.get('prepid')}")
        print(f"   dsname = {x.get('dataset_name')}")
        print(f"   xsec   = {g.get('cross_section')} pb   "
              f"filter_eff={g.get('filter_efficiency')}  "
              f"match_eff={g.get('match_efficiency')}")
        print(f"   negw   = {g.get('negative_weights_fraction')}")
