import pathlib, re
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/workflows/hww_combine_2dcat.yaml")
s = p.read_text()
# comment out the per_channel block -> ggH split only
s = re.sub(r"\n    per_channel:\n(      CR_\w+:\s*\[0\.0, 1\.0\]\n)+",
           lambda m: "\n" + re.sub(r"^", "    # ", m.group(0).strip("\n"), flags=re.M) + "\n",
           s, count=1)
p.write_text(s)
print("per_channel disabled; ggH split still on")
