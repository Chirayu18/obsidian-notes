---
tags: [reference, presentation, decision]
status: active
date: 2026-11-13
source: laptop
---

# Include event-model ONNX export in the slides

Chirayu: **“Good to know and add to slides, the model is exported to onnx”**.

Add to the event-MVA/framework story in [[2026-11-12-november-update-slide-plan]]:

**“The trained PyTorch fold models are exported to ONNX for CPU inference. We compare ONNX and PyTorch probabilities on held-out events before registering the models for scoring.”**

Suggested flow: **PyTorch training → ONNX export and numerical agreement check → registered fold models → held-out event scoring → templates → Combine**.

Explain that export converts the inference representation; it does not retrain the model or define a new physics uncertainty. The current FoldModels scorer used by RUN and the TRAIN-to-card command consumes ONNX. A direct PyTorch scorer is possible but is not the currently implemented path. Do not claim a measured whole-framework speedup from export alone.

Keep completion status accurate when filling the slide. At06:11CET, A folds0–2 passed full held-out comparisons with max absolute probability differences1.52e−6,7.3e−7,1.34e−6 respectively (threshold1e−5); folds3–4 and registration were still pending in the last inspected log `~/bhive_prod_20261112_sol/A/export_20261113.log`. These are software agreement checks, not physics closure. Distinguish event-MVA export from the separate prompt-lepton ONNX models. Keeper owns the deck; no deck edited here.
