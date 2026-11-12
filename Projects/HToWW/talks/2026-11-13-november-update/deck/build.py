#!/usr/bin/env python3
"""Build index.html for the HToWW November update deck (keeper, 2026-11-12).

Edit SLIDES below, then run: python3 build.py && node render.mjs --revision=N
Every number on a slide comes from the vault note linked in its source line.
"""
from pathlib import Path
from urllib.parse import quote

REV = 1
LABEL = "H+c, H→WW · November analysis update · 13 Nov 2026 · internal CMS"
MAIN_TAG = "preliminary · checks not independently reviewed"


def note(path, text):
    href = "obsidian://open?vault=obsidian-notes&amp;file=" + quote(path, safe="")
    return f'<a href="{href}">{text}</a>'


N = {
    "plan": "Projects/HToWW/talks/2026-11-12-november-update-slide-plan.md",
    "syst": "Projects/HToWW/combine-systematics/2026-11-12-current-ab-systematics-status.md",
    "cards": "Projects/HToWW/combine-systematics/2026-11-12-final-cards-todo.md",
    "alphas": "Projects/HToWW/combine-systematics/2026-11-12-hplusc-alphas-rate-sources.md",
    "prod": "Projects/HToWW/samples-and-production/full-rerun/2026-11-12-direct-continuation-training-launch.md",
    "state": "Projects/HToWW/samples-and-production/full-rerun/2026-11-05-fullfix-rerun-run-a-state.md",
    "routeb": "Projects/HToWW/samples-and-production/full-rerun/2026-11-12-route-b-integration-and-train.md",
    "ggtt": "Projects/HToWW/samples-and-production/full-rerun/2026-11-12-ggtt-summer23-replacement-and-retry3.md",
    "speed": "Projects/HToWW/framework/optimization/2026-11-05-speedup-patches.md",
    "dup": "Projects/HToWW/framework/2026-11-12-bhive-validation-dupfix-gpu-readiness.md",
    "c1": "Projects/HToWW/framework/2026-11-12-bhive-pipeline-c1-resume.md",
    "trainrun": "Projects/HToWW/framework/2026-11-05-run-framework-legacy-train-run.md",
    "negrw": "Projects/HToWW/negative-weights/2026-11-12-negrw-g1-g2-provenance-and-corrected-stats.md",
    "negrw_v2": "Projects/HToWW/negative-weights/2026-11-12-negrw-retraining.md",
    "negrw_rev": "Projects/HToWW/negative-weights/2026-11-12-negrw-v2-acceptance-review.md",
    "lepsf": "Projects/HToWW/2026-11-10-lepton-sf-provenance-check.md",
    "decisions": "Projects/HToWW/2026-11-10-training-decisions-discussion.md",
}


def src(*items):
    return '<p class="source">Source: ' + " · ".join(items) + "</p>"


def slide(sid, title, body, source, tag=MAIN_TAG, notes=""):
    aside = f'<aside class="notes">{notes}</aside>' if notes else ""
    return (f'<section id="{sid}">\n<p class="label">{LABEL} · {tag}</p>\n'
            f"<h2>{title}</h2>\n{body}\n{source}\n{aside}\n</section>")


def syst_slide(sid, title, rows, foot, source):
    """rows: (name, nuisance, what it is / why it matters, prescription & scope, evidence & status)."""
    head = ("<table class='syst'><colgroup><col style='width:15%'><col style='width:29%'>"
            "<col style='width:30%'><col style='width:26%'></colgroup>"
            "<tr><th>Source</th><th>What it is · why it matters here</th>"
            "<th>Prescription · scope · correlation</th><th>Evidence · status</th></tr>")
    body = "".join(
        f"<tr><td><b>{n}</b><br><code>{k}</code></td><td>{w}</td><td>{p}</td><td>{e}</td></tr>"
        for n, k, w, p, e in rows)
    return slide(sid, title, head + body + "</table>" + f'<p class="foot">{foot}</p>',
                 source, tag="backup · systematics")


PENDING = "Limit impact: <span class='warn'>pending</span>. Needs the new RUN templates and Combine fit; July impacts used a different model and are not current."

SLIDES = []
add = SLIDES.append

# ---------------------------------------------------------------- main
add(f'''<section id="title" class="title">
<p class="label">{LABEL}</p>
<h1>H+c, H→WW→eμνν at Run 3:<br>analysis update</h1>
<p class="sub">Signal modelling (two arms) · new lepton ID and prompt MVA · event MVA retraining · negative-weight reweighting v2 · systematics</p>
<p class="sub">Chirayu Gupta · 13 November 2026</p>
<p class="foot">Four eras: 2022preEE, 2022postEE, 2023preBPix, 2023postBPix. No new limit is shown: production scoring has not run yet (see status).</p>
</section>''')

add(slide("status", "Status: inputs reprocessed for both arms; MVA training is next",
'''<table class="compact"><colgroup><col style="width:30%"><col style="width:15%"><col style="width:55%"></colgroup>
<tr><th>Stage</th><th>State</th><th>Evidence</th></tr>
<tr><td>Code: lepton ID/MVA, corrections, TRAIN/RUN</td><td class="ok">done</td><td>local <code>hww-analysis</code> commits up to <code>71eef55</code>; unit and one-file tests</td></tr>
<tr><td>TRAIN inputs, all MC (A and B)</td><td class="ok">done</td><td>every MC partition has a completion marker: A 2437, B 2572; hash and entry checks pass</td></tr>
<tr><td>negrw v2 (V+jets)</td><td class="ok">adopted</td><td>trained on all 4 eras; fit-bin closure still open</td></tr>
<tr><td>Event MVA, 5 folds × 2 arms</td><td class="warn">preparing</td><td>input checks and fold split running (A: all 2437 MC files passed); then 5 batch-GPU folds per arm. No fold trained yet</td></tr>
<tr><td>RUN scoring, templates, cards</td><td class="todo">not started</td><td>needs the registered fold models</td></tr>
<tr><td>Expected limits A and B</td><td class="todo">not started</td><td>per era and combined</td></tr>
<tr><td>hDamp (tt)</td><td class="todo">deferred</td><td>Up/Down samples configured for all eras; implementation after the MVA training</td></tr>
</table>
<p class="take">Today's message: what changed in the analysis and how it was checked. Results come once A is scored.</p>
<p class="small">Snapshot 12 Nov 2026, ~16:45 CET. <span class="warn">Refresh before presenting.</span></p>''',
src(note(N["prod"], "production continuation note"), note(N["dup"], "MVA readiness"), note(N["negrw"], "negrw follow-up"))))

add(slide("definitions", "Terms used in this talk",
'''<table class="compact"><colgroup><col style="width:21%"><col style="width:79%"></colgroup>
<tr><td><b>4FS / 3FS</b></td><td>four- or three-flavour scheme: the charm quark is massless and in the proton (4FS), or massive and produced only in the hard process (3FS)</td></tr>
<tr><td><b>Arm A</b></td><td>signal from the central <b>4FS</b> FxFx H+c sample alone; a 3FS-vs-4FS shape uncertainty covers the scheme choice</td></tr>
<tr><td><b>Arm B</b></td><td>signal <b>stitched</b>: 4FS for events with no GEN c-jet, private 3FS for events with ≥1 GEN c-jet</td></tr>
<tr><td><b>TRAIN / RUN</b></td><td>two processing modes: TRAIN writes slim nominal features for MVA training; RUN scores events inline and writes histogram templates for all shifts</td></tr>
<tr><td><b>Fold</b></td><td><code>event % 5</code>. Model <i>i</i> never sees fold <i>i</i> in training; RUN scores each event with the model that held it out, so <b>all</b> events enter the templates</td></tr>
<tr><td><b>b-hive</b></td><td>the training framework for the event MVA (6-class DNN)</td></tr>
<tr><td><b>negrw</b></td><td>negative-weight reweighting for amc@NLO V+jets: replaces signed weights by |w|·g(x), g = classifier estimate of the positive fraction</td></tr>
<tr><td><b>prompt MVA</b></td><td>the ttH lepton MVA used to select prompt leptons (Thomas's HWW working points)</td></tr>
</table>
<p class="take">Arm A vs Arm B is the main physics comparison of this round.</p>''',
src(note(N["trainrun"], "framework how-to"), note(N["routeb"], "Route B note"))))

add(slide("analysis", "Analysis recap: one eμ pair, one c-jet, a 6-class MVA",
'''<div class="two"><div>
<ul>
<li><b>Selection:</b> exactly one eμ pair, MET &gt; 45 GeV, ≥1 c-jet candidate, triggers, MET filters, good vertex</li>
<li><b>Classes:</b> H+c, Higgs background, tt, single top, diboson, V+jets</li>
<li><b>Channels:</b> each event goes to the channel of its highest-score class: 1 SR + 5 CRs</li>
<li><b>New:</b> the SR is split into N<sub>c-jet</sub> = 1 and ≥ 2 (AN-23-102: +8% sensitivity in Run 2)</li>
</ul></div><div>
<p><b>26 input features</b></p>
<ul class="small">
<li>14 kinematic: p<sub>T</sub>(ℓℓ), p<sub>T</sub>(ℓ1,ℓ2), p<sub>T</sub>(c), MET, m<sub>T</sub>(ℓ1,ℓ2), m<sub>ℓℓ</sub>, ΔR and Δφ between leptons, c-jet and MET</li>
<li>11 one-hot c-tag categories (L0, C0–C4, B0–B4) from PNet CvsL × CvsB</li>
<li>nSV (secondary vertices)</li>
</ul></div></div>
<p class="take">The selection and features are unchanged in definition; the leptons and corrections feeding them changed.</p>''',
src("<code>analysis/features/hww.py</code>, <code>hww_allfix_4fs.yaml</code> (lxplus HEAD <code>71eef55</code>, read 12 Nov)")))

add(slide("arms", "Two signal descriptions: Arm A (4FS) and Arm B (3FS/4FS stitched)",
'''<div class="two"><div>
<p><b>Arm A</b> — central 4FS FxFx H+c</p>
<ul class="small">
<li>Normalised to σ<sub>NNLO</sub>×BR = <b>0.0016626 pb</b> (all eras)</li>
<li>Scheme uncertainty: reweight by leading GEN c-hadron p<sub>T</sub>; Up = 3FS-like, Down = 2 − Up</li>
<li>Replaces the old flat 30%</li>
</ul></div><div>
<p><b>Arm B</b> — stitched (LHCHWG-2026-007 §4.4)</p>
<ul class="small">
<li>N<sub>c-jet</sub> = 0 from 4FS, N<sub>c-jet</sub> ≥ 1 from private 3FS; GEN c-jet p<sub>T</sub> &gt; 10 GeV, |η| &lt; 2.5, R = 0.4</li>
<li>Same σ×BR; each region scaled per era by L·σ·c<sub>s</sub>/F<sub>s</sub></li>
<li>3FS PDF: 100 MC replicas (LHA 321900) → replica standard deviation</li>
<li>Arm A's scheme nuisance is off (no double counting)</li>
</ul></div></div>
<p class="take">Same analysis, two signal models: the A/B difference measures the flavour-scheme dependence directly.</p>''',
src(note(N["routeb"], "Route B integration"), note(N["state"], "full-fix state"), "arXiv:2608.26863 §4.4")))

add(slide("samples", "Samples and normalisation updates",
'''<ul>
<li><b>H+c</b>: 0.0016626 pb in all eras (NNLO); running-Yukawa scale fix in the μ<sub>R</sub> weights</li>
<li><b>m<sub>H</sub> = 125.09 GeV convention</b> adopted. Done so far: <b>H→ττ</b> backgrounds (ggH 3.264 pb, VBF 0.2549 pb, W<sup>±</sup>H) from the LHCHWG 13.6 TeV tables × BR<sub>ττ</sub> 0.06256. Other Higgs rates: <span class="warn">not yet re-derived</span></li>
<li><b>2023preBPix ggH→ττ</b>: Winter23 sample replaced by Summer23 v14</li>
<li><b>ttH→ττ coverage open</b>: our <code>ttHnonBB</code> group is the exclusive cc, γγ, Zγ samples, not an inclusive non-bb sample</li>
<li>Generated mass is unchanged: renormalisation changes rates, not kinematics</li>
</ul>
<p class="take">Normalisations are being moved to one convention; the H→ττ part is done.</p>''',
src(note(N["prod"], "continuation note"), note(N["ggtt"], "H→ττ replacement"), note(N["state"], "full-fix state"))))

add(slide("leptonmva", "Prompt-lepton MVA: Thomas's working points, now via ONNX",
'''<ul>
<li><b>What:</b> muons tight ID + tight PF iso + prompt MVA; electrons POG Medium + prompt MVA (HWW/latinos WPs)</li>
<li><b>How:</b> TMVA weights converted to ONNX and scored vectorised once per chunk, on NanoAOD inputs before scale/smearing; reused by every shift</li>
<li><b>Check vs TMVA:</b> max |Δscore| = <b>3.05×10<sup>−7</sup></b> (μ, 24,484 leptons), <b>3.27×10<sup>−7</sup></b> (e, 25,713), including threshold-tie leptons</li>
<li><b>Fixes vs the reference code:</b> signed η for muon SFs (tables span −2.4…2.4); no φ argument for 2023 electron SFs; supercluster η for electrons</li>
<li><b>SFs:</b> all 8 SF files byte-identical to latinos; factorisation matches how latinos applies them</li>
<li><b>Effect:</b> one H+c file keeps 423 events vs 563 with the old leptons (−25%)</li>
</ul>
<p class="take">Same physics as the HWW group's leptons, faster, and checked against the reference to 10<sup>−7</sup>.</p>''',
src(note(N["state"], "full-fix state §ttH MVA"), note(N["lepsf"], "lepton-SF provenance"))))

add(slide("speed", "Processing speed-ups with byte-identical output",
'''<table class="compact"><colgroup><col style="width:34%"><col style="width:66%"></colgroup>
<tr><th>Change</th><th>Effect</th></tr>
<tr><td>parquet writer via numpy</td><td><code>dump_parquet</code> 16.8 s → 1.8 s per chunk</td></tr>
<tr><td>cache era YAML</td><td>parsed once instead of 15× per chunk</td></tr>
<tr><td>cache trigger YAML</td><td>once instead of 45× per chunk</td></tr>
<tr><td>cache correctionlib sets</td><td>c-tag, pileup loaded once per process</td></tr>
</table>
<ul>
<li>One H+c file, one chunk (85,732 events): <b>46.5 s → 31.1 s</b> wall (−33%)</li>
<li>Outputs <b>byte-identical</b> (16/16 parquets, multi-chunk 64/64) with seeded muon RNG</li>
<li>Scope: one-file benchmark, not a measured campaign speed-up. Next cost: object selection re-run for each of 15 shift passes</li>
</ul>
<p class="take">Faster with no change in output; reproducibility needed seeding the muon smearing RNG.</p>''',
src(note(N["speed"], "speed-up patches"))))

add(slide("mva", "Event MVA: retrained for the new leptons and signal",
'''<ul>
<li><b>Why retrain:</b> v11 was trained with the old tight/wp80iso leptons and older corrections; the selected events changed</li>
<li><b>Folds:</b> 5 outer folds by <code>event % 5</code>; model <i>i</i> trains on the other four folds</li>
<li><b>Validation:</b> b-hive splits the training list 85/15 internally (seed 20261112)</li>
<li><b>Loss weights:</b> class weights only (event weights not in the loss): unchanged convention</li>
<li><b>Recipe:</b> 30 epochs, batch 1024, lr 10<sup>−3</sup>, same architecture and 26 features</li>
<li><b>RUN:</b> every event scored once, by the model that never saw it</li>
<li><b>Guards:</b> RUN refuses a model whose feature hash, selection hash, classes, folds or file SHA256 differ</li>
</ul>
<div class="bar"><span class="train" style="width:68%">~68% train</span><span class="valid" style="width:12%">~12% val</span><span class="test" style="width:20%">20% test fold</span></div>
<p class="small">Shares are approximate (by constructed-file fraction). Training inputs are MC only.</p>''',
src(note(N["trainrun"], "framework how-to"), note(N["dup"], "MVA readiness"), note(N["decisions"], "training decisions"))))

add(slide("mvacheck", "MVA reliability: a validation-duplication bug, fixed and tested",
'''<ul>
<li><b>Found:</b> b-hive's loader re-emitted the leftover partial batch, so validation and inference rows were duplicated</li>
<li><b>Size:</b> on 129 real validation files, 103,980 rows emitted for 38,700 events (2.69×); inference 170,465 rows for 64,073 held-out events</li>
<li><b>Effect:</b> biased the validation loss, hence best-epoch selection (and v11's)</li>
<li><b>Fix:</b> every row emitted exactly once: tests over partial, exact-multiple and tiny files, with 0/2/3 loader workers</li>
<li><b>Training unchanged:</b> epoch-0 weights bitwise identical before and after the fix</li>
<li><b>Reproducible:</b> same seed on an A100 → bitwise-identical weights (max |Δw| = 0)</li>
<li><b>Provenance:</b> each fold records code hashes; registration refuses pre-fix or mixed-code folds</li>
</ul>
<p class="take">Model selection now uses a clean validation sample, and a rerun gives the same model.</p>''',
src(note(N["dup"], "dup-fix and GPU note"))))

add(slide("negrw", "negrw v2: retrained on all eras with the new leptons",
'''<div class="two"><div>
<ul class="small">
<li><b>Why:</b> amc@NLO V+jets has many negative weights; |w|·g keeps the yield and cuts the variance</li>
<li><b>v2:</b> same recipe (20 GEN-level features, 20 boosted-tree members); trained on <b>all 4 eras</b> (7.6 M rows), training region defined with the new leptons → disjoint from the eμ SR</li>
<li><b>Held-out</b> events (<code>event % 5 == 0</code>, 1.5 M) for closure</li>
<li>AUC 0.8181 vs 0.8183 (July); corr(g<sub>v2</sub>, g<sub>July</sub>) = 0.9987</li>
<li><b>SR closure</b> (17,627 events): v2 1.011 ± 0.021, July 1.019 ± 0.021</li>
<li>Adopted for both arms; nuisance <code>CMS_negrw_vjets</code> = ensemble spread</li>
</ul></div>
<div><img src="assets/04_closure_holdout_era_dataset.png" alt="negrw held-out closure per era and dataset, v2 vs July"><p class="cap">Held-out closure Σ|w|g/Σw per era and dataset, v2 (blue) vs July (red)</p></div></div>
<p class="take">v2 is equivalent to July in shape, and its inputs now match the current analysis.</p>''',
src(note(N["negrw_v2"], "negrw retraining"), note(N["negrw"], "corrected statistics"), "plots: EOS <code>negrw_out_img/v2_20261112/corrected_report_20261112/img</code>")))

add(slide("negrw-limits", "negrw: closure is good overall, not per sample",
'''<div class="two"><div>
<table class="compact"><tr><th>held-out</th><th>v2 R</th><th>(R−1)/σ</th></tr>
<tr><td>total</td><td>0.9984</td><td>−1.4</td></tr>
<tr><td>DY 10–50</td><td>0.8980</td><td>−11.2</td></tr>
<tr><td>DY 50</td><td>1.0080</td><td>+6.5</td></tr>
<tr><td>W 0J</td><td>0.9855</td><td>−13.2</td></tr>
<tr><td>W 1J</td><td>1.0086</td><td>+3.1</td></tr>
<tr><td>W 2J</td><td>1.0004</td><td>+0.1</td></tr></table>
<p class="small">σ: delta-method on R = Σ|w|g/Σw (earlier quoted σ were too large). Rates are renormalised per era and sample.</p>
<p class="small">Shape after renormalisation, DY 50, N<sub>jet</sub>≥1, V p<sub>T</sub>: χ² 47.2/20 (35.0 with the nuisance); July 47.9/20</p>
</div>
<div><img src="assets/09_shape_renorm_lhe_vpt_njets_ge1_DYto2L_2Jets_50.png" alt="shape residual after renormalisation, DY 50 njets>=1, lhe_vpt"><p class="cap">Shape residual after per-sample renormalisation vs the |<code>CMS_negrw_vjets</code>| band (grey)</p></div></div>
<p class="take">Residual shape bias exists in both models and is not fully covered by the band: the closure check in the final fit bins is still open.</p>''',
src(note(N["negrw"], "G1/G2 and corrected stats"), note(N["negrw_rev"], "acceptance review"))))

add(slide("syst-overview", "Systematics: what is in the model now",
'''<table class="compact"><colgroup><col style="width:22%"><col style="width:52%"><col style="width:26%"></colgroup>
<tr><th>Group</th><th>Sources</th><th>Change since summer</th></tr>
<tr><td>Normalisation</td><td>luminosity, cross sections, BRs, tt rateParam</td><td>H→ττ at 125.09</td></tr>
<tr><td>Leptons</td><td>μ ID, iso, prompt MVA; e ID, prompt MVA, reco (3 p<sub>T</sub> bins); μ/e scale and resolution</td><td><b>new</b> lepton IDs and SFs</td></tr>
<tr><td>Jets and MET</td><td>JES (Total), JER, unclustered MET, pileup</td><td>unclustered MET <b>added</b></td></tr>
<tr><td>c-tagging</td><td>2D SF Total Up/Down</td><td>provisional (calibration update awaited)</td></tr>
<tr><td>Theory</td><td>ISR, FSR, μ<sub>R</sub>, μ<sub>F</sub>, μ<sub>R</sub>μ<sub>F</sub>, PDF, top p<sub>T</sub>, H+heavy-flavour</td><td>H+c PDF rate 7.4%; H+HF ±50% per event</td></tr>
<tr><td>Signal scheme</td><td>A: 3FS/4FS shape · B: stitching</td><td><b>new</b> in both arms</td></tr>
<tr><td>Method / MC</td><td>negrw ensemble, autoMCStats</td><td>negrw v2</td></tr>
<tr><td>tt modelling</td><td>hDamp</td><td><span class="warn">deferred</span></td></tr>
</table>
<p class="take">All sources are implemented except hDamp (deferred); none has a measured impact in the new fit yet. One backup slide per group explains each source.</p>''',
src(note(N["syst"], "systematic inventory (HEAD 71eef55)"))))

add(slide("hdamp", "hDamp: the missing tt matching uncertainty",
'''<ul>
<li><b>What:</b> POWHEG's h<sub>damp</sub> sets where hard real emission hands over to the shower. Varying it probes ME–PS matching for the top</li>
<li><b>Why here:</b> tt is a main background with its own CR and enters the SR; hDamp changes jet multiplicity and the extra-jet spectrum, so c-jet and category migrations</li>
<li><b>Not covered by ISR/FSR:</b> those vary shower radiation; h<sub>damp</sub> varies the matching scale</li>
<li><b>Samples:</b> dedicated <code>TTto2L2Nu_Hdamp158</code> (Down) and <code>_Hdamp418</code> (Up), configured in all 4 eras (σ = 98.578 pb)</li>
<li><b>Plan:</b> alternative-sample templates, each normalised by its own Σw; compare to nominal tt in D, N<sub>jet</sub>, acceptance; check MC stat; one nuisance on tt</li>
<li><b>Status:</b> <span class="warn">deferred until after the MVA training</span>; no template or card yet. Alternative samples stay out of the training sample</li>
</ul>
<p class="take">Adds the standard tt matching variation; results come with the RUN production.</p>''',
src(note(N["prod"], "continuation note §hDamp"), note(N["syst"], "inventory"))))

add(slide("results", "Results: pending production",
'''<table class="compact"><colgroup><col style="width:36%"><col style="width:64%"></colgroup>
<tr><th>Planned result</th><th>Needs</th></tr>
<tr><td>Classifier performance per fold (ROC, overtraining)</td><td>trained folds</td></tr>
<tr><td>SR and CR templates, data/MC in CRs</td><td>RUN over all eras</td></tr>
<tr><td>Systematic Up/Down ratio plots</td><td>RUN shift templates</td></tr>
<tr><td>Expected limit per era and combined, Arm A</td><td>cards + Combine</td></tr>
<tr><td>Same for Arm B, and A vs B</td><td>B scored after A</td></tr>
<tr><td>Impacts and pulls</td><td>new fit (July impacts are not comparable)</td></tr>
</table>
<p class="take">Order: Arm A first, then Arm B. No number is shown until it is produced and checked.</p>''',
src(note(N["prod"], "production status"))))

add(slide("open", "Open questions and next steps",
'''<ul>
<li><b>H+c α<sub>S</sub> rate:</b> the 4FS sample has no α<sub>S</sub> pair; no process-specific number yet (the old 3% had no H+c source)</li>
<li><b>H+b PDF⊕α<sub>S</sub>:</b> candidate +3.36/−3.44%, not installed; check overlap with the 5% Higgs-background rate</li>
<li><b>BR(H→WW), BR(H→ττ) 1%:</b> applied to the whole merged Higgs background; needs component-aware scope</li>
<li><b>c-tag calibration:</b> provisional; category edges are MVA inputs, so a change may need retraining</li>
<li><b>negrw:</b> closure in the final fit bins after scoring</li>
<li><b>ttH→ττ:</b> coverage of the exclusive ttH samples</li>
<li><b>Arm B:</b> 3FS PDF rate vs the 7.4% signal PDF rate; scale normalisation across the stitched regions</li>
<li><b>Trigger SFs</b> disabled by earlier decision: no trigger nuisance, which is not a measured zero</li>
</ul>
<p class="take">Next: train and score Arm A, build cards, first expected limit; then Arm B and the comparison.</p>''',
src(note(N["syst"], "inventory"), note(N["alphas"], "α<sub>S</sub> sources"), note(N["cards"], "final-cards to-do"))))

# ---------------------------------------------------------------- backup: systematics
add('''<section id="backup" class="title"><p class="label">''' + LABEL + '''</p><h1>Backup</h1>
<p class="sub">One slide per systematic group: what it is, how it is varied, what has been checked.</p>
<p class="foot">Common to all: implemented in code at HEAD <code>71eef55</code>; <b>no new templates, plots or impacts yet</b>. Detector nuisances are named per year (2022, 2023): pre/post sub-eras within a year are correlated.</p></section>''')

add(syst_slide("backup-syst-norm", "Normalisation: luminosity, pileup",
[("Luminosity", "lumi_&lt;year&gt;", "Uncertainty on the integrated luminosity; scales every simulated yield", "lnN 1.4% (2022), 1.3% (2023); all MC except free-floating tt; separate per year", "Configured. Official common-component correlation model not implemented"),
 ("Pileup", "CMS_pileup_&lt;year&gt;", "Uncertain distribution of extra pp collisions per crossing; changes MET, isolation, jet counts", "Event-weight Up/Down from the pileup calibration; all MC", "Implemented; template effect pending")],
PENDING, src(note(N["syst"], "inventory §detector"))))

add(syst_slide("backup-syst-lepsf", "Lepton efficiency scale factors",
[("μ ID", "CMS_eff_m_id_&lt;year&gt;", "Data/MC difference in identifying a real muon", "HWW tight-ID SF Up/Down per lepton; all MC", "Files identical to latinos (md5)"),
 ("μ isolation", "CMS_eff_m_iso_&lt;year&gt;", "Data/MC difference in a real muon looking isolated", "Tight PF iso SF, conditional on ID", "Same producer chain"),
 ("μ prompt MVA", "CMS_eff_m_promptMVA_&lt;year&gt;", "Efficiency of the prompt-MVA cut on real muons", "ttH-MVA SF on top of ID×iso", "Up/nom 1.0036 on one H+c file"),
 ("e ID", "CMS_eff_e_id_&lt;year&gt;", "Data/MC difference for POG Medium electrons", "Medium SF", "Matches the latinos combination"),
 ("e prompt MVA", "CMS_eff_e_promptMVA_&lt;year&gt;", "Efficiency of the prompt-MVA cut on real electrons", "Medium+MVA conditional factor", "Up/nom 1.0097 on one H+c file"),
 ("e reco", "CMS_eff_e_reco_{below20, 20to75, above75}", "Electron reconstruction efficiency, measured in three p<sub>T</sub> ranges", "Three independent nuisances by p<sub>T</sub> range", "Implemented")],
"Product ID×iso×MVA (μ) and Medium×MVA×reco (e) matches how latinos applies the same files; no double counting found. Measurement definitions are less documented. " + PENDING,
src(note(N["lepsf"], "lepton-SF provenance"), note(N["state"], "full-fix state"))))

add(syst_slide("backup-syst-lepscale", "Lepton momentum scale and resolution",
[("μ scale", "CMS_scale_m_&lt;year&gt;", "Uncertainty in the absolute muon momentum calibration; moves p<sub>T</sub>, m<sub>ℓℓ</sub>, m<sub>T</sub>", "Object shift Up/Down; selection and features recomputed for each shift", "Implemented; migrations pending"),
 ("μ resolution", "CMS_res_m_&lt;year&gt;", "Uncertainty in the extra smearing that matches MC resolution to data (width, not mean)", "Object shift Up/Down", "Deterministic per-event path implemented; output checks pending"),
 ("e scale", "CMS_scale_e_&lt;year&gt;", "Uncertainty in the absolute electron energy calibration", "Object shift Up/Down", "Implemented"),
 ("e resolution", "CMS_res_e_&lt;year&gt;", "Uncertainty in the electron energy smearing", "Object shift Up/Down", "Earlier nominal-only smearing-key bug fixed")],
"Object shifts re-run the full selection, so acceptance and channel migrations are included, not only weights. " + PENDING,
src(note(N["syst"], "inventory"))))

add(syst_slide("backup-syst-jets", "Jets, MET, c-tagging, trigger",
[("JES", "CMS_scale_j_&lt;year&gt;", "Uncertainty in the jet energy response; moves jets, c-jet choice and MET", "Total source Up/Down, propagated to MET", "Implemented; no per-source split"),
 ("JER", "CMS_res_j_&lt;year&gt;", "MC jet resolution vs data", "Smearing Up/Down, propagated to MET", "Implemented"),
 ("Unclustered MET", "CMS_met_unclustered_&lt;year&gt;", "Soft energy not in jets or leptons; enters MET and m<sub>T</sub>", "Up/Down on the unclustered component", "<b>Added</b>; was missing in July"),
 ("c-tag", "CMS_ctag2d_&lt;year&gt;", "Data/MC difference in PNet CvsL/CvsB, which define the 11 categories (MVA inputs)", "2D SF Total Up/Down", "<span class='warn'>provisional</span>: calibration update awaited"),
 ("Trigger", "—", "Online selection efficiency", "SFs disabled by earlier decision", "No nuisance; not a measured zero")],
PENDING, src(note(N["syst"], "inventory"), note(N["lepsf"], "c-tag status"))))

add(syst_slide("backup-syst-theory", "Theory: parton shower, scales, top p<sub>T</sub>",
[("ISR / FSR", "ps_isr, ps_fsr", "Shower radiation from incoming / outgoing partons; changes jet activity", "PS weight pairs; all processes except tt; one name across processes and eras", "Implemented"),
 ("μ<sub>R</sub>, μ<sub>F</sub>", "scalevar_muR, _muF, _muR_muF", "Missing higher orders: renormalisation and factorisation scale choice", "LHE weights ×2 and ×0.5; three directions (not an envelope); running-Yukawa fix for H+c/H+b", "Implemented; tt excluded"),
 ("Top p<sub>T</sub>", "top_pt", "Data prefer a softer top p<sub>T</sub> than MC", "Nominal reweighted; Down = none, Up = symmetric", "Implemented"),
 ("H + heavy flavour", "higgs_plus_c", "Uncertain rate of ggH/VBF with a real c-jet", "±50% on ggH/VBF events with a GEN c-jet (p<sub>T</sub>&gt;25, |η|&lt;2.5)", "Replaces flat 40% on all Higgs bkg")],
PENDING, src(note(N["syst"], "inventory §theory"))))

add(syst_slide("backup-syst-pdf", "PDF and α<sub>S</sub>",
[("PDF shape", "lhe_pdf", "Parton momentum and flavour content of the proton; changes acceptance and shape", "Hessian members (4FS); MC-replica std (Arm B 3FS); inclusive rate removed per member", "Acceptance may still change"),
 ("H+c PDF rate", "xsec_hplusc_PDF", "PDF uncertainty on the inclusive signal cross section", "lnN 1.074, both arms", "7.43% ± 0.14% (stat) from the 13.6 TeV 4FS gridpack"),
 ("α<sub>S</sub>", "lhe_alphaS", "Uncertainty in α<sub>S</sub>(m<sub>Z</sub>), distinct from scale choice", "Event weights where members exist", "<span class='warn'>4FS H+c has no α<sub>S</sub> pair</span>"),
 ("H+c α<sub>S</sub> rate", "—", "α<sub>S</sub> effect on the signal rate", "Needs a process-specific calculation (PDF4LHC recipe)", "<span class='warn'>missing</span>; old 3% unsourced"),
 ("H+b PDF⊕α<sub>S</sub>", "—", "Theory rate of H+b inside the Higgs background", "Candidate +3.36/−3.44%", "Not installed; overlap with 5%")],
"Arm B: 3FS is not renormalised like 4FS, so check that its PDF rate is not counted twice with the 7.4%. " + PENDING,
src(note(N["syst"], "inventory"), note(N["alphas"], "α<sub>S</sub> sources"))))

add(syst_slide("backup-syst-scheme", "Signal flavour scheme and negrw",
[("A: 3FS vs 4FS", "xsec_hplusc_3FS_4FS", "4FS vs 3FS give different charm kinematics", "Shape from leading GEN c-hadron p<sub>T</sub>: Up = 3FS-like, Down = 2 − Up; Arm A only", "Replaces flat 30%"),
 ("B: stitching", "—", "How 3FS (≥1 c-jet) and 4FS (0 c-jet) regions are joined", "Per-era stitch factors; A's scheme nuisance off", "Missing-rate, scale and PDF consistency checks pending"),
 ("negrw", "CMS_negrw_vjets", "Spread of the negative-weight model on V+jets", "20-member ensemble spread; per-era/sample yield preserved", "Band does not cover all shape bias; fit-bin closure open")],
PENDING, src(note(N["routeb"], "Route B"), note(N["negrw"], "negrw"))))

add(syst_slide("backup-syst-rates", "Rates, fit freedom, MC statistics",
[("Single top", "—", "Inclusive cross-section uncertainty", "lnN −1.27/+1.67%", "Configured"),
 ("Diboson / V+jets", "—", "Inclusive cross sections of merged groups", "lnN 3.7% / 2.7%", "Configured"),
 ("Higgs bkg / BRs", "—", "Production rate; BR(H→WW), BR(H→ττ)", "5%; 1% each on the whole merged group", "<span class='warn'>BR scope too broad</span>"),
 ("tt normalisation", "rate_tt", "Free in the fit, constrained by the tt CR", "rateParam, range [0, 5]", "Not a prior"),
 ("MC statistics", "autoMCStats 10", "Finite simulated events per bin (incl. negative weights)", "Barlow–Beeston-lite per bin from Σw²; threshold 10 events", "Not a flat 10%")],
"Correlations: detector by year; theory names shared across eras. " + PENDING,
src(note(N["syst"], "inventory §rates"))))

# ---------------------------------------------------------------- other backup
add(slide("backup-negrw-sr", "Backup: negrw in the eμ SR (V+jets, 17,627 events)",
'''<div class="two"><div><img src="assets/07_sr_vpt.png" alt="V pT in the SR: nominal, v2, July"></div>
<div><img src="assets/09_shape_renorm_lhe_vpt_all_WtoLNu_2Jets_1J.png" alt="W 1J vpt shape residual after renormalisation">
<p class="cap">W+1J, V p<sub>T</sub>: χ² 139.4/20 (v2), 185.5/20 (July); 120.1 / 155.6 with the nuisance</p></div></div>
<p class="take">In the SR the two models agree with each other; the residual per-sample shape bias is common to both.</p>''',
src(note(N["negrw"], "corrected stats")), tag="backup"))

add(slide("backup-ctag", "Backup: 2D c-tag categories used as MVA inputs",
'''<ul>
<li>Leading c-jet candidate scored by PNet CvsL (x) and CvsB (y)</li>
<li>x edges: 0, 0.250, 0.452, 0.808, 1</li>
<li>y edges: 0, 0.006, 0.017, 0.055, 0.761, 0.944, 0.985, 0.995, 1</li>
<li>11 categories: L0, C0–C4, B0–B4, one-hot inputs to the event MVA</li>
<li>Edges are hashed into the feature signature: changing them invalidates trained models</li>
</ul>
<p class="take">A new c-tag calibration with new edges means retraining; with the same edges only the SF weights change.</p>''',
src("<code>analysis/corrections/ctag2d_categories.py</code> (HEAD <code>71eef55</code>)", note(N["syst"], "inventory")), tag="backup"))

add(slide("backup-production", "Backup: production bookkeeping",
'''<ul>
<li>TRAIN partitions expected: A 2729, B 2864 (after the H→ττ replacement)</li>
<li>MC inputs frozen for training: A 2437 markers / 22,613 parquets; B 2572 / 24,598</li>
<li>Training preparation re-checks every MC marker (mode, era, hashes, entries, exact file list), duplicate chunks, normalisation and Route B stitch records before any fold starts</li>
<li>Model registry: <code>/eos/user/c/cgupta/higgscharm/outputs/hww_mva_models/</code></li>
<li>Code: <code>hww-analysis</code> local commits <code>ccdc8f9</code>, <code>b6d52ea</code>, <code>71eef55</code>; b-hive <code>195fd67</code>; none pushed</li>
</ul>''',
src(note(N["prod"], "continuation note"), note(N["dup"], "MVA readiness")), tag="backup"))

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HToWW November analysis update - 13 Nov 2026 (r%d)</title>
<link rel="stylesheet" href="../../../../../_shared/reveal/reset.css">
<link rel="stylesheet" href="../../../../../_shared/reveal/reveal.css">
<style>
:root { --ink:#172b42; --accent:#126782; --muted:#526374; --line:#c4d1d9; --warn:#9a4b00; --ok:#2c6e3f; }
body { background:#fff; color:var(--ink); font-family: Arial, sans-serif; }
.reveal { font-size: 25px; line-height: 1.32; }
.reveal .slides { text-align: left; }
.reveal .slides section { box-sizing: border-box; padding: 26px 44px 18px; }
.reveal h1 { font-size: 1.9em; color: var(--ink); margin: 120px 0 26px; line-height: 1.15; }
.reveal h2 { color: var(--ink); font-size: 1.3em; font-weight: 700; line-height: 1.14; margin: 0 0 16px; }
.reveal p { margin: 0 0 12px; }
.reveal ul { margin: 0 0 12px 1em; padding: 0; list-style: disc; }
.reveal li { margin-bottom: 7px; padding-left: 4px; }
.reveal strong, .reveal b { color: var(--accent); }
.reveal a { color: var(--accent); }
.reveal code { font-family: monospace; font-size: .84em; overflow-wrap: anywhere; }
.reveal table { border-collapse: collapse; width: 100%%; margin-bottom: 12px; }
.reveal th, .reveal td { text-align: left; padding: 6px 12px 6px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
.reveal th { color: var(--accent); }
.reveal .compact { font-size: .74em; }
.reveal table.syst { font-size: .6em; line-height: 1.25; }
.reveal table.syst td, .reveal table.syst th { padding: 5px 10px 5px 0; }
.reveal table.syst code { font-size: .9em; color: var(--muted); }
.reveal .label { color: var(--muted); font-size: .54em; margin-bottom: 8px; }
.reveal .warn { color: var(--warn); font-weight: 700; }
.reveal .ok { color: var(--ok); font-weight: 700; }
.reveal .todo { color: var(--muted); font-weight: 700; }
.reveal .take { color: var(--accent); font-weight: 600; margin-top: 10px; }
.reveal .small { font-size: .78em; }
.reveal .sub { font-size: .9em; color: var(--muted); }
.reveal .foot { font-size: .62em; color: var(--muted); }
.reveal .cap { font-size: .58em; color: var(--muted); }
.reveal .source { font-size: .5em; line-height: 1.35; color: var(--muted); margin-top: 10px; }
.reveal .two { display: flex; gap: 28px; align-items: flex-start; }
.reveal .two > div { flex: 1 1 0; min-width: 0; }
.reveal img { max-width: 100%%; max-height: 330px; display: block; margin: 0 auto 4px; }
.reveal aside.notes { display: none; }
.reveal .bar { display: flex; height: 34px; margin: 6px 0 4px; font-size: .7em; }
.reveal .bar span { display: flex; align-items: center; justify-content: center; }
.reveal .train { background: #126782; color: white; }
.reveal .valid { background: #d9a441; color: #172b42; }
.reveal .test { background: #74b6ad; color: #172b42; }
.reveal .slide-number { font: 14px Arial, sans-serif; color: var(--muted); background: transparent; }
.reveal .progress { color: var(--accent); height: 3px; }
.reveal .controls { color: var(--accent); }
.vault-nav { position: fixed; bottom: 10px; left: 20px; z-index: 50; font: 13px Arial, sans-serif; color: #526374; }
.vault-nav a { color: #126782; margin-right: 16px; }
@media print { .vault-nav { display: none; } }
</style>
<!-- Obsidian's HTML viewer runs with scripts off: show every slide as a plain page. -->
<noscript><style>
html, body { overflow: auto !important; height: auto !important; }
.reveal, .reveal .slides, .reveal .slides > section {
  position: static !important; display: block !important; transform: none !important;
  width: auto !important; height: auto !important; inset: auto !important;
  overflow: visible !important; opacity: 1 !important; visibility: visible !important;
  pointer-events: auto !important; margin: 0 !important; }
.reveal .slides > section { max-width: 1180px; margin: 0 auto !important;
  border-bottom: 2px solid #c4d1d9; padding: 30px 40px !important; }
.reveal h1 { margin-top: 20px; }
</style></noscript>
</head>
<body>
<nav class="vault-nav" aria-label="Vault and slide navigation"><a href="obsidian://open?vault=obsidian-notes&amp;file=%s">Open slide plan in Obsidian</a><a href="../../../../../index.html">All decks</a></nav>
<div class="reveal"><div class="slides">
'''

TAIL = '''
</div></div>
<script src="../../../../../_shared/reveal/reveal.js"></script>
<script>
Reveal.initialize({ width: 1280, height: 720, margin: 0.04, center: false,
  hash: true, transition: 'none', backgroundTransition: 'none',
  controls: true, progress: true, slideNumber: 'c/t',
  pdfSeparateFragments: false, pdfMaxPagesPerSlide: 1 });
</script>
</body>
</html>
'''

out = Path(__file__).with_name("index.html")
out.write_text(HEAD % (REV, quote(N["plan"], safe="")) + "\n".join(SLIDES) + TAIL)
print(out, len(SLIDES), "slides")
