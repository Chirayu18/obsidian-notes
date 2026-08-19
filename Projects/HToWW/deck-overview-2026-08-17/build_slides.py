from pathlib import Path

TMP = Path("/home/cgupta/.claude/jobs/af76ec6a/tmp")
IMG_SR = (TMP / "img_sr.txt").read_text().strip()
IMG_TOP = (TMP / "img_topcr.txt").read_text().strip()

HTML = """<title>Kinematic cuts vs the MVA — where the gain actually is</title>
<style>
:root{
  --ground:#FAFAF8; --card:#FFFFFF; --ink:#16181C; --muted:#6E7178;
  --rule:#E2E0DB; --rule-strong:#CFCCC5;
  --mva:#B23A2E; --mva-soft:#F5E7E4;
  --cut:#7C8794; --cut-soft:#EDEFF1;
  --good:#2E6B4F; --good-soft:#E4EFE9;
  --shadow:0 1px 2px rgba(22,24,28,.05),0 8px 24px -12px rgba(22,24,28,.18);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#111316; --card:#181B1F; --ink:#ECEAE5; --muted:#9DA1A8;
    --rule:#2A2E33; --rule-strong:#3A3F45;
    --mva:#E4776A; --mva-soft:#33211F;
    --cut:#96A1AD; --cut-soft:#20242A;
    --good:#6FC099; --good-soft:#1B2A24;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --ground:#111316; --card:#181B1F; --ink:#ECEAE5; --muted:#9DA1A8;
  --rule:#2A2E33; --rule-strong:#3A3F45;
  --mva:#E4776A; --mva-soft:#33211F;
  --cut:#96A1AD; --cut-soft:#20242A;
  --good:#6FC099; --good-soft:#1B2A24;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Source Sans 3","Segoe UI",system-ui,-apple-system,sans-serif;
  font-size:16px; line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px;margin:0 auto;padding:40px 24px 72px;display:flex;flex-direction:column;gap:26px}

.masthead{border-bottom:2px solid var(--ink);padding-bottom:18px;display:flex;flex-direction:column;gap:8px}
.kicker{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--mva)}
h1{font-family:Fraunces,"Iowan Old Style",Georgia,serif;font-weight:600;
  font-size:clamp(28px,4.4vw,44px);line-height:1.08;margin:0;text-wrap:balance;letter-spacing:-.015em}
.standfirst{color:var(--muted);font-size:17px;max-width:64ch;margin:0}

.slide{background:var(--card);border:1px solid var(--rule);border-radius:3px;
  box-shadow:var(--shadow);padding:26px 28px 28px;display:flex;flex-direction:column;gap:16px}
.slide-head{display:flex;gap:14px;align-items:baseline;border-bottom:1px solid var(--rule);padding-bottom:12px}
.num{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;color:var(--mva);
  font-weight:700;letter-spacing:.08em;flex:none;padding-top:4px}
h2{font-family:Fraunces,"Iowan Old Style",Georgia,serif;font-weight:600;
  font-size:clamp(19px,2.5vw,25px);line-height:1.2;margin:0;text-wrap:balance;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:14.5px;margin:0}
p{margin:0;max-width:70ch}

.tbl-wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:2px}
table{border-collapse:collapse;width:100%;font-size:14px;
  font-variant-numeric:tabular-nums}
th,td{padding:9px 13px;text-align:right;border-bottom:1px solid var(--rule);white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal;min-width:210px}
thead th{background:var(--cut-soft);font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);font-weight:600;border-bottom:1px solid var(--rule-strong)}
tbody tr:last-child td{border-bottom:none}
td.num-cell{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:13.5px}
tr.win{background:var(--mva-soft)}
tr.win td:first-child{font-weight:600;color:var(--mva)}
tr.verdict{background:var(--good-soft)}
tr.verdict td{font-weight:600;color:var(--good)}
.tag{display:inline-block;font-family:"JetBrains Mono",ui-monospace,monospace;
  font-size:10px;letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;border-radius:2px;
  vertical-align:middle;margin-left:8px}
.tag-mva{background:var(--mva);color:#fff}
.tag-cut{background:var(--cut);color:#fff}

figure{margin:0;display:flex;flex-direction:column;gap:9px}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:2px;background:#fff}
figcaption{font-size:13px;color:var(--muted);max-width:72ch}

.callout{border-left:3px solid var(--mva);background:var(--mva-soft);padding:13px 16px;
  border-radius:0 2px 2px 0;font-size:15px}
.callout strong{color:var(--mva)}
.callout.flag{border-left-color:var(--cut);background:var(--cut-soft)}
.callout.flag strong{color:var(--ink)}

.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.stat{border:1px solid var(--rule);border-radius:2px;padding:14px 16px;display:flex;
  flex-direction:column;gap:3px}
.stat .lab{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.stat .val{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:26px;font-weight:700;
  line-height:1.1;font-variant-numeric:tabular-nums}
.stat .note{font-size:13px;color:var(--muted)}
.stat.hi .val{color:var(--mva)}
.stat.ok .val{color:var(--good)}

ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:7px;max-width:70ch}
li::marker{color:var(--mva)}
code{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:.9em;
  background:var(--cut-soft);padding:1px 5px;border-radius:2px}
footer{color:var(--muted);font-size:13px;border-top:1px solid var(--rule);padding-top:16px}
</style>

<div class="wrap">

<header class="masthead">
  <div class="kicker">H&rarr;WW &middot; 2022postEE &middot; v11 6-class MVA</div>
  <h1>Kinematic cuts buy pre-selection S/&radic;B &mdash; they do not buy control-region purity</h1>
  <p class="standfirst">The MVA defines purer control regions <em>without</em> any kinematic cut, and already
  applies those cuts internally when it picks the signal region. The real lever on SR yield is
  the charm-tag working point.</p>
</header>

<section class="slide">
  <div class="slide-head"><span class="num">01</span>
    <div><h2>The tt&#772; control region is purer when the MVA defines it</h2>
    <p class="sub">Purity = fraction of events whose <em>true</em> process is tt&#772;. Pooled MC, 4,046,127 events, raw/unweighted.</p></div>
  </div>
  <div class="tbl-wrap"><table>
    <thead><tr><th>tt&#772; CR definition</th><th>N</th><th>tt&#772; purity</th><th>signal contam.</th><th>non-tt&#772; bkg</th></tr></thead>
    <tbody>
      <tr class="win"><td>argmax = tt&#772;, no kinematic cuts<span class="tag tag-mva">MVA</span></td>
        <td class="num-cell">1,565,461</td><td class="num-cell">87.86%</td><td class="num-cell">0.0004%</td><td class="num-cell">12.14%</td></tr>
      <tr><td>mT<sub>l2</sub>&gt;30 &amp; mT<sub>ll</sub>&le;60<span class="tag tag-cut">cut</span></td>
        <td class="num-cell">565,368</td><td class="num-cell">78.10%</td><td class="num-cell">0.0142%</td><td class="num-cell">21.89%</td></tr>
      <tr><td>m<sub>ll</sub>&gt;72<span class="tag tag-cut">cut</span></td>
        <td class="num-cell">2,375,781</td><td class="num-cell">83.04%</td><td class="num-cell">0.0009%</td><td class="num-cell">16.96%</td></tr>
      <tr><td>m<sub>ll</sub>&gt;72 &amp; mT<sub>l2</sub>&gt;30 &amp; mT<sub>ll</sub>&gt;60<span class="tag tag-cut">cut</span></td>
        <td class="num-cell">1,614,248</td><td class="num-cell">83.12%</td><td class="num-cell">0.0004%</td><td class="num-cell">16.88%</td></tr>
    </tbody>
  </table></div>
  <div class="callout"><strong>The MVA CR wins on both axes at once.</strong> It is the purest
  (87.9% vs 78.1% for the classic top CR) <em>and</em> 2.8&times; larger (1.57M vs 565k events).
  The cut-based top CR is the worst of the four &mdash; it is also the one carrying the most
  signal contamination, 35&times; that of the MVA CR.</div>
  <p>Composition of the MVA tt&#772; CR: tt&#772; 87.86%, single-top 9.38%, Higgs bkg 2.63%,
  diboson 0.12%, V+jets 0.01%, H+c <strong>7 events</strong>. Single-top is the only real
  contaminant, and it is physically tt&#772;-like &mdash; exactly what you want a tt&#772; CR to constrain.</p>
</section>

<section class="slide">
  <div class="slide-head"><span class="num">02</span>
    <div><h2>The MVA has already internalised the SR kinematic cuts</h2>
    <p class="sub">Fraction of events the network calls signal, across the (m<sub>ll</sub>, mT<sub>ll</sub>) plane. No kinematic cut is applied &mdash; the walls are the network's own.</p></div>
  </div>
  <figure>
    <img src="__IMG_SR__" alt="2D plane of dilepton mass versus transverse mass, coloured by the fraction of events the MVA assigns argmax=signal. A sharp boundary appears at mTll around 53 and mll around 100 with no cut applied.">
    <figcaption>argmax=signal support is bounded at mT<sub>ll</sub> &isin; [52.8, 202] and m<sub>ll</sub> &le; 100 &mdash;
    despite <code>mtll</code> not being an input feature.</figcaption>
  </figure>
  <div class="grid2">
    <div class="stat hi"><span class="lab">below the mT<sub>ll</sub> wall</span><span class="val">0.0098%</span>
      <span class="note">argmax=signal rate &mdash; 75 events out of 662,103</span></div>
    <div class="stat"><span class="lab">above the wall</span><span class="val">11.36%</span>
      <span class="note">argmax=signal rate, 1,160&times; higher</span></div>
  </div>
  <p>Imposing mT<sub>ll</sub>&gt;60 as an explicit pre-selection therefore removes events the network
  was <em>already</em> routing away from the signal class. It does not sharpen the SR; it only
  deletes the sidebands the network learned that boundary from.</p>
</section>

<section class="slide">
  <div class="slide-head"><span class="num">03</span>
    <div><h2>Same behaviour in the top CR &mdash; the separation is learned, not cut</h2>
    <p class="sub">The region the classic top CR carves out by hand is where the network sends almost nothing to the signal class.</p></div>
  </div>
  <figure>
    <img src="__IMG_TOP__" alt="2D plane for the top control region showing the argmax=signal fraction never exceeding 0.48 percent anywhere in the region.">
    <figcaption>Across the entire cut-defined top CR the argmax=signal fraction peaks at
    <strong>0.48%</strong>; only 66 of 565,368 events are called signal (0.0117%), max P(H+c)=0.358 &mdash;
    below the 0.5 needed to ever win argmax.</figcaption>
  </figure>
  <div class="callout"><strong>The cut is redundant with the classifier.</strong> The network
  independently recovers the same region because both follow the same physics &mdash; not because
  it was trained on the cut. <code>hww_MVA.yaml</code> has no mT/m<sub>ll</sub> cut in its base
  selection, and the labels are process truth.</div>
</section>

<section class="slide">
  <div class="slide-head"><span class="num">04</span>
    <div><h2>Cutting shrinks the training set the MVA needs</h2>
    <p class="sub">Efficiency of each kinematic cut, applied on top of the &ge;1 c-jet requirement.</p></div>
  </div>
  <div class="tbl-wrap"><table>
    <thead><tr><th>cut</th><th>&epsilon;<sub>S</sub></th><th>&epsilon;<sub>B</sub></th><th>S/&radic;B</th><th>gain</th></tr></thead>
    <tbody>
      <tr><td>mT<sub>ll</sub> &gt; 60</td><td class="num-cell">0.926</td><td class="num-cell">0.790</td><td class="num-cell">0.00091</td><td class="num-cell">1.04&times;</td></tr>
      <tr><td>mT<sub>l2</sub> &gt; 30</td><td class="num-cell">0.890</td><td class="num-cell">0.827</td><td class="num-cell">0.00086</td><td class="num-cell">0.98&times;</td></tr>
      <tr><td>m<sub>ll</sub> &le; 72</td><td class="num-cell">0.978</td><td class="num-cell">0.397</td><td class="num-cell">0.00136</td><td class="num-cell">1.55&times;</td></tr>
      <tr class="win"><td>all three (the SR)</td><td class="num-cell">0.845</td><td class="num-cell">0.271</td><td class="num-cell">0.00143</td><td class="num-cell">1.63&times;</td></tr>
    </tbody>
  </table></div>
  <p>The cuts <em>are</em> real at pre-selection: 1.63&times; on S/&radic;B, keeping 84.5% of signal
  while removing 73% of background. But that gain is a <em>counting</em> gain in a region the
  classifier already isolates &mdash; and it comes at the cost of 73% of the background events the
  network would otherwise learn the sidebands from.</p>
  <div class="callout flag"><strong>Cost, made concrete.</strong> Putting <code>m<sub>ll</sub>&le;72</code>
  into the base selection empties the high-m<sub>ll</sub> CR <em>by construction</em> &mdash; the
  region holds 2.38M events and 83.0% tt&#772; purity. You trade a well-populated constraint region
  for a 1.63&times; pre-selection number the MVA does not need.</div>
</section>

<section class="slide">
  <div class="slide-head"><span class="num">05</span>
    <div><h2>The real lever: the charm tag, not the kinematics</h2>
    <p class="sub">Per-process efficiency of the &ge;1 c-jet requirement at the medium PNet WP.</p></div>
  </div>
  <div class="grid2">
    <div class="stat hi"><span class="lab">c-jet eff &mdash; H+c signal</span><span class="val">23.1%</span>
      <span class="note">the medium WP discards 77% of signal</span></div>
    <div class="stat"><span class="lab">c-jet eff &mdash; ggH</span><span class="val">15.9%</span>
      <span class="note">the shape-degenerate competitor</span></div>
    <div class="stat ok"><span class="lab">enrichment H+c / ggH</span><span class="val">1.46&times;</span>
      <span class="note">ggH:H+c goes 681:1 &rarr; 467:1</span></div>
  </div>
  <p>Compare the two levers directly. The kinematic cuts keep <strong>84.5%</strong> of signal;
  the charm tag keeps <strong>23.1%</strong>. Signal acceptance is dominated by the c-jet
  requirement by a wide margin &mdash; so that is where extra SR events have to come from.</p>
  <p class="sub">Loose vs medium, measured offline on the untagged tree
  (5,619 H+c events, <code>hww_2dcat_nocjet</code>):</p>
  <div class="tbl-wrap"><table>
    <thead><tr><th>c-tag option</th><th>signal N</th><th>eff of &ge;1-jet base</th><th>vs medium</th></tr></thead>
    <tbody>
      <tr><td>medium (CvL&gt;0.160, CvB&gt;0.304)</td><td class="num-cell">3,244</td>
        <td class="num-cell">57.7%</td><td class="num-cell">1.00&times;</td></tr>
      <tr class="win"><td>loose (CvL&gt;0.054, CvB&gt;0.182)</td><td class="num-cell">5,337</td>
        <td class="num-cell">95.0%</td><td class="num-cell">1.65&times;</td></tr>
      <tr><td>no tag at all</td><td class="num-cell">5,619</td>
        <td class="num-cell">100.0%</td><td class="num-cell">1.73&times;</td></tr>
    </tbody>
  </table></div>
  <div class="callout"><strong>Loosening the WP recovers 1.65&times; the signal</strong> &mdash; most of
  what dropping the tag entirely would give (1.73&times;), while still rejecting light flavour.
  Compare the kinematic cuts: worth 1.63&times; on S/&radic;B, but paid for with the control regions.</div>
  <div class="callout"><strong>Recommendation.</strong> Keep the CRs cut-free and let the MVA define
  them. Spend the acceptance budget on the charm WP &mdash; loose (CvL&gt;0.054, CvB&gt;0.182) instead of
  medium (CvL&gt;0.160, CvB&gt;0.304) &mdash; because that is the cut actually removing 77% of the signal.</div>
</section>

<section class="slide">
  <div class="slide-head"><span class="num">06</span>
    <div><h2>The one thing this argument does not yet prove</h2>
    <p class="sub">What the c-tag comparison still has to establish.</p></div>
  </div>
  <ul>
    <li><strong>Loosening the WP admits more ggH too.</strong> CvL carries the H+c-vs-ggH separation
    (AUC 0.731); CvB does not (0.551 &asymp; coin flip). A looser WP moves down the CvL axis, so signal
    and ggH both rise &mdash; acceptance alone cannot decide it.</li>
    <li><strong>Purity is measured here, sensitivity is not.</strong> These are raw event counts;
    the limit also depends on how systematics act on a larger background.</li>
    <li><strong>Selection and SF boundaries do not coincide.</strong> The 2D SF scheme bins on
    <code>x=CvL/(CvL+CvB(1&minus;CvL))</code> and <code>y=1&minus;CvB</code>; a rectangular WP cut is a
    different shape in that plane. Already true in production, but worth stating.</li>
  </ul>
  <p><strong>All numbers here are 2022postEE</strong>, from the completed
  <code>hww_combine_fixed</code> MVA tree. The loose-WP row is measured offline on the untagged
  <code>hww_2dcat_nocjet</code> signal &mdash; a genuine like-for-like WP comparison, but
  signal-only, so it gives acceptance and <em>not</em> the ggH the looser WP also admits.
  <code>hww_ctag_compare</code> (2022preEE, 191 jobs running) supplies that missing half with
  full MC across all four categories on identical events.</p>
</section>

<footer>
  Numbers from 2022postEE, v11 6-class MVA <code>[hplusc, higgsbkg, tt, st, diboson, vjets]</code>,
  pooled MC 4,046,127 events, raw and unweighted. Purity = true-process fraction.
  Plots: <code>Projects/HToWW/argmax-kinematics-2026-08-07/</code>.
</footer>

</div>
"""

HTML = HTML.replace("__IMG_SR__", IMG_SR).replace("__IMG_TOP__", IMG_TOP)
out = Path("/home/cgupta/obsidian-notes/Projects/HToWW/argmax-kinematics-2026-08-07/kin-cuts-vs-mva-slides.html")
out.write_text(HTML)
print("wrote", out, len(HTML), "bytes")
