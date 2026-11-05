import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/corrections/correction_manager.py")
s = p.read_text()

# import
old_imp = "from analysis.corrections.partonshower import add_partonshower_weight"
assert old_imp in s, "ps import anchor missing"
s = s.replace(old_imp, old_imp + "\nfrom analysis.corrections.toppt import add_toppt_weight")

# hook: add right after the nnlops block, before the muon block
old_hook = """        if "muon" in weights_config:
            if weights_config["muon"]:
                if "selected_muons" in pruned_ev.fields:"""
new_hook = """        if "toppTWeight" in weights_config:
            if weights_config["toppTWeight"]:
                # tt only (AN-23-102 line 566); the module no-ops on other datasets
                add_toppt_weight(
                    events=pruned_ev,
                    weights_container=weights_container,
                    shift=shift,
                    dataset=dataset,
                )
        if "muon" in weights_config:
            if weights_config["muon"]:
                if "selected_muons" in pruned_ev.fields:"""
assert old_hook in s, "muon hook anchor missing"
s = s.replace(old_hook, new_hook, 1)
p.write_text(s)
print("patched correction_manager.py")
