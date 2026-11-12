---
tags: [reference, slides, audit]
status: active
date: 2026-11-12
source: laptop
---
# November talk: content selection and source audit

For [[2026-11-13-november-update/deck/speaker-notes|the November analysis update]]. This records presentation selection and source checks, not new physics validation. No analysis code, processing, training or Combine was run by the keeper.

## Scope inspected

- All **619 messages**, including **136 human messages**, in [HToWW discussion](t3-thread://v2/7fbb6319-2aff-454c-af0e-25d245ea222a/mcp:launch:c579469bb982201d1faef641142a07a085154cf634947a20f3f05bc741f395cf), positions0–2615; pagination reached the end, no truncated messages. Latest saved discussion status is12November21:42CET. Tool activity is not replayed. Operational instructions in history are not fresh authorizations.
- **234 vault commits** touching HToWW since1September through c92659b, including original paths before the5November reorganization. Many concern the separately reorganized CombineAgent project, repeated monitoring snapshots or slide production; these do not become HToWW physics updates.
- Current HToWW PDF/HTML/TeX inventory:112 source/PDF candidates including analysis-note components and53individual closure plots;31non-closure PDFs text-extracted. Deck families reviewed: September flavour-scheme23pages; October framework19pages; November gridpacks21/11/15pages and revisions; full-rerun r1–r7; framework r1/r2; current November r1/r2. August analysis-overview62pages, Athens83pages, MVA studies24pages, c-tag33pages, negrw56pages, lepton ONNX26pages and kinematic/MVA11pages inspected as baseline/context, not labelled new since September. The standalone2024tt sample9-page survey is an inventory, not a production fit result.
- Read post-September ordinary source notes and the dated sections of the evolving full-rerun and framework notes. Search degraded to keyword-only inside the sandbox; exact-path source reads and Git history supplied the evidence.
- Actual October figures recovered read-only from EOS; source SHA256 and proportional-resize provenance in deck/assets/*.json. The build uses local figures and local Reveal, no external content upload.

## Chirayu's decisions, in message order

| Discussion position | Decision / exact wording | Consequence |
|---|---|---|
|1546|“the update on the lepton prompt MVA and the other speedups we did right?”|Keep reference-checked ONNX and measured timings, distinguish prompt/event classifiers.|
|1627,1645|“a detailed breakdown of each systematic and its implementation, with plots and results of checks where nessary”; “an explaination for each systematic on what it is”|Full physical/implementation walkthrough; no invented check plots.|
|1790|“do it later, not now” for hDamp|Deferred; configuration is not an implemented nuisance.|
|2143|“we present this first after presenting what all we did to arrive till here... Then we present updates upon updates after that”|August→October→691, then subsequent signal and analysis improvements.|
|2159|“for the new limit we will produce, we will have2SR with the ncjet split”|FinalNc=1/≥2; current TRAIN iteration schema needs mergedSR.|
|2171|“add the higgs scale treatement ... as a slide after the691 limit”|V0/V1/V2 immediately after reference limit.|
|2201|“more cheap results? Like data/MC plots? ... uncertainity badns were large ... investigate”|Restore actual October data/MC, band decomposition, slope investigation and revised diagnosis.|
|2221|“I have already sent the corrected H+c and H+b gridpacks ... I have also done for3FS validation”|Supersedes Nov10draft-only communication status; main gridpack handoff slide.|
|2221|Sebastiano “can try to reproduce those samples with increased priority”|Report as Chirayu's communication, not completed central reproduction.|
|2250|“add the leptonMVA alternative”|Requested; no precise alternative or completed result established. Do not invent one.|
|2426,2432|“problems we found ... fixes we made”; “better way to present”|Problems→solutions→single-pass design, no menu of mode names.|
|2448|“NO say a bit of refractoring, record that”|Chosen wording retained; no measured integration-effort claim.|

Further keeper-thread requests12November: review every deck/history since1September; add all minor updates at the end; no running/queued language; full systematic walkthrough; explicit Sebastiano handoff; full central signal/background inventory including2024; theory citations; impact table and likelihood scans; Claude review/correction followed by keeper review.

## Selection ledger

| Material | Choice | Evidence / qualification |
|---|---|---|
|Four-era expected limit691 and all7period combinations|Main|[[Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings]] and original limits_summary.png. Explicit pre-fix reference.|
|Higgs-scaleV0/V1/V2|Main|V0recorded691; V1direct log703; V2direct log691. Logs and construction source preserved in deck/review/evidence.|
|October nuisance impacts and numerical table|Main|Direct impacts_run3.json; Asimovr=1; signedΔr,not percent limit effects. Excludes MC-bin parameters.|
|October freeze-group breakdown|Main summary|[[Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3]]; different conventions forbid direct percentage-size comparison with Run2.|
|Data/MC MET,mTll|Main|Actual2022postEE plotter outputs,notAsimov; old production and large weight-only band.|
|All-era uncertainty-band decomposition|Main|Originalband_overview_allEras.png; readband_breakdown.pyandoldcard directly. tt scale is absent from the fit but included by plotter.|
|Slope tests and revised preEE diagnosis|Main|Slope summary and [[Projects/HToWW/samples-and-production/full-rerun/2026-10-06-independent-review]]. preEE duplicates overturn earlier “era-specific only” argument.|
|Correction bugs found in investigation|Main|MeasuredJER/top-pT/Type1/e-smearing/c-tag/WH failures; later implementations do not establish new full data/MC closure.|
|Signal LHE/FxFx problem and selected-region validation|Main|Original GEN figures, region_scale_acceptance.png; no claim repair regenerates missing events.|
|Gridpack rebuild and communication|Main|4FS validation; latest Chirayu report to Sebastiano overrides stale draftNOTSENT. H+b not assigned H+c numerical checks.|
|Ratio derivation,decay transfer,Run2 reco closure|Main|[[Projects/HToWW/samples-and-production/flavour-schemes/2026-09-30-fs-shape-systematic-validation]], official samples only.|
|Jet multiplicity not covered by ratio|Backup + visible main caveat|StandaloneRun2χ²23/5; not newRun3 result.|
|A versus B strategy|Main|CurrentRouteB integration; historical no3FSWW reason against stitching is superseded.|
|Leptons and SFs|Main|ONNX parity and producer comparison; no unsupported double-counting assertion.|
|negrwv2|Main|Corrected report,held-out sample and residual-bias plot. Ensemble spread not guaranteed to cover bias.|
|Each detector/theory/rate source|Dedicated walkthrough|[[Projects/HToWW/combine-systematics/2026-11-12-current-ab-systematics-status]], physical meaning, construction, scope and check boundary. Theory citations distinguish prescription, calculation and open gaps.|
|Framework storage/timing/problem→solution|Main|Measured150×different-output storage and33%one-file timing; no100×runtime claim.|
|Five-fold event MVA|Main|Method only; no unavailableROC/AUC improvement.|
|Validation duplication|Backup|Bounded diagnostic and same-hardware reproducibility, no new physics result.|
|October prefit shapes|Backup|Six channels, no real data_obs, cannot be captioned data/MC.|
|Likelihood scan|Backup|August single-era1034baseline only. No new October/A/B scan found; likelihood crossing not equated toCLs.|
|Minor sample/rate/correction/integrity updates|Final appendix|minor-updates.json includes note commits/status; progression snapshots consolidated.|
|FreshA/Blimits,MVAcurves,lnN-onlyfit|Not populated|No completed production result in inspected records. Readiness/tests are not a result.|
|A yields JSON|Not promoted|File exists but split-shard aggregation and negrw-v2 normalization/variance need checking; do not present an unchecked sum as final yields.|
|Operational queues, retries,account limits|Not main|No queued/running statuses in the presentation. Scientific implementation boundaries retained.|
|CombineAgent,agentsetup,reorganization|Excluded|Different project / task.|
|Private exploratoryγγflavour-scheme results|Excluded|29Sept“NEVER for presentations”decision. Official-sample validation only.|

## Direct source checks

- Old combined card `/eos/user/c/cgupta/higgscharm/outputs/combine/full/v12_hplusc_full_run3.txt`: parsed process and scalevar rows; **everyttentry is“-”** forμR,μF,μRμF. Non-ttprocesses retain1.0. A floating normalization alone does not justify removing all shapes; this is the specific old-card prescription.
- `runall/band_breakdown.py`: band contains MCstat+allweightvariations, excludes object shifts andlnN. Right panel of overview is an approximation assuming the scale contribution istt-dominated.
- Separate slope study has20bins and nominalMETχ²418.7; band study has19bins/χ²308.6. Do not mix these test definitions or claim the pre-fix JESDown improvement identifies the physical cause.
- V1 and V2 limits: Combine10.6.0,AsymptoticLimitsCLs,seed123456. V1median703,16/84%=469.0242/1106.5151. V2median691,16/84%=461.0181/1093.1359. V2build log includes nontrivial Higgs/st/Vjets rescalings and unchanged diboson. These results do not establish a new adopted prescription.
- Theory sources linked on relevant pages: LHCHWG-2026-007§4.3/4.4/5.3, PDF4LHC15§6.2, PDF4LHC21§6.3.3, LHCHWG-2025-011Table1, AN-23-102§7.1/Table16, YR4. H+cPDF7.43%is our gridpack calculation; H+cαS still lacks process-specific rate. Inherited background percentages are not relabelled freshRun3calculations.

## New central sample inventory

Read-only DAS queries use the existing proxy, never renew credentials. Full query results and scope accompany the inventory; current-analysis samples, alternate systematic samples and2024available equivalents must not be silently combined. Dataset version/extension policy and matching gaps must remain visible. See the companion inventory note once complete.

## Review boundary

Requested next: Claude content/figure/statistics review inspired by the CERN skill, direct corrections, then keeper review and repeat only for unresolved substantive findings. Preserve localPDF/PNGignores and unrelated dirty edits. No general vault lint/organization or push of unrelated pending commits in this task.
