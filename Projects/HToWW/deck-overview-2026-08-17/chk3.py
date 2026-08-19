import sys
sys.path.insert(0, "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
from analysis.workflows.config import WorkflowConfigBuilder
for wf in ["hww_combine_2dcat", "hww_2dcat_nocjet", "hww_2dcat_looseWP", "hww_2dcat_nocjet_kin"]:
    c = WorkflowConfigBuilder(workflow=wf).build_workflow_config()
    cuts = c.object_selection["cjets"]["cuts"]
    tag = [x for x in cuts if "ctagging" in x]
    cats = c.event_selection["categories"]["base"]
    print("{:<24s} ctag={:<10s} nbase={} kin={}".format(
        wf, (tag[0].split("'")[1] if tag else "NONE"), len(cats),
        "YES" if "transverse_mass_signal" in cats else "no"))
    print("      out:", c.combine["output"]["datacard"])
