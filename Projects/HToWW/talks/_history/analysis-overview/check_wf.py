import sys
sys.path.insert(0, "/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
from analysis.workflows.config import WorkflowConfigBuilder
for wf in ["hww_MVA", "hww_MVA_nocjet", "hww_MVA_looseWP"]:
    c = WorkflowConfigBuilder(workflow=wf).build_workflow_config()
    cuts = c.object_selection["cjets"]["cuts"]
    tag = [x for x in cuts if "ctagging" in x]
    print("{:<18s} ncuts={}  ctag={}".format(wf, len(cuts), tag[0] if tag else "NONE"))
    print("   categories.base:", c.event_selection["categories"]["base"])
