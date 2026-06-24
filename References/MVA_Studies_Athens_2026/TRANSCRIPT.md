# Transcript — MVA studies for $H+c$ ($H\to WW\to 2\ell2\nu$) at Run 3
**Speaker: Chirayu Gupta · Higgs–Charm Workshop, Athens 2026 · ~10 min**

Framing: Thomas has already covered the analysis (strategy, selection, control regions,
input features, baseline MVA). Anything he covered, I **flash through quickly** — this talk
is the deep-dive into the MVA *model*: the κ-HCE loss, what it buys us, and the results.

Target pace ≈ 140 wpm. Bracketed `[~Xs]` are running cues; aim to land the Combine slide
by ~8:30 so takeaways breathe.

---

### Title  [~0:00–0:20]
Thanks Thomas. As he said at the end of his talk, I'll now go one level deeper into the
MVA itself. So this is the model side of the Run 3 $H+c$ analysis in the $H\to WW$ to
two-lepton-two-neutrino channel — specifically the multiclass classifier and a custom loss
we call the κ-HCE discriminant.

### Slide 1 — Training Dataset  [~0:20–1:10]  *(flash)*
Quick recap of what goes in. We train a multiclass network to separate $H+c$ from the
dominant backgrounds, following the Run 2 analysis. The classes are here: signal $H+c$, a
grouped Higgs-background class, then $t\bar t$, single top, diboson and V+jets. About four
million events, split roughly 80/20 train/test. Because $H+c$ and $H+b$ are so scarce, we
borrow extra signal events from 2022preEE and 2023preBPix just for training — but every
number, plot and limit you'll see uses **2022postEE only**, 26.7 inverse femtobarns. Class
imbalance is handled with inverse-frequency weights in the cross-entropy. That's the setup —
let's get to the model.

### Slide 2 — MVA Input Features  [~1:10–1:35]  *(flash)*
These are the 17 inputs — kinematics, transverse masses, angular separations, charm tagging
— inherited from Run 2. Thomas already showed the feature-importance study behind this list,
so I'll move straight on.

### Slide 3 — Model & Previous Attempts (v10, v11)  [~1:35–2:40]
Now the interesting part — and the problem that motivates everything that follows. The
architecture is a simple MLP, three hidden layers, softmax output. We tried two baselines.
**v10** uses the full 13 fine classes with plain cross-entropy — and it **fails**: the fine
Higgs sub-modes are kinematically almost identical, so forcing a 13-way split confuses the
network and the $H+c$ output never really gets learned — AUC about 0.51, no better than
chance. **v11** merges the Higgs modes down to 6 classes — that **works**, AUC 0.93 against
all backgrounds, and you can see the signal separating in the score plot on the right. But
it throws away the per-process information we'd like to keep for the control regions. So:
plain CE either fails or costs us information. That's the gap we wanted to close.

### Slide 4 — Motivation for a κ-HCE Loss  [~2:40–3:45]
The key insight is that we want a single loss doing three things at once. One: learn the
**global** separation — Higgs versus top versus diboson versus V+jets. Two: learn the
**fine-grained** separation *inside* the signal-like group — $H+c$ against the other Higgs
modes. And three: directly optimise the **discriminant** we actually cut on. That
discriminant is $D_\kappa$ — here on the slide,
$D_\kappa = P_\text{sig}/(P_\text{sig}+\sum_j \kappa_j P_j)$. Let me define **κ**, because it
runs through the whole talk: for each background class $j$ there is one number $\kappa_j$ — a
weight, between 0 and 1 — that sets how strongly that background counts in the denominator,
i.e.\ how hard we suppress it. A background that looks like signal gets a **high κ**, close
to 1, so we don't over-fight it; a background that's clearly different gets a **low κ**, near
0, so it's pushed away. So κ is just a per-background suppression weight — and the nice part,
two slides on, is that we don't set it by hand, the network learns it. Train with all this
and we get the model I'll call **v32**.

### Slide 5 — κ-HCE Loss: the three ideas  [~3:45–4:40]
Concretely the loss is three terms. The **group term** learns the broad picture first. The
**fine term** zooms in on the hardest case — within the signal-like group, it gives extra
attention to the processes that look most like $H+c$. And the **discriminant term**
optimises $D_\kappa$ directly, which indirectly optimises signal-over-signal-plus-background.
The plot on the right is where κ comes from: it's the cosine similarity between each class
and the signal, as a function of training epoch. The network is *learning* which classes are
signal-like — and that learned similarity is exactly what sets κ, through a sigmoid. So κ is
not a free parameter; it falls straight out of training.

### Slide 6 — Learned Cosine Similarity  [~4:40–5:30]
Here's that similarity made concrete. On the left, the cosine of each class's weight vector
with the $H+c$ one — a number the MVA learns, not something we put in by hand. ggH, $H+b$,
VBF, V+jets come out positive, signal-like. Diboson is roughly orthogonal. $t\bar t$ and
single top are strongly negative — the genuine backgrounds. On the right is the full
13-by-13 matrix; that structure is what the dynamic grouping and the κ weights are built
from. So κ isn't a free knob — it's pinned to a physically meaningful, learned quantity.

### Slide 7 — α-weighted Feature Importance  [~5:30–6:05]  *(flash-ish)*
Thomas introduced this method, so briefly: it's the α-weighted, integrated-gradient-style
importance per feature and class. The takeaway is the ranking on the right — dilepton mass,
the leading-lepton transverse mass, missing $p_T$, number of secondary vertices, and the
ParticleNet charm discriminants are doing the heavy lifting. No surprises, but it confirms
the network leans on the physically sensible variables.

### Slide 8 — ROC Curves, v11 vs v32  [~6:05–6:55]
Now does the κ-HCE loss actually help? Yes. Left panel, $H+c$ against all backgrounds: AUC
goes from 0.928 with v11 to **0.954** with v32. Right panel, against $t\bar t$ specifically —
our worst background — 0.937 to **0.968**. Top-left corner is best, and v32 is above v11
everywhere. So we keep the fine-grained classes *and* improve discrimination — that's the
"best of both worlds" we were after.

### Slide 9 — $D_\kappa$ Discriminant & κ Optimisation  [~6:55–7:25]
This is the discriminant we feed to the fit. On the left, the v32 score after κ optimisation
— signal, overlaid and scaled, separates cleanly to high $D_\kappa$. On top of the κ's the
network learns, we then *tune* them with differential evolution to maximise the
yield-weighted significance on the validation set. The backgrounds with the largest κ —
V+jets, WH, diboson, ggH — are exactly the ones the network most wants to suppress, which is
a nice sanity check that κ is doing what we said.

### Slide 10 — $S/\sqrt{B}$ vs Signal Efficiency  [~7:25–8:00]
Here's what that tuning buys us, with two messages. First, the red curve — the optimised
$D_\kappa$ discriminant — lifts the peak significance, $S/\sqrt{B}$, by about **+10%** over
the blue curve, which is just the raw $P(H+c)$ node. So optimising the κ's is worth a real
10%. Second, and bigger: compared to the Run 2 cut-based selection at the same luminosity,
the MVA gives roughly a **five-times higher** $S/\sqrt{B}$. The little table makes it
concrete — Run 2 cut-based is $6.6\times10^{-4}$, the raw node $3.2\times10^{-3}$, the
optimised $D_\kappa$ $3.5\times10^{-3}$. The bands are statistical.

### Slide 11 — Grouped Confusion Matrix  [~8:00–8:35]
Now a reality check on what the classifier actually does on yields. Recall is good — about
**75%** of true $H+c$ events are kept; that's the left panel. But precision, on the right, is
cross-section-weighted, and there it's brutal: the $H+c$-predicted column is roughly
two-thirds $t\bar t$ plus ttH, so on real data a tagged event is almost never truly signal.
That's not a model failure — it's just the tiny signal-to-background of this channel, full
stop. The classifier is doing its job; the physics is simply hard.

### Slide 12 — Process Yields per Channel  [~8:35–9:05]
And this is how the multiclass output gets used downstream. Events are routed into one of six
channels — the $H+c$ signal region plus five control regions — by taking the argmax of
$P(\text{class})$ over its prior. The payoff is on the right: the $t\bar t$ control region
comes out about **94% pure**, which is exactly the clean handle the simultaneous fit needs to
constrain the dominant background. The signal and Higgs-background yields are magnified by
large factors just to be visible against the $\sim$$10^4$ $t\bar t$ events.

### Slide 13 — Combine, statistical sensitivity  [~9:05–9:35]
Putting it in Combine, stat-only so we isolate the classifier's raw power: v32 gives the
best floor, an expected limit of **584**, about 1.3 times tighter than v11. And scaled to our
luminosity, both our floors already beat the Run 2 stat-only expectation. So the κ-HCE model
genuinely separates the signal better. The honest caveat — and it's in backup — is that the
*full* limit, with systematics, is dominated by MC statistics, not by the classifier. That's
the next thing to fix, not a separation problem.

### Slide 14 — Key Takeaways  [~9:35–10:00]
To wrap up. One: plain cross-entropy on 13 fine classes fails — the degenerate Higgs modes
break it. Two: the κ-HCE loss gives us both the fine-grained classes *and* the best $H+c$
discrimination, v32. Three: the discriminant-aware term optimises what we actually cut on,
and the learned cosine similarity gives a physically meaningful κ per background. Four: charm
tagging, dilepton mass, leading-lepton transverse mass and nSV are the dominant features.
And five: v32 has the best statistical floor. The table summarises it — 0.51, to 0.928, to
0.954. Happy to take questions, and there's plenty of detail in backup.  [~10:00]

---

## Timing safety valves
- **Running long?** Compress Slide 5 (just name the three terms, point at the plot) and skip
  the feature-importance ranking read-out on Slide 7 — those recover ~45 s.
- **Running short?** Expand Slide 9 (walk through the κ values) and the precision argument on
  Slide 11 (confusion matrix).
- **If the $S/\sqrt{B}$ and Combine slides feel redundant under time pressure**, Slide 10 can
  be a 15 s "+10% from κ-tuning, 5× over Run 2 cut-based" and move on.
- **If asked "why not just use v11?"** — v11 loses per-process info needed for the CRs and is
  0.026 lower in AUC; κ-HCE keeps both.
- **If asked about the full limit** — go to the Combine-full and impacts backup slides:
  ~80% systematics-limited, dominated by `prop_binSR_hplusc_*` (autoMCStats), reducible via
  cross-era template averaging.
