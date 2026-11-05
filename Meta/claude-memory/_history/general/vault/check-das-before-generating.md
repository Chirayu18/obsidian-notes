---
name: check-das-before-generating
description: Before generating ANY MC sample, query DAS for official produced samples — I privately generated H+c 3FS/4FS that already existed centrally
metadata:
  type: feedback
---

**Always query DAS for an official produced sample before generating anything** — even when
the task sounds like "use the gridpack". A gridpack on cvmfs almost always means the sample
was also produced centrally.

On 2026-09-25 I privately generated 400k H+c 3FS/4FS HToGG events (160 condor jobs, LHE→NanoGEN)
from the cvmfs gridpacks, then submitted another 160 jobs for Run 2 — while official NanoAOD for
all of them was on DAS with 10× the statistics:
- Run 3: `/HPlusCharm_{3FS,4FS}_MuRFScaleDynX0p50_HTo2G_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8/Run3Summer2*NanoAODv13-*/NANOAODSIM`
- Run 2: `/HPlusCharm_{3FS,4FS}_MuRFScaleDynX0p50_{HToGG,HToWWTo2L2Nu}_…_13TeV…/RunIISummer20UL*NanoAODv9-*/NANOAODSIM`
The user called this out bluntly ("Are you dumb?").

**Why:** generation is expensive, slower, and lower-statistics than the central sample; NanoAOD
already has genWeight, GenJet_hadronFlavour, GenPart, LHEScaleWeight — everything a GEN-level
ratio needs.

**How to apply:** `dasgoclient -query="dataset=/<Process>*/*/NANOAODSIM"` (with
X509_USER_PROXY set) is step 1. Only if nothing exists, propose generation — and ask first.
Related: [[Meta/claude-memory/_history/projects/HToWW/vault/hww-signal-private-fetch-iihe|hww-signal-private-fetch-iihe]], [[Meta/claude-memory/_history/workflow/vault/lxplus-proxy-and-tmux|lxplus-proxy-and-tmux]]
