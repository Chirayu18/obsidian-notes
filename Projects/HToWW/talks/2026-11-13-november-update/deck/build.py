#!/usr/bin/env python3
"""November HToWW update, revision 2. Higgs2026 template, internal CMS.
Build: python3 build.py && node render.mjs --revision=2
Numbers and plots are recorded artifacts, not new analysis results.
"""
from pathlib import Path
from urllib.parse import quote
import json
D=Path(__file__).resolve().parent
REV=2
N={
'plan':'Projects/HToWW/talks/2026-11-12-november-update-slide-plan.md',
'frame':'Projects/HToWW/talks/2026-11-12-framework-presentation-decision.md',
'evening':'Projects/HToWW/talks/2026-11-12-evening-results-and-restart-handoff.md',
'old':'Projects/HToWW/samples-and-production/full-rerun/2026-10-01-full-rerun-plan-and-findings.md',
'prod':'Projects/HToWW/samples-and-production/full-rerun/2026-11-12-direct-continuation-training-launch.md',
'b':'Projects/HToWW/samples-and-production/full-rerun/2026-11-12-b-fold-startup-fix.md',
'route':'Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train.md',
'state':'Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state.md',
'syst':'Projects/HToWW/combine-systematics/2026-11-12-current-ab-systematics-status.md',
'alpha':'Projects/HToWW/combine-systematics/2026-11-12-hplusc-alphas-rate-sources.md',
'lep':'Projects/HToWW/2026-11-10-lepton-sf-provenance-check.md',
'ggtt':'Projects/HToWW/samples-and-production/full-rerun/2026-11-12-ggtt-summer23-replacement-and-retry3.md',
'speed':'Projects/HToWW/framework/optimization/2026-11-05-speedup-patches.md',
'dup':'Projects/HToWW/framework/2026-11-12-bhive-validation-dupfix-gpu-readiness.md',
'negrw':'Projects/HToWW/negative-weights/2026-11-12-negrw-g1-g2-provenance-and-corrected-stats.md',
'ntrain':'Projects/HToWW/negative-weights/2026-11-12-negrw-retraining.md',
'nreview':'Projects/HToWW/negative-weights/2026-11-12-negrw-v2-acceptance-review.md',
'scorer':'Projects/HToWW/framework/2026-11-12-train-card-scorer-implemented.md',
'grid':'Projects/HToWW/samples-and-production/gridpacks/slides-sebastiano-2026-11/4fs_r3.html',
}
def link(key,label=None):
 p=N.get(key,key);return '<a href="obsidian://open?vault=obsidian-notes&amp;file='+quote(p,safe='')+'">'+(label or key)+'</a>'
def refs(*pairs):return ' · '.join(link(k,t) for k,t in pairs)
def bullets(*items):return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def fig(name,cap):return '<figure><img src="assets/'+name+'" alt="'+cap.replace('"','')+'"><figcaption>'+cap+'</figcaption></figure>'
def col(*items,ratio=None):return '<div class="columns"'+(' style="grid-template-columns:'+ratio+'"' if ratio else '')+'>'+''.join('<div>'+i+'</div>' for i in items)+'</div>'
def metric(value,label,detail=''):return '<div class="metric"><span>'+value+'</span><b>'+label+'</b><small>'+detail+'</small></div>'
def table(head,rows,cls=''):
 return '<table class="t '+cls+'"><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
slides=[]
def add(sid,title,sub,body,take,source,notes='',backup=False,layout=''):
 n=len(slides)+1
 forward={
 'analysis':[('definitions','terms → backup')],
 'gridpack-validation':[('backup-gridpack-weights','weight checks → backup'),('backup-gridpacks','3FS validation → backup')],
 'negrw-limits':[('backup-negrw-sr','SR diagnostics → backup')],
 'status':[('backup-production','input inventory → backup')],
 'syst-overview':[( 'backup-syst-norm','rates/PU'),('backup-syst-lepsf','lepton SFs'),('backup-syst-lepscale','lepton shifts'),('backup-syst-jets','jets/MET'),('backup-syst-theory','theory'),('backup-syst-pdf','PDF/αS'),('backup-syst-scheme','scheme/negrw'),('backup-syst-rates','fit model'),('hdamp','hDamp'),('backup-ctag','c-tag')]
 }
 if sid in forward:
  source += ' · Backup: ' + ' · '.join('<a href="#/'+target+'">'+text+'</a>' for target,text in forward[sid])
 slides.append({'id':sid,'title':title,'backup':backup,'html':f'''<section class="slide {layout}" id="{sid}" data-n="{n}" data-backup="{str(backup).lower()}">
<header><h2>{title}</h2><p class="sub">{sub}</p></header>
<div class="content">{body}</div>
<p class="takeaway">{take}</p>
<p class="provenance">{source}</p><p class="internal">CMS internal · preliminary</p>
<aside class="notes">{notes}</aside></section>'''})
# Title uses the same gradient, logo tile, typography and orange rule as Higgs2026.
slides.append({'id':'title','title':'Higgs + charm, H → WW','backup':False,'html':'''<section class="slide title-slide" id="title" data-n="1" data-backup="false">
<div class="logos-tile"><img src="assets/CMSlogo_color.png" alt="CMS"><img src="assets/VUB_logo.png" alt="VUB"></div>
<div class="title-block"><h1>Higgs + charm, H → WW<br>Run 3 analysis update</h1><p class="venue">Internal analysis discussion · 13 November 2026</p><p class="speaker">Chirayu Gupta</p><p class="affil">IIHE · Vrije Universiteit Brussel</p></div>
<div class="title-agenda"><span>Four-era reference</span><span>Signal modelling</span><span>New A/B analysis</span></div><p class="title-scope">Historical results, completed checks and the path to the next limit</p>
<aside class="notes">Internal CMS talk. The October result is a pre-fix reference. No new A/B limit or trained-model performance is claimed. Main status follows the saved 12 November 20:29 CET record.</aside></section>'''})
add('analysis','The H+c analysis in Run 3','H → WW → eμνν · four eras · 61.9 fb⁻¹',
col('<h3>A rare signal in a large background</h3>'+bullets('One opposite-flavour eμ pair, missing transverse momentum &gt; 45 GeV, and a c-jet candidate.','A six-class event classifier separates H+c, Higgs backgrounds, tt, single top, diboson and V+jets.','Each event enters the signal region (SR) or one of five control regions (CRs).'),
'<div class="formula panel">H + c → eμ + p<sub>T</sub><sup>miss</sup> + c</div><h3>What changes in this round?</h3>'+bullets('Two descriptions of the signal: central 4FS and stitched 3FS/4FS.','New prompt-lepton selection and retrained event classifiers.','A future full-systematics fit with two SRs: N<sub>c-jet</sub> = 1 and ≥ 2.')),
'The analysis is being rebuilt around the updated objects and signal samples.',refs(('plan','Talk plan'),('syst','Current model')),
'4FS and 3FS are defined on the signal-comparison slide before the detailed construction. The historical fit had a merged SR; the two-SR result is a future production result, not the October fit.')
add('progress','August → October: building the four-era analysis','Establish the reference before introducing the new corrections',
'<div class="milestones"><div><h3>August</h3>'+metric('1 era','2022postEE reference','Expected μ limit 1034')+'<p>Initial event-MVA analysis and systematic checks.</p></div><div><h3>October</h3>'+metric('4 eras','Run 3 combination','61.9 fb⁻¹')+'<p>Central signals, additional backgrounds, corrected card construction.</p></div><div><h3>This update</h3>'+metric('A / B','Controlled signal comparison','new leptons + retraining')+'<p>Generator repairs, new reweighting, model safeguards and compact processing.</p></div></div><p class="context">Coverage changed between August and October. The two limit numbers are not an isolated measurement of a single improvement.</p>',
'The October combination is our reference point, not the final corrected result.',refs(('plan','Agreed August→October storyline'),('old','October analysis record')),
'August reference is the 19 August analysis-overview deck as recorded in the agreed plan. Do not imply the decrease from1034 to691 measures only algorithmic improvements or only luminosity.')
add('historical-result','October reference: expected μ < 691','Blind Asimov · expected 95% CL · pre-fix four-era model',
col('<div class="result hero"><div class="rlab">Run 3 combined · 61.9 fb⁻¹</div><div class="rval">μ<sub>95</sub><sup>exp</sup> &lt; 691</div><p>μ is the signal rate relative to the SM prediction.</p></div>'+table(['Period','Expected full-systematics limit'],[['2022','905'],['2023','1077']]),
'<h3>What limited this reference?</h3><div class="hbars"><div><label>Full model</label><i style="width:96%">691</i></div><div><label>Freeze autoMCStats</label><i style="width:85.6%">616</i></div><div><label>Stat-only</label><i class="orange" style="width:47%">338.5</i></div></div><p class="small">Different nuisance configurations of the same historical card; these bars are not nuisance impacts.</p>'),
'Keep 691 as a dated benchmark; the corrected A/B fits are still to come.',refs(('old','7 October result table'),('plan','Presentation baseline')),
'Important pre-fix caveats: JER no-op, WH cross section zero, partial signal scale repair, NLO-like H+c normalization and flat30% scheme lnN. The stat-only and freeze-autoMCStats configurations are historical. Do not combine or subtract these as independent uncertainty components.')
add('higgs-scale','A diagnostic of the Higgs-background scale treatment','Same old card · vary the rate/shape bookkeeping only',
col(table(['Variant','Treatment'],[['V0','Keep the historical scale shapes and rate terms'],['V1','Make Higgs-background scale shapes shape-only; retain the separate rate term'],['V2','Also apply this treatment to single top, diboson and V+jets']]),
'<div class="hbars"><div><label>V0 reference</label><i style="width:86.4%">691</i></div><div><label>V1 diagnostic</label><i class="orange" style="width:87.9%">703</i></div></div><p class="context">V1 changes the median by about +1.7%. V2 had no recorded result at the 18:51 source check.</p><p class="small">V1 expected 16–84% band: 469–1107.</p>'),
'This tests an uncertainty prescription; it is not a new corrected A/B result.',refs(('evening','Saved scale diagnostic and logs')),
'V0=691 was recovered from parent history; the V1 log was directly read at18:47. V2 was still running at18:51 and no completion is asserted. The treatment has not been adopted as the final physics prescription.')
add('signal-samples','Two issues in the central signal samples','Separate the weight problem from the FxFx merging problem',
col('<h3>Variation weights</h3><div class="result"><div class="rval">scale ≈ ×2</div><div class="rlab">central sample: anomalous LHE variations</div></div>'+bullets('External reweighting misses the running charm-Yukawa dependence.','A per-event workaround is implemented and checked; seek agreement on the prescription.'),
'<h3>FxFx merging</h3><div class="panel"><b>Veto restricted to |η| &lt; 2.5</b><p>The fragment does not use the full-η merging setup of the clean reference.</p></div>'+bullets('Affects the forward-parton population.','Reweighting cannot regenerate missing events; corrected generation is the long-term fix.')),
'Both issues are reported to GEN; the current samples remain a provisional analysis input.',refs(('plan','Chirayu’s message to Thomas / GEN'),('grid','4FS validation slides')),
'User says nominal samples are usable and expects a small effect inside the central selection. The ≈1–2% statement is the communicated selection-level estimate, not a new measurement here. Do not imply the scale workaround fixes the fragment’s nominal-generation defect.')
add('gridpack-validation','Corrected gridpack: checks against the clean reference','H+c 4FS · LHE+GEN validation · corrected fragment',
col(fig('gridpack_higgs_pt.png','Higgs pT: rebuilt el8 gridpack vs official clean reference.'),
'<h3>Independent generation, consistent outputs</h3>'+table(['Quantity','Rebuilt','Reference'],[['Matched σ [fb]','97.4 ± 1.6','96.5 ± 1.6'],['PDF/member 0','0.999','0.999'],['Negative-weight fraction','0.217','0.216'],['μR×2 ratio','0.966','0.967']])+'<p class="small">≈10k matched events per sample; all nine scale points agree within 0.7%. These are generator-validation cross sections, not the NNLO analysis normalization.</p>',ratio='1.15fr 1fr'),
'Corrected H+c/H+b gridpacks are sent; full detector-level reproduction is still ahead.',refs(('grid','4FS r3 validation'),('plan','Latest send status')),
'H+c numbers from existing validation slides:10370 vs10296 matched events, Higgs-pT χ²/ndf1.4/10. H+b sent status is Chirayu’s own report; do not transfer the H+c numerical validation to H+b. Three-flavour validation is in backup.',layout='plot-slide')
add('arms','Flavour scheme: two complementary strategies','4FS: massless charm in the proton · 3FS: massive charm produced in the hard process',
col('<div class="arm-title">A <span>Ratio method</span></div><h3>Keep central 4FS signal</h3>'+bullets('Use the leading GEN c-hadron pT ratio to make a 3FS-like shape.','Up = 3FS-like; Down = 2 − Up.','This shape treatment replaces the historical flat 30% rate uncertainty.'),
'<div class="arm-title orange">B <span>Stitching method</span></div><h3>Join complementary GEN regions</h3><div class="partition"><div>4FS<br><b>N<sub>c-jet</sub> = 0</b></div><div>3FS<br><b>N<sub>c-jet</sub> ≥ 1</b></div></div><p class="small">GEN c jets: pT &gt;10 GeV, |η|&lt;2.5, R=0.4. Per-era generated-weight normalization. A’s separate scheme nuisance is off in B.</p>'),
'Same analysis and NNLO target rate; compare the two signal descriptions explicitly.',refs(('route','Stitching implementation'),('state','Ratio-method prescription')),
'Both arms use σ×BR=0.0016626pb. B does not automatically close scale/PDF overlap or missing-rate coverage questions; retain those as card-stage checks. This is not a new central3FS production claim.')
add('samples','Rates and sample coverage brought up to date','One mass convention, with remaining component checks explicit',
'<div class="milestones"><div><h3>Signal rate</h3>'+metric('0.0016626 pb','H+c σ×BR','NNLO target in all four eras')+'<p>Running-Yukawa correction applied to the scale-variation treatment.</p></div><div><h3>Higgs backgrounds</h3>'+metric('125.09 GeV','Normalization convention','H→ττ rates updated')+'<p>2023preBPix ggH→ττ replaced with Summer23 v14.</p></div><div><h3>Coverage still open</h3>'+bullets('Re-derive remaining Higgs rates consistently.','Check ttH→ττ: current ttHnonBB group is not an inclusive non-bb sample.')+'</div></div><p class="context">A rate convention does not change the generated Higgs mass or event kinematics.</p>',
'The H→ττ update is complete; a global Higgs-rate validation is not yet claimed.',refs(('ggtt','Summer23 replacement'),('prod','Normalization updates'),('syst','Remaining rate scope')))
add('leptonmva','Prompt-lepton selection aligned with HWW','Reference working points, vectorized inference and scale-factor provenance',
col('<h3>Physics selection</h3>'+bullets('Muon: HWW tight ID × tight isolation × prompt-lepton MVA.','Electron: POG Medium × prompt-lepton MVA, with separate reconstruction factors.','All eight SF files match latinos byte-for-byte; nominal factorization follows the producer chain.'),
'<h3>Reference checks</h3>'+metric('≈3×10⁻⁷','Maximum ONNX–TMVA score difference','24,484 muons · 25,713 electrons')+'<div class="result"><div class="rval">563 → 423 selected events</div><div class="rlab">One H+c file, old vs new leptons (−25%)</div></div>'),
'New event populations require retraining; numerical parity is not a calibration measurement.',refs(('state','Lepton inference checks'),('lep','SF producer comparison')),
'Muon maxdifference3.05e-7, electron3.27e-7 including threshold-tie coverage. SF factorization concern from the earlier review is not supported by the producer comparison. Measurement provenance/correlations and c-tag calibration are separate questions.')
add('negrw','Negative weights: retraining the reweighting model','negrw v2 · all four eras · updated lepton selection',
col('<div class="formula panel">w′ = |w| g(x)<br><small>g(x) = 2P(w &gt; 0 | x) − 1</small></div>'+bullets('A generator-level classifier estimates the signed-weight cancellation.','20 features, 20 boosted-tree members; 7.6M training rows.','About 1.5M held-out events test closure; the training region excludes the updated eμ SR.')+'<p class="small">SR closure: v2 1.011 ±0.021; July 1.019 ±0.021 (17,627 events).</p>',
fig('04_closure_holdout_era_dataset.png','Held-out closure by era and sample: v2 (blue), July (red).'),ratio='0.9fr 1.2fr'),
'v2 is adopted for A and B; the training inputs now match the analysis selection.',refs(('ntrain','Retraining'),('negrw','Corrected closure statistics')),
'The estimator can be negative; do not call every output weight positive. Closure is a ratio of signed sums, with correlated delta-method errors in the corrected report. Shape agreement between two models is not proof of agreement with the original signed distribution.',layout='plot-slide')
add('negrw-limits','Overall closure hides sample-level shape bias','The ensemble spread is not a complete model-bias uncertainty',
col(fig('09_shape_renorm_lhe_vpt_njets_ge1_DYto2L_2Jets_50.png','DY mass&gt;50, Njet≥1: residual shape after sample-yield renormalization.'),
'<h3>What the checks show</h3>'+table(['Held-out closure','v2'],[['All samples','0.9984'],['DY 10–50','0.8980'],['W+0J','0.9855']])+'<p>Per-era/sample renormalization restores rates. It does not remove every shape discrepancy.</p><div class="result"><div class="rval">χ²/ndf = 47.2/20</div><div class="rlab">DY shape example; 35.0/20 with the nuisance</div></div>',ratio='1.2fr 0.9fr'),
'Final fit-bin closure remains a required check after event-MVA scoring.',refs(('negrw','Corrected G1/G2'),('nreview','Acceptance review')),
'This is a limitation in both v2 and July; July shape χ²47.9/20 for the shown diagnostic. The band is ensemble spread, not an independently validated envelope of all method biases.',layout='plot-slide')
add('syst-overview','Systematics: implementation and physics scope','Detector calibration, generator modelling, rate terms and finite MC',
col('<h3>Detector / object response</h3>'+bullets('Lepton efficiencies and momentum/energy shifts.','Total JES, JER and soft/unclustered MET shifts.','Pileup and luminosity; c-tag SFs remain provisional.'),'<h3>Generator / fit model</h3>'+bullets('ISR/FSR, μR/μF and PDF variations; process scope matters.','Top-pT and Higgs+heavy-flavour modelling.','Flavour scheme, negrw ensemble and autoMCStats.'))+'<div class="context"><b>Still open:</b> H+c αS rate, component-aware Higgs rate/BR terms, final empty-template policy and fit-bin checks. hDamp implementation is deferred.</div>',
'Configured sources are not yet measured impacts in the new A/B fit.',refs(('syst','Current inventory'),('alpha','Signal αS provenance')),
'Full explanations and implementation/evidence status for every source are in backup. tt is excluded from configured scalevar/ps rows, not automatically from all theory-named nuisances. Trigger SFs remain disabled by decision; not a measured zero.')
add('speed','Framework optimization: remove repeated work','Measured component improvements; separate storage and timing claims',
col('<h3>Redundant event storage</h3>'+metric('2,858 MB → 18.9 MB','Same historical tt partition','Legacy output vs nominal TRAIN output')+'<p>≈150× smaller for these different output contents: repeated shifts, weight columns and precision dominate.</p>',
'<h3>Controlled timing benchmark</h3>'+metric('46.5 s → 31.1 s','One H+c chunk','85,732 events; −33% wall time')+'<p>NumPy parquet writer, cached YAML and correction sets. Seeded outputs match byte-for-byte.</p>')+'<p class="context">Production median 18 min, p90 50 min; 11% failed in the recorded grid snapshot. Retries and input access dominated campaign wall time.</p>',
'These are measured comparisons, not a claimed 150× runtime speedup.',refs(('frame','Storage comparison and agreed framing'),('speed','One-file timing'),('plan','Production snapshot')),
'Legacy stores nominal+15 shifts and all53weight columns; TRAIN is nominal-only. The proposed combined writer will store more than TRAIN: its size/runtime have not been measured. 16/16 and64/64parquet equality checks refer to the controlled optimization test.')
add('framework-flow','A compact event record for offline iteration','Problems found → solutions implemented → combined workflow',
'<div class="problem-flow">'+table(['Problem','Solution'],[['Weight columns repeated in shifted tables','Keep weight variations in nominal; shifts carry only needed quantities'],['Unused columns and excess precision','Compact columns and suitable precision; preserve event IDs'],['Histogram-only outputs tie iteration to NanoAOD','Retain event inputs for offline training, scoring and rebinning'],['Missing inputs or stale model outputs','Coverage, provenance and model-compatibility guards']])+'</div><div class="workflow"><div>One NanoAOD<br>pass</div><span>→</span><div>Compact nominal<br>+ shifted inputs</div><span>→</span><div>Offline MVA<br>+ templates</div><span>→</span><div>Combine</div></div>',
'The core components are implemented; a bit of refactoring remains to bring them together.',refs(('frame','Chirayu’s final presentation decision'),('scorer','Offline scorer now implemented')),
'Intended combined single-pass workflow, not claimed complete. The new model cannot be used before it is trained: store event inputs first, then score offline. The exact user wording is “a bit of refactoring”; this is his presentation preference, not an engineering-effort estimate. Automatic Condor retries/global redirector remain planned.',layout='flow-slide')
add('mva','Event classifier: five held-out models per arm','One validation owner; every fitted event has an out-of-training score',
'<div class="workflow folds"><div>event % 5<br>test fold i</div><span>↘</span><div>Model i<br>trained on other folds</div><span>→</span><div>Score fold i<br>once in the fit</div></div>'+col('<h3>b-hive owns validation</h3>'+bullets('Training list split 85/15 internally; seed 20261112.','Roughly 68% training, 12% validation, 20% held out, by constructed files.'),'<h3>Physics recipe kept explicit</h3>'+bullets('Six classes, 26 features; 30 epochs, batch 1024, learning rate 10⁻³.','Class weights only; event-weight columns do not enter the loss.')),
'A and B require ten trained models in total; submitted jobs are not completed models.',refs(('dup','Training readiness and seed'),('plan','A/B strategy')),
'Features:14kinematic+11c-tagonehot+nSV. Cached constructed datasets use unique fold/split identities. RUN/registration guard feature/selection hashes, class order and provenance. Same test fold remains assigned for object-shifted copies.')
add('mvacheck','A duplicated validation batch changed model selection','Found, reproduced and corrected before the new training',
col('<div class="result"><div class="rlab">Real validation fixture ·129 files</div><div class="rval">38,700 events<br>→ 103,980 emitted rows</div><p>2.69× duplication before the fix</p></div>'+bullets('The leftover partial batch was emitted again.','Validation loss and inference metrics were affected; training updates were unchanged.'),
'<h3>Checks after the fix</h3>'+bullets('Exactly-once tests for partial, tiny and exact-size files with 0/2/3 loader workers.','Epoch-0 weights identical before/after.','Same seed on the same A100: bitwise-identical model weights.','Registration rejects pre-fix or mixed-code fold provenance.')),
'The new best-epoch selection uses an exactly-once validation sample.',refs(('dup','Duplication regression and GPU repeatability')),
'Inference fixture:170465emitted rows for64073events. Reproducibility boundary is same hardware/setup; do not claim universal cross-GPU bitwise equality. The v11 validation/inference was also affected, so its published internal metrics are not a clean baseline.')
add('results','Fast iteration cards from the TRAIN event records','New offline scorer implemented; production fold models still needed',
'<div class="workflow"><div>Frozen TRAIN<br>event inventory</div><span>→</span><div>Held-out score<br>+ current negrw v2</div><span>→</span><div>One nominal<br>template pass</div><span>→</span><div>Two card<br>variants</div></div>'+col('<h3>Statistical iteration</h3>'+bullets('Stat-only: no shape or lnN terms.','Retain autoMCStats and floated tt normalization.','Optional rate-systematics variant shares identical nominal templates.'),'<h3>Evidence and boundary</h3>'+bullets('7/7 focused tests, including ROOT readback and signed variance.','One real A/B event checked for generator schema and negrw compatibility.','Current TRAIN schema needs a merged SR; the full fit will use two SRs.')),
'The tool is ready for model validation; it has not produced an A/B limit yet.',refs(('scorer','Local analysis commit 5b25295; tests and schema check')),
'No production scoring or Combine run. Original stored July negrw weights are ignored and v2 rescored from generator columns; normalize after all shards merge. A merged-SR iteration result must not be compared as though identical to the intended split-SR full-systematics fit.')
add('status','Production: complete inputs, training underway','Saved 12 November 20:29 CET snapshot; refresh before presentation',
'<div class="milestones"><div><h3>Inputs complete</h3>'+metric('A: 6.96M','Selected training rows','2,437 MC markers')+metric('B: 6.98M','Selected training rows','2,572 MC markers')+'</div><div><h3>Fold processing</h3>'+metric('A: 3 running','2 queued','Dataset construction observed')+metric('B: queued','5 folds in one job','Sequential, approved submission')+'</div><div><h3>Results not yet available</h3>'+bullets('No completed production fold.','No exported or registered model.','No new A/B templates, impacts or expected limits.')+'</div></div>',
'Preparation and job submission are complete; trained-model performance is still pending.',refs(('scorer','Latest execution snapshot'),('b','B preparation and submission')),
'Exact saved selected rows A6959308 B6978013. B single job9706954 underDAG9706953. Afolds9706926–9706928running,9706929–30idle. This slide is a dated saved record, not live queue monitoring. No new job operations performed by keeper.')
add('open','Progress made, and questions for the conveners','Signal generation, flavour schemes and the next controlled comparison',
col('<h3>What is now in place</h3>'+bullets('Four-era inputs for both signal arms.','Reference-checked leptons, negrw v2 and reproducible training setup.','Corrected gridpacks sent; compact processing and offline-card components built.'),'<h3>Where guidance is needed</h3>'+bullets('Existing samples: endorse the per-event scale workaround, or another prescription?','FxFx forward merging: agree the treatment while corrected samples are reproduced?','Flavour scheme: is ratio method A versus stitched B the right comparison?')),
'Next result: held-out A/B iteration limits, followed by the full-systematics two-SR fit.',refs(('plan','Chirayu’s GEN / convener questions'),('frame','Framework framing'),('scorer','Result dependency')),
'Analysis follow-ups remain: provisionalc-tagcalibration, H+cαSrate, H+bPDF+αSoverlap, HiggsBRscope, ttHττcoverage, negrwfit-binclosure. hDamp is deferred by instruction; no alternative-sample template is claimed.')
# Backup starts only after the main conclusions. Every page links back to its main context.
slides.append({'id':'backup','title':'Backup','backup':True,'html':f'''<section class="slide divider" id="backup" data-n="{len(slides)+1}" data-backup="true"><div class="line"></div><h1>Backup</h1><p class="divsub">Systematic prescriptions · validation plots · production provenance</p><p class="backup-home"><a href="#/open">← Main conclusions</a></p></section>'''})
add('definitions','Backup: definitions and fit conventions','Reference terms; implementation details live in the companion notes',
table(['Term','Meaning'],[['Arm A / Arm B','Central 4FS with scheme-shape uncertainty / stitched 3FS+4FS signal'],['TRAIN / RUN','Nominal feature-event output / inline-scored systematic templates'],['SR / CR','Signal region / control region selected by classifier argmax'],['negrw g(x)','Generator-level signed-weight cancellation estimate, 2P(positive|x)−1'],['lnN / shape / rateParam','Rate uncertainty / varied template / fitted normalization'],['autoMCStats','Finite MC-bin statistics from signed-weight variance, not a flat 10%'],['Current iteration / final fit','Merged SR from present TRAIN schema / intended two c-jet-count SRs']]),
'Keep the statistical model and the saved-output schema attached to every result.',refs(('syst','Inventory'),('scorer','TRAIN-to-card conventions')),backup=True)
for sid,item in json.loads((D/'systematics.json').read_text()).items():
 rows=[];details=[]
 for r in item['rows']:
  rows.append([r['name'],r['effect'],r['construction']+'<br><span class="check">'+r['evidence']+'</span>'])
  details.append(r['nuisance'])
 add(sid,item['title'],'Backup · what it is, how it is varied, and current evidence',table(['Source','Physical effect / why it matters','Variation, scope and check'],rows,'systematics'),
 'New template effects and fit impacts remain to be checked after scoring.',item['source']+' · <a href="#/syst-overview">← systematics overview</a>',
 'Implementation nuisance names: '+', '.join(details)+'. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.',backup=True,layout='systematics-slide')
add('hdamp','Backup: hDamp probes tt matching','Deferred until after MVA training, by instruction',
col('<h3>Physical uncertainty</h3>'+bullets('POWHEG h_damp controls the damping of hard real emission relative to shower matching.','Changes extra-jet activity and can migrate tt events between c-jet categories.','ISR/FSR shower weights do not automatically cover this matching variation.'),'<h3>Implementation still pending</h3>'+bullets('Dedicated Hdamp158/418 tt samples configured in all four eras.','Normalize each alternative using its own full generated sumw.','Need acceptance, shape and MC-stat checks before adding the template nuisance.')),
'Configured samples are not an implemented or validated alternative-sample nuisance.',refs(('prod','Deferred hDamp scope'),('syst','Current inventory'))+' · <a href="#/syst-overview">← main</a>',backup=True)
add('backup-negrw-sr','Backup: negrw in the selected eμ signal region','17,627 events · corrected v2 report',
col(fig('07_sr_vpt.png','SR V-pT distributions: original signed weights, v2 and July.'),fig('09_shape_renorm_lhe_vpt_all_WtoLNu_2Jets_1J.png','W+1J: shape residual after per-sample renormalization.')),
'Model-to-model agreement does not close the common residual shape bias.',refs(('negrw','Corrected statistics'))+' · <a href="#/negrw-limits">← main</a>',
'W+1J χ²139.4/20 v2185.5/20July, 120.1/155.6withnuisance in savedreport. The horizontal nuisanceband should not be represented as independent measurement errors.',backup=True,layout='plot-slide')
add('backup-ctag','Backup: c-tag categories enter the event MVA','ParticleNet CvsL × CvsB · provisional calibration',
col('<h3>Eleven one-hot categories</h3><div class="category-strip"><span>L0</span><span>C0–C4</span><span>B0–B4</span></div>'+bullets('Leading c-jet candidate is categorized in the two tagger discriminants.','Categories are model inputs, not just a downstream plotting choice.','The calibration is provisional while Livio’s update is awaited.'),
'<h3>Versioned category definition</h3><p class="small">CvsL edges:0,0.250,0.452,0.808,1</p><p class="small">CvsB edges:0,0.006,0.017,0.055,0.761,0.944,0.985,0.995,1</p><div class="panel">Changing category edges changes the inputs and can force reprocessing/retraining. Changing only SF weights is a different operation.</div>'),
'Tagger category consistency must be preserved through training, scoring and fitting.',refs(('syst','c-tag status'))+' · <a href="#/syst-overview">← main</a>',backup=True)
add('backup-gridpack-weights','Backup: scale and PDF weights after the rebuild','H+c 4FS · same corrected WW fragment in rebuilt and reference samples',
col(fig('gridpack_scale_higgs_pt.png','Scale-variation response versus Higgs pT: rebuilt gridpack and clean reference.'),
'<h3>Weight-level checks</h3>'+table(['Quantity','Rebuilt','Reference'],[['PDF/member 0','0.999','0.999'],['μR×2 σ ratio','0.966','0.967'],['μR×0.5 σ ratio','1.049','1.044']])+'<p>The broken central sample had PDF/member0 ≈2.26 and anomalous scale variations.</p><p class="small">All nine scale points agree within0.7% in the ≈10k-event generation check.</p>',ratio='1.15fr 1fr'),
'Generation-level agreement supports the rebuilt setup; detector-level reproduction remains separate.',refs(('grid','4FS validation, full numbers'))+' · <a href="#/gridpack-validation">← main</a>',backup=True,layout='plot-slide')
add('backup-gridpacks','Backup: private 3FS validation','Reused official gridpack; H→WW decay configuration',
col(fig('gridpack_3fs_higgs_pt.png','Production-level LHE Higgs pT: private WW versus official γγ reference.'),
'<h3>What is compared</h3>'+bullets('Production variables before Higgs decay.','The official gridpack is reused unchanged.','Decay-specific jet/lepton distributions are checked separately.','The 3FS re-NANO supplies the PDF replica weights needed by Arm B.')+'<p class="small">Do not use decay-dependent jet agreement as a production-only equivalence test.</p>',ratio='1.2fr 0.85fr'),
'Generator validation and central-sample reproduction are separate stages.',
'<a href="../../../samples-and-production/gridpacks/deck/3fs.html">3FS validation deck</a> · <a href="#/gridpack-validation">← main</a>',backup=True,layout='plot-slide')
add('backup-production','Backup: traceable inputs and output boundaries','Four eras · local code commits · preserved preparation manifests',
table(['Artifact','Saved record'],[['Original TRAIN MC partitions','A 2437; B 2572 (completion markers and full input checks)'],['Original selected-event parquet shards','A 22,613; B 24,598 before later fold splitting'],['Selected rows after preparation','A 6,959,308; B 6,978,013'],['Classifier training','Five held-out models per arm; B folds sequential in one Condor job'],['Offline scorer','Analysis local 5b25295; 7 focused tests and bounded real-schema check'],['Full-systematics result','Not yet produced; requires models, scoring, templates and final-card checks']]),
'Timestamps, manifests and model identities travel with every later result.',refs(('prod','Input inventory'),('b','B readiness'),('scorer','Latest scorer / queue record'))+' · <a href="#/status">← main</a>',backup=True)
# Exact Higgs2026 template plus scoped adaptations for Reveal navigation and offline reading.
head='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>HToWW November analysis update · Higgs2026 template · r2</title>
<link rel="stylesheet" href="../../../../../_shared/reveal/reset.css"><link rel="stylesheet" href="../../../../../_shared/reveal/reveal.css"><link rel="stylesheet" href="higgs2026-theme.css"><link rel="stylesheet" href="talk.css">
<noscript><style>html,body{height:auto!important;overflow:auto!important}.reveal,.reveal .slides{position:static!important;transform:none!important;width:auto!important;height:auto!important}.reveal .slides>section.slide{display:block!important;position:relative!important;transform:none!important;inset:auto!important;opacity:1!important;visibility:visible!important;margin:20px auto!important;pointer-events:auto!important}body{overflow-x:auto!important}</style></noscript></head><body><div class="reveal"><div class="slides">'''
tail='''</div></div><script src="../../../../../_shared/reveal/reveal.js"></script><script>Reveal.initialize({width:1280,height:720,margin:0,center:false,hash:true,transition:'none',backgroundTransition:'none',controls:true,progress:false,slideNumber:false,pdfSeparateFragments:false,pdfMaxPagesPerSlide:1});</script></body></html>'''
(D/'index.html').write_text(head+'\n'.join(s['html'] for s in slides)+tail)
(D/'slides.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='html'} for s in slides],indent=2,ensure_ascii=False)+'\n')
print(len(slides),'slides;',sum(not s['backup'] for s in slides),'main;',sum(s['backup'] for s in slides),'backup')

# Companion notes are generated from the evidence/interpretation annotations, not invented results.
import re,html
lines=['---','tags: [slides, speaker-notes]','status: active','date: 2026-11-12','source: laptop','---','','# November update r2: speaker notes','','Internal CMS talk. The old-card reference and new-production status are explicitly separate. No new A/B limit is claimed.','']
for i,s in enumerate(slides,1):
 raw=s['html'];notes=re.search(r'<aside class="notes">(.*?)</aside>',raw,re.S)
 takeaway=re.search(r'<p class="takeaway">(.*?)</p>',raw,re.S)
 text=(notes.group(1) if notes and notes.group(1).strip() else takeaway.group(1) if takeaway else 'Section divider.')
 text=html.unescape(re.sub('<[^>]*>',' ',text))
 lines += [f"## {i}. {html.unescape(re.sub('<[^>]*>','',s['title']))}",'',f"[Open slide](index.html#/{s['id']})",'',text,'']
(D/'speaker-notes.md').write_text('\n'.join(lines))
