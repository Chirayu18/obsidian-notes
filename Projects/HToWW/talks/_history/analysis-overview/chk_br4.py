import uproot
url = "root://cms-xrd-global.cern.ch//store/mc/Run3Summer22EENanoAODv12/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2540000/0a2e0f0a-0f9e-4b6e-8f0b-1b1b1b1b1b1b.root"
import json
# instead: use DAS-free approach -- read local parquet-era file list if present
import glob
print("trying global redirector listing is unreliable; use dasgoclient result passed in")
