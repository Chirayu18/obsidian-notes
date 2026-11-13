#!/usr/bin/env python3
"""November HToWW update, revision 4. Higgs2026 template, internal CMS.
Build: python3 build.py && node render.mjs --revision=4
Numbers and plots are recorded artifacts, not new analysis results.
"""
from pathlib import Path
from urllib.parse import quote
import json
D=Path(__file__).resolve().parent
REV=4
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
'audit':'Projects/HToWW/talks/2026-11-12-content-selection-audit.md',
'fs':'Projects/HToWW/samples-and-production/flavour-schemes/2026-09-30-fs-shape-systematic-validation.md',
'review':'Projects/HToWW/samples-and-production/full-rerun/2026-10-06-independent-review.md',
'breakdown':'Projects/HToWW/combine-systematics/2026-10-21-uncertainty-breakdown-run2-vs-run3.md',
'plots':'Projects/HToWW/plots.md',
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
<div class="title-agenda"><span>Four-era reference</span><span>Signal modelling</span><span>New A/B analysis</span></div><p class="title-scope">Four-era results · data/MC investigations · signal-model validation</p>
<aside class="notes">Internal CMS talk. The October result is a pre-fix reference. No new A/B limit or trained-model performance is claimed. Results are dated and source-linked; no unproduced A/B limit is implied.</aside></section>'''})
add('analysis','The H+c analysis in Run 3','H → WW → eμνν · four eras · 61.9 fb⁻¹',
col('<h3>A rare signal in a large background</h3>'+bullets('One opposite-flavour eμ pair, missing transverse momentum &gt; 45 GeV, and a c-jet candidate.','A six-class event classifier separates H+c, Higgs backgrounds, tt, single top, diboson and V+jets.','Each event enters the signal region (SR) or one of five control regions (CRs).'),
'<div class="formula panel">H + c → eμ + p<sub>T</sub><sup>miss</sup> + c</div><h3>What changes in this round?</h3>'+bullets('Two descriptions of the signal: central 4FS and stitched 3FS/4FS.','New prompt-lepton selection and retrained event classifiers.','A future full-systematics fit with two SRs: N<sub>c-jet</sub> = 1 and ≥ 2.')),
'The analysis is being rebuilt around the updated objects and signal samples.',refs(('plan','Talk plan'),('syst','Current model')),
'4FS and 3FS are defined on the signal-comparison slide before the detailed construction. The historical fit had a merged SR; the two-SR result is a future production result, not the October fit.')
add('progress','August → October: building the four-era analysis','Establish the reference before introducing the new corrections',
'<div class="milestones"><div><h3>August</h3>'+metric('1 era','2022postEE reference','Expected μ limit 1034')+'<p>Initial event-MVA analysis and systematic checks.</p></div><div><h3>October</h3>'+metric('4 eras','Run 3 combination','61.9 fb⁻¹')+'<p>Central signals, additional backgrounds, corrected card construction.</p></div><div><h3>This update</h3>'+metric('A / B','Controlled signal comparison','new leptons + retraining')+'<p>Generator repairs, new reweighting, model safeguards and compact processing.</p></div></div><p class="context">The1October audit also restored7 inactive nuisances: pileup, μID/iso, eID and the3 e-reconstruction bins. Coverage and model changed, so1034→691 is not an isolated algorithmic gain.</p>',
'The October combination is our reference point, not the final corrected result.',refs(('plan','Agreed August→October storyline'),('old','October analysis record')),
'August reference is the 19 August analysis-overview deck as recorded in the agreed plan. Do not imply the decrease from1034 to691 measures only algorithmic improvements or only luminosity.')
inventory=json.loads((D/'central-inventory.json').read_text())
def inv_group(p):
 if p in ['H+c','H+b','tt','Single Top','DY+Jets']:return p
 if p=='V+Jets':return 'W+jets'
 if p in ['WW','WZ','ZZ','WG']:return 'Diboson /Wγ'
 return 'Other Higgs'
eras=['2022preEE','2022postEE','2023preBPix','2023postBPix']
invrows=[]
for group in ['H+c','H+b','tt','Single Top','DY+Jets','W+jets','Diboson /Wγ','Other Higgs']:
 cells=[]
 for era in eras:
  rs=[r for r in inventory['current'] if r['era']==era and inv_group(r['process'])==group]
  cells.append(f"{len(rs)} / {sum(r['nevents'] for r in rs)/1e6:,.2f}M")
 invrows.append([group]+cells)
add('central-inventory','Central samples: full current-analysis inventory','DAS12November · cell = datasets / produced events before selection',
table(['Process']+eras,invrows,'inventory-table')+'<p><b>46 central nominal MC datasets per era</b>; selected by the current workflow. Private3FS, collision data and alternative systematic samples are counted separately.</p>',
'These are generated sample sizes, not selected yields or a claim of production completeness.',link('Projects/HToWW/talks/2026-11-12-central-sample-inventory.md','Exact datasets, counts and DAS queries'),
'Direct DAS summary census22:02CET,no failed queries. Current exact configured versions only;46perera. OtherHiggs16includesWHWW,WHtau,ggH,VBF,ZH,ggZH,ttHcomponents. Countoneentryperdataset;allselectedbeforecuts. CentralH+c counts1.010M,1.013M,1.005M,.922M. H+b1.006M,2.432M,1.863M,.898M. No model training or jobs run.',layout='inventory-slide')
import collections
inv24=collections.defaultdict(list)
for r in inventory['available2024']:
 g=r['display_group']
 if g in ['ggH','VBF','ZH','WH','ttH']:g='Higgs backgrounds'
 if g=='Wgamma':g='Wγ'
 inv24[g].append(r)
rows24=[]
for group in ['tt','Single top','DY','W+jets','Diboson','Wγ','Higgs backgrounds']:
 rs=inv24[group];rows24.append([group,str(len(rs)),f"{sum(r['nevents'] for r in rs)/1e6:,.1f}M"])
rows24.append(['H+c /H+b','No matching NanoAOD','GEN/request status not inferred'])
add('central-2024','2024: central background samples are available','Relevant SM options · standard NanoAOD · latest versions, including extensions',
col(table(['Family','Datasets','Produced events'],rows24,'inventory-table'),
'<h3>Different from the2022/23 fileset</h3>'+bullets('Names changed: DY is split by lepton flavour; W+jets has pT-binned alternatives.','Higgs and ttH primaries were renamed; exact old-name searches miss them.','Alternative generators, binnings and decays can overlap. This is an availability inventory, not a fileset to sum blindly.')+'<p class="small">No matching2024H+c/H+b NanoAOD found in the queried name families. This does not prove absence of an earlier production tier.</p>',ratio='1.2fr 1fr'),
'Extending the analysis to2024 requires sample selection, calibrations and signal-production follow-up.',link('Projects/HToWW/talks/2026-11-12-central-sample-inventory.md','DAS census, selection rules and full dataset list'),
'Broader DAS discovery22:05CET corrects missing2024samplesfromliteral2022primaryqueries. Exact rawqueries/results preserved; selected73datasetoptions. StandardNanoAODv15preferredperprimary,latestprocessingandextretained;excludeBTV/JME/FastSim. NLODYunbinnedE/Mu/Tau10–50,>50;W14pTbins/options,HiggsSMWW/tauandttHchoices. ttHnonbb and individualdecays mayoverlap:do not combineall. Single-top tchannel exactmatch gaps remain. This is not all CMSDAS and not a2024processingclaim.',layout='inventory-slide')
add('historical-result','October reference: four eras, expected μ < 691','Blind Asimov · expected 95% CL · pre-fix four-era model',
col(fig('oct_limits.png','Expected limits with ±1σ/±2σ bands; stat-only and MC-stat-frozen references.'),
'<h3>Run 3 · 61.9 fb⁻¹</h3>'+table(['Fit configuration','Expected μ₉₅'],[['Full model','691'],['Freeze autoMCStats','616'],['Stat-only','338.5']])+'<p>2022: <b>905</b><br>2023: <b>1077</b></p><p class="small">Rough √L scaling to138 fb⁻¹ gives463, versus the published Run2 expected506. Different analyses and pre-fix inputs: not a controlled improvement measurement.</p>',ratio='1.8fr .8fr'),
'This is a dated reference; the corrected A/B results are separate.',refs(('old','7 October results'),('plots','Original Combine plots')),
'Historical card: partial signal scale correction, NLO signal normalization, flat30% scheme term, no-op JER and missing WH contributions. All numbers are expected, not observed. L-label62 on original plot is rounded61.9. The 691→338.5 difference is not a quadrature uncertainty decomposition.',layout='plot-slide wide-plot')
add('higgs-scale','Higgs-background scale treatment: 691 → 703','Old-card diagnostic · preserve channel migration; remove the inclusive scale rate',
col(table(['Variant','Scale-template treatment','Expected μ₉₅'],[['V0','Historical card','691'],['V1','Higgs background: shape-only','703'],['V2','Also st, diboson and V+jets: shape-only','691']]),
'<h3>What changes?</h3>'+bullets('Normalize each scale variation to the nominal sum across the six channels of each era.','Retain the separate cross-section rate nuisance. Signal keeps rate + shape; tt has no scale template.')+'<p class="small">V1: +1.7% in the median. V2 returns to691 at the reported precision; this does not establish a preferred prescription.</p>',ratio='1.3fr 1fr'),
'The treatment matters; do not import a sensitivity gain from the HZZ analysis.',refs(('audit','V1/V2 logs and construction'),('evening','Original diagnostic request')),
'Directly read V1.limit.log and V2.limit.log from ~/htoww_submit_logs/higgs_scale_20261112. Combine10.6 AsymptoticLimits CLs:V1 median703,16/84%=469.0242/1106.5151;V2 median691,16/84%=461.0181/1093.1359. Build logs show nontrivial rescalings, diboson unchanged. These are tests on the historical card, not corrected A/B limits.')
add('signal-samples','Central signal samples: two independent production issues','Running-Yukawa variation weights and the FxFx forward-parton veto',
col(fig('signal_weights.png','Scale variations ≈×2; PDF-replica mean/member0 ≈2.26 rather than1.'),fig('signal_merging.png','The central WW fragment restricts the FxFx veto to|η|<2.5.')),
'Variation weights can be repaired per event; the merging defect requires regenerated samples.',refs(('old','13 October diagnosis'),('grid','Existing GEN validation deck')),
'Nominal samples remain usable provisionally. Yukawa patch is applied in Fortran but omitted by Python systematics. FxFx settings:etaJetMax999 and coneRadius1 absent; default2.5/.7. Forward1jet fraction≈.98% central versus6.6–6.8% clean. Corrected H+c/H+b gridpacks sent. GEN reproduction pending.',layout='plot-slide')
add('gridpack-validation','Corrected gridpack: checks against the clean reference','H+c 4FS · LHE+GEN validation · corrected fragment',
col(fig('gridpack_higgs_pt.png','Higgs pT: rebuilt el8 gridpack vs official clean reference.'),
'<h3>Independent generation, consistent outputs</h3>'+table(['Quantity','Rebuilt','Reference'],[['Matched σ [fb]','97.4 ± 1.6','96.5 ± 1.6'],['PDF/member 0','0.999','0.999'],['Negative-weight fraction','0.217','0.216'],['μR×2 ratio','0.966','0.967']])+'<p class="small">≈10k matched events per sample; all nine scale points agree within 0.7%. These are generator-validation cross sections, not the NNLO analysis normalization.</p>',ratio='1.15fr 1fr'),
'Corrected H+c/H+b gridpacks are sent; full detector-level reproduction is still ahead.',refs(('grid','4FS r3 validation'),('plan','Latest send status')),
'H+c numbers from existing validation slides:10370 vs10296 matched events, Higgs-pT χ²/ndf1.4/10. Do not transfer the H+c numerical validation to H+b. Three-flavour validation is in backup.',layout='plot-slide')
add('gridpack-handoff','Corrected gridpacks sent to Sebastiano','GEN follow-up · sent 12 November',
'<h3>Three parts of the production package</h3>'+table(['Sample','Validation and material','Follow-up'],[['H+c4FS FxFx','Rebuilt gridpack + corrected fragment; LHE/GEN checks against cleanγγ reference','Corrected gridpack sent'],['H+b5FS FxFx','Same weight/fragment issue identified; corrected gridpack sent with validation follow-up','Do not transfer H+c numerical checks to H+b'],['H+c3FS','Official-gridpack/private-WW validation; decay and era comparisons; re-NANO PDF weights','Validation slides available']])+'<p>Issues reported to Sebastiano; he said he can try reproduction with increased priority. The per-event workaround allows the analysis to proceed while corrected samples are produced.</p>',
'Gridpack handover is complete; central reproduction is a separate step.',refs(('plan','Send status'),('grid','4FS validation slides')),
'Corrected H+c and H+b gridpacks have been sent; 3FS validation slides exist. Sebastiano can try the reproduction with increased priority. Do not imply acknowledgement, new production completion or CMS approval.')
add('arms','Flavour scheme: baseline A, cross-check B','4FS: massless charm in the proton · 3FS: massive charm produced in the hard process',
col('<div class="arm-title">A <span>Ratio method</span></div><h3>Keep central 4FS signal</h3>'+bullets('Use the leading GEN c-hadron pT ratio to make a 3FS-like shape.','Up = 3FS-like; Down = 2 − Up.','This shape treatment replaces the historical flat 30% rate uncertainty.'),
'<div class="arm-title orange">B <span>Stitching method</span></div><h3>Join complementary GEN regions</h3><div class="partition"><div>4FS<br><b>N<sub>c-jet</sub> = 0</b></div><div>3FS<br><b>N<sub>c-jet</sub> ≥ 1</b></div></div><p class="small">GEN c jets: pT &gt;10 GeV, |η|&lt;2.5, R=0.4. Per-era generated-weight normalization. A’s separate scheme nuisance is off in B.</p>'),
'Proposed: A as the nominal signal model; B cross-checks the flavour-scheme treatment with the same NNLO rate.',refs(('route','Stitching implementation'),('state','Ratio-method prescription')),
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
add('negrw-limits','Closure: good overall, residual shape in some samples','Rates restored per sample; the ensemble nuisance absorbs part of the shape residual',
col(fig('09_shape_renorm_lhe_vpt_njets_ge1_DYto2L_2Jets_50.png','DY mass&gt;50, Njet≥1: residual shape after sample-yield renormalization.'),
'<h3>What the checks show</h3>'+table(['Held-out closure','v2'],[['All samples','0.9984'],['DY 10–50','0.8980'],['W+0J','0.9855']])+'<p>Per-era/sample renormalization restores the rates; some shape residual remains.</p><div class="result"><div class="rval">χ²/ndf = 47.2/20</div><div class="rlab">DY shape example; 35.0/20 with the nuisance</div></div>',ratio='1.2fr 0.9fr'),
'Overall closure is within 0.2%; the remaining sample-level shape differences are partly covered by the negrw nuisance.',refs(('negrw','Corrected G1/G2'),('nreview','Acceptance review')),
'This is a limitation in both v2 and July; July shape χ²47.9/20 for the shown diagnostic. The band is ensemble spread, not an independently validated envelope of all method biases.',layout='plot-slide')
add('syst-overview','Systematics: implementation and physics scope','Detector calibration, generator modelling, rate terms and finite MC',
col('<h3>Detector / object response</h3>'+bullets('Lepton efficiencies and momentum/energy shifts.','Total JES, JER and soft/unclustered MET shifts.','Pileup and luminosity; c-tag SFs remain provisional.'),'<h3>Generator / fit model</h3>'+bullets('ISR/FSR, μR/μF and PDF variations; process scope matters.','Top-pT and Higgs+heavy-flavour modelling.','Flavour scheme, negrw ensemble and autoMCStats.'))+'<div class="context"><b>Still open:</b> H+c αS rate, component-aware Higgs rate/BR terms, final empty-template policy. hDamp will be implemented.</div>',
'Configured sources are not yet measured impacts in the new A/B fit.',refs(('syst','Current inventory'),('alpha','Signal αS provenance')),
'Full explanations and implementation/evidence status for every source are in backup. tt is excluded from configured scalevar/ps rows, not automatically from all theory-named nuisances. Trigger SFs remain disabled by decision; not a measured zero.')
add('speed','Framework optimization: remove repeated work','Measured component improvements; separate storage and timing claims',
col('<h3>Redundant event storage</h3>'+metric('2,858 MB → 18.9 MB','Same historical tt partition','Legacy output vs nominal TRAIN output')+'<p>≈150× smaller for these different output contents: repeated shifts, weight columns and precision dominate.</p>',
'<h3>Controlled timing benchmark</h3>'+metric('46.5 s → 31.1 s','One H+c chunk','85,732 events; −33% wall time')+'<p>NumPy parquet writer, cached YAML and correction sets. Seeded outputs match byte-for-byte.</p>')+'<p class="context">Production median 18 min, p90 50 min; 11% failed in the recorded grid snapshot. Retries and input access dominated campaign wall time.</p>',
'These are measured comparisons, not a claimed 150× runtime speedup.',refs(('frame','Storage comparison and agreed framing'),('speed','One-file timing'),('plan','Production snapshot')),
'Legacy stores nominal+15 shifts and all53weight columns; TRAIN is nominal-only. The proposed combined writer will store more than TRAIN: its size/runtime have not been measured. 16/16 and64/64parquet equality checks refer to the controlled optimization test.')
add('framework-flow','A compact event record for offline iteration','Problems found → solutions implemented → combined workflow',
'<div class="problem-flow">'+table(['Problem','Solution'],[['Weight columns repeated in shifted tables','Keep weight variations in nominal; shifts carry only needed quantities'],['Unused columns and excess precision','Compact columns and suitable precision; preserve event IDs'],['Histogram-only outputs tie iteration to NanoAOD','Retain event inputs for offline training, scoring and rebinning'],['Missing inputs or stale model outputs','Coverage, provenance and model-compatibility guards']])+'</div><div class="workflow"><div>One NanoAOD<br>pass</div><span>→</span><div>Compact nominal<br>+ shifted inputs</div><span>→</span><div>Offline MVA<br>+ templates</div><span>→</span><div>Combine</div></div>',
'The core components are implemented; a bit of refactoring remains to bring them together.',refs(('frame','Presentation framing'),('scorer','Offline scorer now implemented')),
'Intended combined single-pass workflow, not claimed complete. The new model cannot be used before it is trained: store event inputs first, then score offline. The exact user wording is “a bit of refactoring”; this is his presentation preference, not an engineering-effort estimate. Automatic Condor retries/global redirector remain planned.',layout='flow-slide')
add('mva','Event classifier: five held-out models per arm','One validation owner; every fitted event has an out-of-training score',
'<div class="workflow folds"><div>event % 5<br>test fold i</div><span>↘</span><div>Model i<br>trained on other folds</div><span>→</span><div>Score fold i<br>once in the fit</div></div>'+col('<h3>b-hive owns validation</h3>'+bullets('Training list split 85/15 internally; seed 20261112.','Roughly 68% training, 12% validation, 20% held out, by constructed files.'),'<h3>Physics recipe kept explicit</h3>'+bullets('Six classes, 26 features; 30 epochs, batch 1024, learning rate 10⁻³.','Class weights only; event-weight columns do not enter the loss.')),
'Every event contributes once, using a model that held it out of training.',refs(('dup','Training readiness and seed'),('plan','A/B strategy')),
'Features:14kinematic+11c-tagonehot+nSV. Cached constructed datasets use unique fold/split identities. RUN/registration guard feature/selection hashes, class order and provenance. Same test fold remains assigned for object-shifted copies.')
add('mvacheck','Backup: validation duplication and model selection','Found, reproduced and corrected before the new training',
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
add('open','Proposed baseline and path to the result','What we ask the conveners to agree, and what remains after that',
col('<h3>Proposed baseline</h3>'+bullets('<b>Arm A</b>: all central samples, with the per-event scale-variation fix.','Arm B (3FS/4FS stitching) as a cross-check of the flavour-scheme treatment.')+'<h3>Agreement requested</h3>'+bullets('Per-event scale workaround for the existing samples.','FxFx forward-merging treatment while corrected samples are reproduced.','A as nominal, B as cross-check, with the caveats shown.'),
'<h3>Remaining steps</h3>'+bullets('<b>Production:</b> train and score Arm A in all four eras; cards and full-systematics two-SR fit.','<b>Inputs we will ask for:</b> a sourced H+c αS rate; H+b PDF+αS and its overlap with the 5% Higgs rate.','<b>Expected:</b> c-tag calibration update.','<b>We implement:</b> hDamp; decay-component scope of the Higgs BR terms; ttH→ττ coverage check.','Then: AN update and the approval steps.')),
'With these prescriptions agreed, no further method development is needed; the remaining steps are production and the listed inputs.',refs(('plan','Convener questions'),('syst','Open-input inventory'),('scorer','Result dependency')),
'No corrected limit exists yet: Arm A training and scoring are in production. c-tag update comes from Livio. H+c alphaS rate and H+b PDF+alphaS overlap are questions to the theory/sample contacts. BR terms: the 1% BR(WW) and BR(tautau) currently act on the whole merged Higgs background; we scale them to the decay components. ttH: our ttHnonBB group is exclusive cc, gamma-gamma, Z-gamma, so tau-tau coverage must be checked without double counting an inclusive sample. hDamp will be implemented. Do not present this as a result or as approval readiness.')
add('oct-impacts','What drives the October fit?','Historical pre-fix card · Asimov r = 1 · no new A/B impact claim',
col(fig('oct_impacts.png','Top30 of55 saved nuisance impacts; MC-bin nuisances excluded from this ranking.'),
'<h3>Freeze-group diagnostic</h3>'+table(['Group','Quadrature fraction'],[['Scale / PDF / PS','46.1%'],['MC statistics','44.9%'],['Leptons incl. scale/res','26.0%'],['c-tagging','23.5%']])+'<p class="small">Fractions are √(σ²−σ²_frozen)/σ, not additive shares. The group freeze and individual impacts answer different questions.</p><p class="small">The leading scale nuisances act on non-tt processes. Four tt rate parameters also rank highly.</p>',ratio='1.2fr 1fr'),
'Systematic treatment and finite MC statistics both matter in the reference fit.',refs(('plots','9 October impact plot'),('breakdown','21 October group-freeze study')),
'Nominal σ(r)=299.8; freeze groups one at a time. Do not compare these numerical fractions directly to Run2 table conventions. Card read confirms scalevar rows are dash for every tt entry. One electron-reco impact tree unreadable in saved report. The JER group understates actual uncertainty because old JER was a no-op.',layout='plot-slide tall-plot')
impact_rows=json.loads((D/'impact-values.json').read_text())['rows'][:8]
add('oct-impact-table','October fit: leading individual nuisance impacts','Asimov r = 1 · Δr after fixing one nuisance at its fitted ±1σ',
table(['Nuisance','Fitted value','Fitted −/+ error','Δr at −1σ','Δr at +1σ'],[[r['p'].replace('_',' '),f"{r['val']:.3f}",f"{r['lo']:.3f} / +{r['hi']:.3f}",f"{r['dlo']:+.1f}",f"{r['dhi']:+.1f}"] for r in impact_rows],'impact-table')+'<p class="small">MC-bin parameters excluded. Entries are shifts in fitted r, not changes in the 95% CL limit.</p>',
'The table quantifies the same historical fit shown in the impact plot.',refs(('plots','Saved impacts_run3.json'),('audit','Exact values and fit conventions')),
'Directly read JSON fromOctober9plot folder:55nuisances,failed electron reconstruction entry listed separately. rate_tt values are scale factors with absolute errors, not Gaussian pulls. Other nuisance values/errors are in standard nuisance coordinates. Δr signed according to fixed nuisance down/up, so effects can reverse. No new fit run. Do not relabel as expected-limit impacts or r=0/median expected set.',layout='impact-slide')
add('oct-scan','October card: likelihood scan in μ','Blind Asimov μ = 1 · four eras, 61.9 fb⁻¹ · all uncertainties vs statistical only',
col(fig('oct_scan.png','Profile likelihood scan; statistical-only curve freezes all constrained nuisances.'),
'<h3>Read from the scan</h3>'+table(['','68% CL','95% CL'],[['All uncertainties','−294 … +309','−637 … +693'],['Statistical only','−168 … +171','−332 … +339']])+bullets('σ(μ) ≈ 300 total vs ≈ 170 statistical-only.','The 95% CL crossing (+693) matches the CLs expected limit μ < 691.'),ratio='1.35fr 1fr'),
'Systematics widen the October interval by about 1.8× relative to statistics alone.',link('breakdown','Group-freeze study')+' · <a href="#/run2-compare">Run 2 comparison →</a>',
'New fit, 13 Nov: MultiDimFit grid, 41 points, r in [-1000,1000], Asimov r=1, on the unchanged October workspace (pre-fix: old global LHE fix, JER no-op, provisional c-tag). Stat-only scan freezes allConstrainedNuisances from the total-fit snapshot. A −2ΔlnL=3.84 crossing is a likelihood interval, not CLs; its agreement with 691 is a consistency check. Not the corrected A/B result. Outputs: lxplus ~/htoww_submit_logs/scan_oct691_20261113/.',layout='plot-slide')
add('run2-compare','Uncertainty shares: our October card vs Run 2','Freeze one group at a time · Run 2: HIG-24-009 Table 3 (1POI, 138 fb⁻¹) · ours: pre-fix four-era card (61.9 fb⁻¹)',
col(fig('run2_vs_run3_impacts.png','Impact on σ(μ) when each group is frozen. Orange solid and outline: our two conventions.'),
'<h3>Same leading term</h3>'+bullets('Data statistics: 60% (Run 2) vs 57%.')+'<h3>Larger in our card</h3>'+bullets('MC statistics 45% vs 6%; scale/PDF/PS 46%.','c-tag, leptons, JES/JER: 17–26% vs 5–6%.')+'<h3>Smaller in our card</h3>'+bullets('Higgs background 7% vs 21%.')+'<p class="small">Compare rankings, not exact sizes.</p>',ratio='1.9fr 1fr'),
'Like Run 2 we are limited by data statistics; MC statistics and the signal-variation treatment are our largest reducible terms.',link('breakdown','21 October group-freeze study')+' · <a href="obsidian://open?vault=obsidian-notes&amp;file=References%2FHToWW">HIG-24-009 Table 3</a> · <a href="#/oct-impacts">← October impacts</a>',
'Our values: blind Asimov r=1 on the pre-fix October card, nominal σ(r)=299.8, MultiDimFit singles with one group frozen at a time. Quad = sqrt(σ²−σ²_frozen)/σ, lin = (σ−σ_frozen)/σ; Run 2 caption says change of 1σ when fixed, but its rows are not additive in either convention. Caveats: our scale/PDF/PS includes the signal scalevar biased by the old global LHE fix; JES/JER understated because JER was a no-op in these cards; c-tag 23.5 consistent with the flagged 2022 Up (+43% SR signal); luminosity differs 138 vs 61.9 fb⁻¹ so statistical share is not like for like. Not the corrected A/B fit.',layout='plot-slide tall-plot')
add('oct-datamc','Data/MC: broad bands hid a visible shape trend','2022postEE · October production, before the correction campaign',
col(fig('oct_datamc_met.png','Missing transverse momentum: data/MC falls from about1.0 to0.83 in the tail.'),fig('oct_datamc_mtll.png','Dilepton transverse mass shows a similar trend.')),
'The broad band is not evidence that the central modelling is satisfactory.',refs(('old','5–6 October investigation'),('plots','Original pre-fix plots')),
'These are actual data over MC, not blind Asimov shapes. Signal drawn scaled×10000 as labelled by original plot. Large plotting band includes MC statistics and weight variations; does not include object shifts or lnN rates. Observed postEE total ratio0.923 in original band study. New-production closure has not been established here.',layout='plot-slide tall-plot')
add('oct-band','Where the large uncertainty band came from','All four eras · decomposition of the historical plotter band',
fig('oct_band.png','Variance shares and mean band half-width; right panel estimates removal of the tt scale contribution.')+'<p class="small">tt μR/μF: <b>54–72%</b> of variance; c-tag SF: <b>15–38%</b>; PDF/αS: <b>7–9%</b>. The fit excludes tt scale templates, but the plotter included them.</p>',
'A data/MC plot band and the fit uncertainty must use a consistent prescription.',refs(('plots','All-era band decomposition'),('audit','Direct script and datacard check')),
'Checked band_breakdown.py: MC stat plus all stored weight variations, no object shifts and no lnN rates. Direct v12 combined-card inspection: scalevar_muR,muF,muR_muF are absent on tt. Free rate_tt alone would not justify dropping shape uncertainty; exclusion is the actual historical card prescription. Right-hand estimate assumes scale contribution is tt-dominated, not a fresh full band recomputation.',layout='plot-slide panorama')
add('oct-slope','The MET-slope study exposed inconsistent variations','2022postEE · shape-normalized ratios · all curves from pre-fix outputs',
col(fig('oct_slope.png','Top: correction variations. Bottom: E/F/G run periods against the same MC.'),
'<h3>What the comparisons told us</h3>'+bullets('E/F/G share the trend: not isolated to one run period.','Jet-veto map and pileup changes do not remove the trend.','JER Up = Down = top-pT off exactly: a software inconsistency, not a physical response.')+'<p class="small">JES Down looked better, but the MET-propagation sign was wrong. That apparent improvement cannot identify the cause.</p>',ratio='1.2fr 1fr'),
'The study found real correction bugs; it did not establish that the old slope is resolved.',refs(('old','Slope study and correction audit'),('audit','Original summary.json')),
'Original MET χ² values:nominal418.7,top-pT off497.1,JERUp/Down497.1,JESDown183.1. Separate band-breakdown shape fit309/19 uses different binning/selection, so do not mix χ²s. Source is runall/slope_study.py. July stored-PuppiMET output already had a slope, ruling out the October Type1 bug as its sole cause.',layout='plot-slide')
add('oct-corrections','What the data/MC investigation changed','Measured failures → correction or follow-up in the new production',
table(['Finding','Evidence in the old production','Action'],[
['preEE data overlap','2243 extra rows /37373; ratio1.009→0.948 after removal','Correct primary-dataset trigger exclusivity'],
['Missing c-tag MVA inputs','All11 one-hot inputs absent; tt SR fraction16.8→16.0% when restored','Build categories; fail on missing features'],
['JER + top-pT in shifts','JER Up=Down; shifted tt lost nominal top-pT','Read split JER uncertainty; retain top-pT'],
['Type1 MET propagation','Wrong reference/sign; JES moved jets and MET together','Re-correct stored MET with NanoAOD jet reference'],
['Electron / WH templates','Resolution keys nominal-only; two WH rates zero','Correct variation keys and normalization']],'audit-table'),
'After removing duplicates, preEE also slopes: the earlier “postEE-only” diagnosis was overturned.',refs(('review','6 October independent audit'),('old','Correction smoke-test record'),('state','Later implementation handoff')),
'Dedup after removal MET ratio1.00→0.89; postEE1.00→0.83. Matching used(event,round(lepton1_pt)), not a complete modern run/lumi/event duplicate scan. The historical review was not independently repeated; new corrections have bounded tests, not a new all-era data/MC closure measurement. Old Asimov limit does not use data, so data duplicates alone did not change it.')
add('yukawa-check','Per-event scale repair: check the selected phase space','≥1 GEN c-jet · pT>20 GeV · |η|<2.4 · 13 October study',
col(fig('yukawa_acceptance.png','Acceptance response under scale variations: repaired WW versus two clean references.'),
'<h3>Beyond a common factor</h3>'+bullets('Invert the PDF-replica mean to infer each event’s Yukawa scale.','Restore the running factor separately for every μR variation.','In the analysis-like region: shapes agree at about1–2%; acceptance differences are about1percentage point.')+'<p class="small">Nominal acceptance:29.3% ours,29.7% clean γγ,28.5% Run2 WW. Different energies; this is a diagnostic comparison.</p>',ratio='1.4fr 1fr'),
'The repair addresses variation weights; it cannot regenerate events missing from FxFx merging.',refs(('audit','13 October investigation and original plot'),('old','High-stat and analysis-region checks')),
'GEN-region proxy, not full reconstructed analysis selection. Single-scale events match patch<0.1%; real/counterterm two-scale treatment has≈1% residual. Inclusive reference discrepancies were traced to event-class mix and MG1GeV scale-floor events. H+b follow-up validation is separately recorded, not inferred from H+c.',layout='plot-slide')
add('fs-validation','Ratio-method validation: era consistency and decay transfer','Official samples · equal inclusive cross section · September/October study',
col(fig('fs_eras.png','Four Run3 γγ eras: all six era-pair χ²/ndf are6.2–10.0/10.'),fig('fs_decay.png','Run2 WW versus γγ: transfer checked with statistical bands.')),
'The ratio changes the flavour-scheme shape; the NNLO rate is a separate input.',refs(('fs','Derivation, sample counts and checks')),
'Derived on official Run3γγ; no private exploratory γγ samples used. c-hadron threshold5GeV,|η|<2.5. Run2 WW/γγ χ²18.9/10,9of10bins within1–2σ. The20–30GeV outlier was examined per-file and with Run3γγ; consistent with a Run2γγ fluctuation, not established decay dependence. Run3 weights1.052 vsWW1.048 in that bin.',layout='plot-slide')
add('fs-reco','Does the ratio cover a real 3FS H→WW sample?','Run2 UL18 · standalone reconstructed selection · equal inclusive normalization',
col(fig('fs_sr.png','Leading c-tagged-jet pT: true3FS versus4FS and its scheme variation.'),
'<h3>SR yield, relative to4FS</h3>'+table(['Input','Yield ratio'],[['Real3FS','1.063 ±0.023'],['4FS ×Run3 γγ ratio','1.073'],['4FS ×WW-derived ratio','1.079']])+'<p>The ±7.3% variation covers the measured +6.3±2.3% shift.</p><p class="small">Partial compensation:preselection differs by4%, while the reweighting gives a larger c-tag gain. Jet multiplicity remains an uncovered difference.</p>',ratio='1.2fr 1fr'),
'Useful closure at the yield level, with a specific limitation to test in the fit.',refs(('fs','Reco validation and caveat')),
'Not the current Run3 MVA selection:standalone OS eμ with tightμ/WP80e,20/10GeV,mll12–72,mT cuts,DeepJetmediumUL18 stand-in. Real3FS SR yield versus4FS +6.3±2.3%,variation+7.3%. Njets χ²23/5 not covered;2jet3FS/4FS≈0.82. Historical “no3FSWW inRun3” reason to avoid stitching is now obsolete:private3FS and re-NANO exist.',layout='plot-slide')
add('backup-fs-njet','Backup: the ratio does not cover jet multiplicity','Run2 standalone WW SR · a remaining limitation, not a new Run3 result',
col(fig('fs_njet.png','Njets(pT>30GeV): real3FS differs from4FS; scheme weight barely moves it.'),
'<h3>What remains to check</h3>'+table(['Njets','3FS /4FS'],[['0','1.09'],['1','0.95'],['2','0.82'],['3','≈0.8']])+'<p>χ²=23/5. The c-hadron ratio changes Njets by only about±1%.</p><p class="small">Merged4FS versus unmerged3FS is part of this difference. The current A/B comparison must test its relevance to the final classifier and fit.</p>'),
'Yield closure does not imply closure of every discriminating variable.',refs(('fs','Standalone reco study'))+' · <a href="#/fs-reco">← main</a>',backup=True,layout='plot-slide')
add('backup-prefit','Backup: October MVA templates before the fit','2022postEE · six argmax channels · blind Asimov model',
fig('oct_prefit.png','FitDiagnostics prefit shapes; no real data points because data_obs is the background sum.')+'<p>The model uses the winning-class score in each region. CRs constrain shared backgrounds; they are not discarded.</p>',
'These templates belong to the historical691 card, not the newly trained models.',refs(('plots','Original prefit outputs'))+' · <a href="#/historical-result">← main</a>',backup=True,layout='plot-slide panorama')
# Backup starts only after the main conclusions. Every page links back to its main context.
slides.append({'id':'backup','title':'Backup','backup':True,'html':f'''<section class="slide divider" id="backup" data-n="{len(slides)+1}" data-backup="true"><div class="line"></div><h1>Backup</h1><p class="divsub">Systematic prescriptions · validation plots · production provenance</p><p class="backup-home"><a href="#/open">← Main conclusions</a></p></section>'''})
add('definitions','Backup: definitions and fit conventions','Reference terms; implementation details live in the companion notes',
table(['Term','Meaning'],[['Arm A / Arm B','Central 4FS with scheme-shape uncertainty / stitched 3FS+4FS signal'],['TRAIN / RUN','Nominal feature-event output / inline-scored systematic templates'],['SR / CR','Signal region / control region selected by classifier argmax'],['negrw g(x)','Generator-level signed-weight cancellation estimate, 2P(positive|x)−1'],['lnN / shape / rateParam','Rate uncertainty / varied template / fitted normalization'],['autoMCStats','Finite MC-bin statistics from signed-weight variance, not a flat 10%'],['Current iteration / final fit','Merged SR from present TRAIN schema / intended two c-jet-count SRs']]),
'Keep the statistical model and the saved-output schema attached to every result.',refs(('syst','Inventory'),('scorer','TRAIN-to-card conventions')),backup=True)
theory_citations={
'backup-syst-theory': ('<a href="obsidian://open?vault=obsidian-notes&amp;file=References%2FHToWW%2FAN-23-102.pdf">AN-23-102§7.1/Table16</a> · <a href="https://arxiv.org/abs/2608.26863">LHCHWG-2026-007§4.3,AppB</a>', 'ISR/FSR,top-pT and HF prescriptions follow the analysis sources, not universal uncertainty sizes. AN-23-102§7.1/Table16 sources50%ggH+HF; extension toVBF is an analysis choice requiring review. LHE×2/.5 scales are generator variations; three independent directions and shared correlation are current analysis choices, not the paper seven-point-envelope prescription.'),
'backup-syst-pdf': ('<a href="https://arxiv.org/abs/1510.03865">PDF4LHC15§6.2</a> · <a href="https://arxiv.org/abs/2203.05506">PDF4LHC21§6.3.3</a> · <a href="https://arxiv.org/abs/2510.18815">LHCHWG-2025-011Table1</a>', 'PDF/alphaS method:PDF4LHC15eq26–28 or21eq6.6–6.8 with differentalphaSsteps,not interchanged. H+c7.43±.14% is our own clean4FS gridpack Hessian calculation,10370events,not a percentage fromthepaper. H+b+3.36/−3.44 is an interpolation ofLHCHWG2025-011Table1 at125.09,not yet installed. H+c alphaS process-specific number remainsmissing.'),
'backup-syst-scheme': ('<a href="https://arxiv.org/abs/2608.26863">LHCHWG-2026-007§4.4/5.3</a> · <a href="https://arxiv.org/abs/2510.16217">negrw method:arXiv2510.16217</a> · '+link('fs','Our ratio validation'), 'Paper motivates flavour-scheme comparison andstitching; c-hadron shape ratio and mirroredDownare our analysis construction with official-sample checks. negrw ensemble spread is an implemented method uncertainty,not a paper-supplied universalcoverage guarantee.'),
'backup-syst-rates': ('<a href="obsidian://open?vault=obsidian-notes&amp;file=References%2FHToWW%2FAN-23-102.pdf">AN-23-102§7.1/Table16</a> · <a href="https://arxiv.org/abs/1610.07922">YR4 Higgs rates/BR</a> · '+link('syst','Current implementation'), 'Single-top−1.27/+1.67%,diboson3.7%,Vjets2.7%,Higgs5%are inheritedANprescriptions;not newlycalculated2024orRun3theoryerrors. BR1%iscurrentconfiguredprescription;merged-backgroundscopeisbroaderthandecaycomponents. rate_tt andautoMCStats are fit/statisticalmodelchoices,not externaltheory uncertainties.')}
for sid,item in json.loads((D/'systematics.json').read_text()).items():
 rows=[];details=[]
 for r in item['rows']:
  rows.append([r['name'],r['effect'],r['construction']+'<br><span class="check">'+r['evidence']+'</span>'])
  details.append(r['nuisance'])
 add(sid,item['title'],'Systematic walkthrough · physical origin, implementation and checks',table(['Source','Physical effect / why it matters','Variation, scope and check'],rows,'systematics')+('<div class="syst-example"><b>How it enters the fit:</b> luminosity multiplies the yield coherently within a year. Pileup instead changes each event’s weight, so its Up/Down templates can change both yield and shape.</div>' if sid=='backup-syst-norm' else ''),
 'New template effects and fit impacts remain to be checked after scoring.',item['source']+(' · '+theory_citations[sid][0] if sid in theory_citations else '')+' · <a href="#/syst-overview">← systematics overview</a>',
 theory_citations.get(sid,('', ''))[1]+' Implementation nuisance names: '+', '.join(details)+'. See the source inventory for exact dispatch/configuration. These are implemented/source-inspected prescriptions, not fresh all-era validation plots.',backup=True,layout='systematics-slide')
add('hdamp','Backup: hDamp probes tt matching','To be implemented after MVA training',
col('<h3>Physical uncertainty</h3>'+bullets('POWHEG h_damp controls the damping of hard real emission relative to shower matching.','Changes extra-jet activity and can migrate tt events between c-jet categories.','ISR/FSR shower weights do not automatically cover this matching variation.'),'<h3>Implementation still pending</h3>'+bullets('Dedicated Hdamp158/418 tt samples configured in all four eras.','Normalize each alternative using its own full generated sumw.','Need acceptance, shape and MC-stat checks before adding the template nuisance.')),
'Configured samples are not an implemented or validated alternative-sample nuisance.',refs(('prod','Deferred hDamp scope'),('syst','Current inventory'))+' · <a href="#/syst-overview">← main</a>',backup=True)
add('backup-negrw-sr','Backup: negrw in the selected eμ signal region','17,627 events · corrected v2 report',
col(fig('07_sr_vpt.png','SR V-pT distributions: original signed weights, v2 and July.'),fig('09_shape_renorm_lhe_vpt_all_WtoLNu_2Jets_1J.png','W+1J: shape residual after per-sample renormalization.')),
'v2 and July agree in the SR; both share the same residual W+1J shape.',refs(('negrw','Corrected statistics'))+' · <a href="#/negrw-limits">← main</a>',
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
# Small changes belong at the end, with their Git evidence and current status.
minor_ids=[]
for sid,title,items in json.loads((D/'minor-updates.json').read_text()):
 minor_ids.append(sid)
 rows=[[subject,detail+'<br><span class="commit-ref">'+commits+'</span>',status] for subject,detail,commits,status in items]
 add(sid,title,'Appendix · September1–November12 · consolidated Git history, not additional fit results',table(['Update','What changed / evidence commits','Status'],rows,'minor-table'),
 'Recorded implementation is distinct from all-era physics validation.',refs(('audit','Complete content and commit ledger'))+' · <a href="#/open">← main conclusions</a>',
 'Small changes consolidated from vault Git history. Commit IDs record the note or handoff, not necessarily the analysis-code commit. Superseded operational counts and temporary queue failures are omitted. Scope/status is stated per row.',backup=True,layout='minor-slide')
# Revision3: select physics results for the main story, keep engineering detail in backup.
main_ids=['title','analysis','progress','central-inventory','central-2024','historical-result','higgs-scale','oct-impacts','oct-impact-table','oct-scan','run2-compare','oct-datamc','oct-band','oct-slope','oct-corrections','signal-samples','yukawa-check','gridpack-validation','gridpack-handoff','arms','fs-validation','fs-reco','samples','leptonmva','negrw','negrw-limits','syst-overview','speed','framework-flow','mva','open']
systematic_ids=list(json.loads((D/'systematics.json').read_text()))
pos=main_ids.index('syst-overview')+1
main_ids[pos:pos]=systematic_ids
byid={s['id']:s for s in slides}
# Production queues, scorer tests and validation mechanics are not the main physics story.
extras=['mvacheck']
back_ids=['backup','backup-fs-njet','backup-prefit']+extras+[s['id'] for s in slides if s['backup'] and s['id'] not in ['backup','backup-fs-njet','backup-prefit','backup-production'] and s['id'] not in minor_ids and s['id'] not in main_ids]+minor_ids
slides=[byid[k] for k in main_ids+back_ids]
for i,s in enumerate(slides,1):
 import re
 s['backup']=s['id'] not in main_ids
 s['html']=re.sub(r'data-n="\d+"',f'data-n="{i}"',s['html'])
 s['html']=re.sub(r'data-backup="(?:true|false)"',f'data-backup="{str(s["backup"]).lower()}"',s['html'])
# Factual queue snapshot from the latest message, not a live status claim.
for s in slides:
 s['html']=s['html'].replace('12 November 20:29 CET','12 November 21:42 CET').replace('12 Nov 20:29 CET','12 Nov 21:42 CET')
 s['html']=s['html'].replace('A: 3 folds running; 2 waiting','A: 4 folds running; 1 waiting')
# Exact Higgs2026 template plus scoped adaptations for Reveal navigation and offline reading.
head='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>HToWW November analysis update · Higgs2026 template · r4</title>
<link rel="stylesheet" href="../../../../../_shared/reveal/reset.css"><link rel="stylesheet" href="../../../../../_shared/reveal/reveal.css"><link rel="stylesheet" href="higgs2026-theme.css"><link rel="stylesheet" href="talk.css">
<noscript><style>html,body{height:auto!important;overflow:auto!important}.reveal,.reveal .slides{position:static!important;transform:none!important;width:auto!important;height:auto!important}.reveal .slides>section.slide{display:block!important;position:relative!important;transform:none!important;inset:auto!important;opacity:1!important;visibility:visible!important;margin:20px auto!important;pointer-events:auto!important}body{overflow-x:auto!important}</style></noscript></head><body><div class="reveal"><div class="slides">'''
tail='''</div></div><script src="../../../../../_shared/reveal/reveal.js"></script><script>Reveal.initialize({width:1280,height:720,margin:0,center:false,hash:true,transition:'none',backgroundTransition:'none',controls:true,progress:false,slideNumber:false,pdfSeparateFragments:false,pdfMaxPagesPerSlide:1});</script></body></html>'''
import spacing  # restores spaces lost between words and numbers (keeper, 13 Nov)
(D/'index.html').write_text(spacing.fix_html(head+'\n'.join(s['html'] for s in slides)+tail))
(D/'slides.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='html'} for s in slides],indent=2,ensure_ascii=False)+'\n')
print(len(slides),'slides;',sum(not s['backup'] for s in slides),'main;',sum(s['backup'] for s in slides),'backup')

# Companion notes are generated from the evidence/interpretation annotations, not invented results.
import re,html
lines=['---','tags: [slides, speaker-notes]','status: active','date: 2026-11-12','source: laptop','---','','# November update r4: speaker notes','','Internal CMS talk. The old-card reference and new-production status are explicitly separate. No new A/B limit is claimed.','']
for i,s in enumerate(slides,1):
 raw=s['html'];notes=re.search(r'<aside class="notes">(.*?)</aside>',raw,re.S)
 takeaway=re.search(r'<p class="takeaway">(.*?)</p>',raw,re.S)
 text=(notes.group(1) if notes and notes.group(1).strip() else takeaway.group(1) if takeaway else 'Section divider.')
 text=html.unescape(re.sub('<[^>]*>',' ',text))
 lines += [f"## {i}. {html.unescape(re.sub('<[^>]*>','',s['title']))}",'',f"[Open slide](index.html#/{s['id']})",'',text,'']
(D/'speaker-notes.md').write_text('\n'.join(''.join(part if part.startswith('](') else spacing.fix_text(part) for part in re.split(r'(\]\([^)]*\))',ln)) for ln in lines))
