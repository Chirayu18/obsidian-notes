import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/corrections/correction_manager.py")
s = p.read_text()
old = '                    flav=weights_config.get("higgsHFFlavour", "c"),'
new = '                    # charm: AN-23-102 scopes this to the ggH+HF composition and our\n                    # signal is H+c, so the c-flavour variant is the relevant one.\n                    flav="c",'
assert old in s
s = s.replace(old, new, 1)
p.write_text(s)
print("pinned flav='c'")
