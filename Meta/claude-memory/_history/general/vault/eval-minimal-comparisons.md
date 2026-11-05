---
name: eval-minimal-comparisons
description: "Combine-agent evals — run the baseline first, add comparison axes one at a time and on few questions; never launch a full factorial matrix"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4802996e-67e1-456e-b436-0c4812daa983
  modified: 2026-10-21T15:42:21.111Z
---

Keep eval runs small and staged. Baseline first (current client, web fetch ON, all merged questions, 3 repeats); only after looking at those results add another axis (web on/off). Client comparisons (opencode vs omp) need just 2-3 questions.

**Why:** user stopped a 240-run matrix on 2026-10-21: "Noo not soo many comparisons ... dont check web on and off, we will test that only after seeing results with web fetch on, and opencode and omp comparison can be done with just 2-3 questions". Quota on aigw is shared.

**How to apply:** propose the smallest run set that answers the current question, state the run count, then run. Related: [[Meta/claude-memory/_history/general/vault/ask-before-aigw-spend|ask-before-aigw-spend]], [[Meta/claude-memory/_history/slides/vault/acat2027-combine-agent-talk|acat2027-combine-agent-talk]].
