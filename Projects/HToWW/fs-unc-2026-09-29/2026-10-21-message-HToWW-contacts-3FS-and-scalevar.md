---
tags: [reference, draft]
status: active
date: 2026-10-21
source: lxplus
---

# DRAFT: message to the HToWW contacts (3FS H→WW sample + Run 3 signal scale variations)

> Draft only, not sent. Two topics in one message, as asked. The detailed GEN ticket for topic 2 is
> [[2026-10-13-GEN-ticket-draft-HplusC-HplusB-WW]]; this message points to it rather than repeating it.
> Fill in [N events] and the recipients before sending.

---

**Subject:** H+c → WW: request for a Run 3 3FS sample, and broken scale/PDF weights in the Run 3 H+c/H+b WW samples

Dear all,

I would like to raise two production topics for the H+c → WW signal in one go.

**1. A Run 3 3FS H+c → WW sample**

For the flavour scheme treatment we follow LHCHWG-2026-007 (arXiv:2608.26863), which recommends stitching the 4FS FxFx and 3FS predictions rather than the flat 3FS/4FS normalisation uncertainty used in Run 2. For now we derive the 3FS/4FS difference as a shape systematic by reweighting the 4FS FxFx signal in the leading GEN charm hadron pT, using the official 3FS and 4FS H → γγ samples. On the real Run 2 UL18 H → WW 3FS and 4FS samples this reproduces the 3FS yield in our signal region (+7.3% predicted against +6.3 ± 2.3% observed) and all signal region shapes except the jet multiplicity, where 3FS has about 18% fewer two jet events. Validating this at 13.6 TeV and eventually doing the stitching itself needs a Run 3 3FS H → WW sample, and none exists: DAS has Run 3 3FS H+c only for H → γγ (2022 to 2024), and 3FS H → WW and H → ZZ only for Run 2 UL.

The request should be cheap. The official Run 3 3FS gridpack

`/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/HPlusCharm_3FS_MuRFScaleDynX0p50_HToGG_M125_TuneCP5_13p6TeV_amcatnlo_pythia8_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`

generates an undecayed Higgs (`p p > h c c~ [QCD]`, MG5_aMC 2.9.9, no MadSpin), so the decay is done in Pythia and the gridpack can be reused as it is. It also already skips the python systematics step in its runcmsgrid, so its scale and PDF weights are correct (see topic 2). Only a new fragment is needed: the 3FS H → γγ fragment with the decay changed to `25:onIfMatch = 24 -24`, `24:onIfAny = 11 13 15`, the same decay settings as our 4FS H → WW samples. I have run a short LHE+GEN test with this fragment in CMSSW_13_0_17 and it works [TEST RESULT]. The fragment is at `/eos/home-c/cgupta/HToWW/fs_unc/gen3fs_ww/python/HPlusCharm_3FS_HToWWTo2L2Nu_13p6TeV_fragment.py`.

Would it be possible to request this centrally for 2022, 2022postEE, 2023 and 2023BPix? Because about 40% of the 3FS events carry negative weights, a 3FS sample gives about six times fewer effective events per generated event than the 4FS FxFx one in our signal region, so we would suggest [N events] per era. So as not to lose time, we are starting a private production with the same gridpack and fragment through our existing private chain (GEN-SIM to NanoAODv13, same steps as our private 4FS sample), which we would use only until a central sample is available. Please let us know if you see a problem with that.

**2. Scale and PDF weights in the Run 3 H+c and H+b → WW samples**

While validating the central Run 3 signal samples we found two independent problems, both in the production setup and not in the physics cards.

The first concerns the LHE weights. In the H+c and H+b → WW samples every scale variation is about twice the nominal in both directions, and the mean of the PDF replicas over member 0 is about 2.26 instead of 1. The nominal weight and member 0 are correct. The cause is that these gridpacks were built with the current genproductions_scripts master NLO workflow, which switches off MG5_aMC's internal reweighting and computes the variations with the python systematics module afterwards. That module does not know about the running charm (bottom) Yukawa that the `_mg5amc.patch` of the H+HF cards implements in the internal reweighting, so every variation misses a factor of about 0.44 that varies event by event. The official H+c → γγ gridpacks, and the 3FS one above, avoid this through a sample specific change in runcmsgrid that skips the systematics step. We can correct the weights per event in the analysis to about 1% for μF and 1 to 4% for μR, but a re-production would make this unnecessary.

The second concerns the FxFx merging. The fragments of all seven H+c and H+b → WW requests lack the lines `JetMatching:jetAlgorithm = 2`, `JetMatching:etaJetMax = 999.` and `JetMatching:coneRadius = 1.`, which the γγ fragment, the Run 2 fragments and the current central FxFx fragments in the same campaigns contain. Pythia then uses its defaults (|η| < 2.5, R = 0.7), so the FxFx veto ignores forward jets: forward one jet events are seven times rarer and hard forward zero jet events ten times more frequent than in the clean samples. This cannot be corrected by reweighting. In our selection the effect on the nominal acceptance is small (29.3% against 29.7% for the γγ reference), but it also distorts the scale variation shapes.

The affected requests are HIG-Run3Summer22wmLHEGS-02684, HIG-Run3Summer22EEwmLHEGS-02600 and HIG-Run3Summer23BPixwmLHEGS-02468 for H+c, and HIG-Run3Summer22wmLHEGS-02697, HIG-Run3Summer22EEwmLHEGS-02645, HIG-Run3Summer23wmLHEGS-03356 and HIG-Run3Summer23BPixwmLHEGS-02517 for H+b. The clean reference is HIG-Run3Summer22EEwmLHEGS-01159. We would like to ask for a re-production of these seven requests with the gridpacks rebuilt from the same cards without the systematics step (I can rebuild them as before) and with the three JetMatching lines added to the fragments. I have a detailed write-up with figures ready for a GEN ticket and would be glad to know whether you prefer me to file it on the existing mccm issue or directly with the GEN conveners. It may also be worth checking other processes that carry a running Yukawa patch, such as bbH, for the same weight problem.

The Run 3 3FS sample could naturally be requested in the same round as these re-productions.

Best regards,
Chirayu
