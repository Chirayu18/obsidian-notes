---
tags: [reference, draft]
status: active
date: 2026-11-10
source: laptop
evidence: agent-reported
---
# Draft reply to Sebastiano Quinto (Mattermost), 2026-11-10: NOT SENT

Answers his 16:18 message ("there are still some samples that are submitted and not fully produced. Are you happy to stop the production of those and rerun it with the necessary fixes?"). Rebuilt from the summary in [[Projects/HToWW/samples-and-production/gridpacks/2026-11-10-gridpack-production-status|status note §4]], with Chirayu's 2026-11-10 addition: ask that the existing samples are kept on storage. Chirayu decides whether and when to send it.

> Hi Sebastiano, yes, happy to stop them and rerun with the fixes.
>
> - **H+c 4FS:** the rebuilt el8 gridpack and the fragment with the three missing FxFx lines are ready (slides + files in the package: https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/mcm_grid/request_package_2026-11). Validated at LHE+GEN against the official clean 4FS H→γγ gridpack; not run through SIM/RECO.
> - **H+b:** same build fix; the gridpack is being rebuilt now and is not validated yet, so I'll follow up once it is.
> - Which of these are still in production? H+c: HIG-Run3Summer22wmLHEGS-02684, HIG-Run3Summer22EEwmLHEGS-02600, HIG-Run3Summer23BPixwmLHEGS-02468; H+b: HIG-Run3Summer22wmLHEGS-02697, -22EEwmLHEGS-02645, -23wmLHEGS-03356, -23BPixwmLHEGS-02517.
> - The fragment currently points at the gridpack on my EOS. How should I get it onto cvmfs?
> - **One request:** could the samples that are already produced (and any partial output from the ones you stop) be kept on disk rather than invalidated/deleted, even if they are marked as superseded? We'd like to keep using them for things that don't depend on the broken weights or the forward-jet merging, e.g. as extra statistics for training a classifier. They won't be used for the signal templates or systematics.
>
> Thanks!

## Notes for Chirayu (not part of the message)
- Training caveat (agent's assessment, not checked): the existing samples are fine where only nominal-weight kinematics in the central region matter. The LHE scale/PDF weights are wrong (scale ≈×2, PDF ratio 2.26), and the forward 1-jet share is ≈7× too low (≈0.010 vs ≈0.07, [[Projects/HToWW/samples-and-production/gridpacks/deck/4fs.html|4FS deck]] slide 6). A classifier that uses forward jets would learn the wrong shape there.
- Assumes he means the central McM requests, not the private 3FS production.
- Which samples are fully produced vs in flight is not checked (no McM/DAS query was made).
- Data retention is ultimately a PdmV/computing decision; "kept on disk" is a request, not a guarantee.
