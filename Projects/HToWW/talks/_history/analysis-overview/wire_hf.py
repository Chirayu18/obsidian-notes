import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/corrections/correction_manager.py")
s = p.read_text()

old_imp = "from analysis.corrections.toppt import add_toppt_weight"
assert old_imp in s
s = s.replace(old_imp, old_imp + "\nfrom analysis.corrections.higgs_hf import add_higgs_hf_weight")

old_hook = """        if "muon" in weights_config:
            if weights_config["muon"]:
                if "selected_muons" in pruned_ev.fields:"""
new_hook = """        if "higgsHFWeight" in weights_config:
            if weights_config["higgsHFWeight"]:
                # ggH/VBF only; per-event, keyed on gen-jet heavy flavour, so it
                # replaces the mis-scoped flat lnN on the merged higgsbkg group
                add_higgs_hf_weight(
                    events=pruned_ev,
                    weights_container=weights_container,
                    shift=shift,
                    dataset=dataset,
                    flav=weights_config.get("higgsHFFlavour", "c"),
                )
        if "muon" in weights_config:
            if weights_config["muon"]:
                if "selected_muons" in pruned_ev.fields:"""
assert old_hook in s
s = s.replace(old_hook, new_hook, 1)
p.write_text(s)
print("patched correction_manager.py for higgs_hf")
