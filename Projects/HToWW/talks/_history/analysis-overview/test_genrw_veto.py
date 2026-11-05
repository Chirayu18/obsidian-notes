import os, sys, glob
os.chdir("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
sys.path.insert(0, os.getcwd())
from coffea import processor
from coffea.nanoevents import NanoAODSchema
from analysis.processors.base import BaseProcessor
import numpy as np, pandas as pd

# Two vjets samples via eoscms redirector (no proxy). W-dominated + DY-dominated.
URLS = {
    "WtoLNu_2Jets": "root://eoscms.cern.ch//eos/cms/store/mc/Run3Summer22EENanoAODv12/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2520000/4ac52a7f-8837-403a-a1b0-61f9a5862639.root",
}
output_location = "/tmp/genrw_veto_test/"
os.system(f"rm -rf {output_location}; mkdir -p {output_location}")

out = processor.run_uproot_job(
    {k: [v] for k, v in URLS.items()},
    treename="Events",
    processor_instance=BaseProcessor(workflow="hww_genrw_train", year="2022postEE",
                                     output_format="parquet", output_location=output_location),
    executor=processor.iterative_executor,
    executor_args={"schema": NanoAODSchema, "workers": 1},
    chunksize=20000, maxchunks=4,
)
print("RUN OK. cutflow:", out["metadata"].get("train", {}).get("cutflow"))

pqs = [p for p in glob.glob(output_location+"**/*.parquet", recursive=True) if "sumw_records" not in p]
print("feature parquet files:", len(pqs))
df = pd.concat([pd.read_parquet(p) for p in pqs], ignore_index=True)
print("total training rows:", len(df))

# --- verify the veto: NO exactly-one-emu-pair events survived ---
has_pair = df["lepton1_pdgId"].astype(int) != 0
l1 = df["lepton1_pdgId"].abs(); l2 = df["lepton2_pdgId"].abs()
is_emu = ((l1 == 11) & (l2 == 13)) | ((l1 == 13) & (l2 == 11))
n_emu_leaked = int((has_pair & is_emu).sum())
print("\n=== VETO CHECK ===")
print("rows with a pair:", int(has_pair.sum()), " of which emu (should be 0):", n_emu_leaked)
is_sf = has_pair & (((l1==11)&(l2==11)) | ((l1==13)&(l2==13)))
print("no-pair rows:", int((~has_pair).sum()), " same-flavor rows:", int(is_sf.sum()))

# --- COVERAGE: does training x span the emu-SR x? proxy emu-SR = the (vetoed) emu region ---
# We can't see emu here (vetoed), so compare same-flavor (train) vs the FULL loose x-range as SR proxy.
# Better: report training x support so we can eyeball vs the earlier emu-inclusive smoke run.
print("\n=== TRAINING gen-feature support (this veto'd region) ===")
for c in ["lhe_vpt","lhe_ht","lhe_nc","lhe_njets","genparton1_pt"]:
    if c in df.columns:
        s = df[c].astype(float)
        print("  %-14s mean %7.3f  p95 %8.2f  max %8.2f  frac>0 %.4f" % (
            c, np.nanmean(s), np.nanpercentile(s,95), np.nanmax(s), np.mean(s>0)))
print("  frac(lhe_nc>=1):", float((df["lhe_nc"]>=1).mean()))
print("  frac(genWeight sign>0):", float((np.sign(df.get("genweight_sign", pd.Series([np.nan]*len(df))))>0).mean()) if "genweight_sign" in df.columns else "n/a")
