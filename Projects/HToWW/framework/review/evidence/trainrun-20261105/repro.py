import sys, os, numpy as np, tempfile
from pathlib import Path
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.getcwd()+"/scripts/combine")
from coffea import processor
from analysis.sinks.hww import make_templates
from scripts.combine.build_cards_from_templates import normalize_record, make_process_hists, configure_era
from analysis.workflows.config import WorkflowConfigBuilder
from analysis.filesets.utils import get_dataset_config
cls=["hplusc","higgsbkg","tt","st","diboson","vjets"]; ch={"SR_hplusc":"hplusc","CR_higgsbkg":"higgsbkg","CR_tt":"tt","CR_st":"st","CR_diboson":"diboson","CR_vjets":"vjets"}
edges=[0,.2,.3,.35,.4,.44,.48,.52,.56,.6,1.]
s=np.array([[.9,.02,.02,.02,.02,.02]]*4)
print("== R1 variation present in only some chunks")
c1=make_templates(s[:2],cls,ch,edges,{"nominal":np.ones(2),"CMS_pileup_2022Up":np.ones(2)*1.1})
c2=make_templates(s[2:],cls,ch,edges,{"nominal":np.ones(2)})
m=processor.accumulate([c1,c2])
print(" nominal SR sum", normalize_record(m["nominal"])["SR_hplusc"][0].sum(), " pileupUp SR sum", normalize_record(m["CMS_pileup_2022Up"])["SR_hplusc"][0].sum(), "(expected 4.4); norm_raw nominal/up:", m["nominal"]["norm_raw"], m["CMS_pileup_2022Up"]["norm_raw"])
print("== R2 negative bin not floored")
r=make_templates(s[:2],cls,ch,edges,{"nominal":np.array([-5.,1.])})
print(" SR nominal last bin:", normalize_record(r["nominal"])["SR_hplusc"][0][-1])
print("== R3 whole samples missing from RUN inputs")
cfg=configure_era(WorkflowConfigBuilder("hww_allfix_4fs").build_workflow_config(),"2022postEE")
ds=get_dataset_config("2022postEE"); pm=cfg.combine["process_map"]
from runner import get_datasets_to_run_over
run=get_datasets_to_run_over("hww_allfix_4fs","2022postEE")
chosen={}; 
for d in run:
    info=ds[d]
    if info["era"]=="data": continue
    for p,procs in pm.items():
        if info["process"].strip() in procs and p not in chosen: chosen[p]=d
out={"samples":{}}
for p,d in chosen.items():
    w={"nominal":np.ones(2)}
    for sname in cfg.combine["shape_systematics"]:
        w[sname+"Up"]=np.ones(2); w[sname+"Down"]=np.ones(2)
    rec=make_templates(np.tile(np.eye(6)[cls.index(p)],(2,1)),cls,ch,edges,w, np.ones(2) if p=="vjets" else None, np.zeros(2) if p=="vjets" else None)
    out["samples"][d]={"sumw":1.0,"templates":{"base":rec}}
na={d: cfg.combine["shape_systematics"]+["CMS_negrw_vjets"] for d in chosen.values()}
h,v,o,e=make_process_hists(out,cfg,"2022postEE",na)
nmc=sum(1 for d in run if ds[d]["era"]!="data")
print(" MC samples selected by workflow:",nmc," supplied:",len(chosen)," -> make_process_hists raised? NO; cards would be built")
unmapped=sorted({ds[d]["process"] for d in run if ds[d]["era"]!="data" and not any(ds[d]["process"].strip() in v for v in pm.values())})
print("== R8 processed MC with no card mapping (would raise in build_cards):", unmapped)
grp=cfg.mva["labels"]["process_groups"]
print("   mva groups not in process_map:", sorted({x for g in grp.values() for x in g} - {x for v in pm.values() for x in v}))
print("== R4 condor output dir")
from coffea.util import save
with tempfile.TemporaryDirectory() as t:
    legacy=Path(t)/"outputs/hww_allfix_4fs/2022postEE/DS"; legacy.mkdir(parents=True)
    new=str(legacy).replace("/hww_allfix_4fs/","/hww_allfix_4fs__run/")
    try: save({"a":1}, new+"/DS_1.coffea"); print(" save OK")
    except Exception as x: print(" save into replaced path ->", type(x).__name__, x)
print("== R5 pyarrow error classes")
import pyarrow as pa, pyarrow.parquet as pq
with tempfile.TemporaryDirectory() as t:
    p=Path(t)/"z.parquet"; p.write_bytes(b"")
    try: pq.read_table(p)
    except Exception as x: print(" zero-byte:", type(x).__name__, "isOSError=",isinstance(x,OSError))
    p.write_bytes(b"PAR1garbage")
    try: pq.read_table(p)
    except Exception as x: print(" truncated:", type(x).__name__, "isOSError=",isinstance(x,OSError))
