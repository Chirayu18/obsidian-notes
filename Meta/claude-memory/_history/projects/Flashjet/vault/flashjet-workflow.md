---
name: flashjet-workflow
description: "flashjet validation work — live paths, condor pattern, and where the verdicts are written up"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8cb963cf-d304-4ee6-8f09-c79b0129a6f5
---

Flashjet (GPU jet clustering, with Alexandre De Moor) — as of 2026-07-17:

- Repo: `/eos/home-c/cgupta/flashjet/FlastJetDemo` branch `benchmarking` (substructure F1/F2/F3 pushed as `2e912ef`).
- Plot scripts + npz diagnostics: `/eos/home-c/cgupta/flashjet/plots/2026-07-13-substructure/`; data files in `/eos/home-c/cgupta/flashjet/data/` (QCD + TTTo2L2Nu UL18 JMENano 150X, TTto4Q Run3 2024 JMENanoV15 — all have `PFCand`/`FatJetPFCand`, PUPPI-weighted; these are the ONLY JMENano-with-constituents datasets found).
- Long jobs: HTCondor from `/afs/cern.ch/user/c/cgupta/flashjet_condor/` (AFS — /eos submit paths rejected); executable exports `MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba` and `MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba` (NOT ~/micromamba — that prefix has no b_hive), then `$MAMBA_EXE run -n b_hive`; flashjet is installed editable there (torch 2.5.1, triton 3.1.0). The laptop has no flashjet/torch — run everything on lxplus.
- Deck: vault `Projects/Flashjet/presentation/flashjet-substructure.md` (Marp → PDF via npx marp-cli, node in `~/.nvm/versions/node/v24.10.0/bin`).
- Key physics verdicts (details in vault [[2026-07-13-cms-validation]] + [[2026-07-17-msd-outlier-anatomy]] + Status.md): compare RAW-to-RAW (undo JECs via rawFactor), groom the big-R C/A reclustering (not the anti-kt tree), and the residual m_SD tail is a NanoAOD input property (constituent-table ~0.1 GeV floor + reduced-mantissa storage), NOT an algorithm error.

**Why:** these were each multi-hour discoveries; re-deriving them wastes a session.
**How to apply:** start any flashjet comparison from `make_compare_plots.py`/`exact_match2.py` patterns; never re-run FastJet (compare against stored branches — user's explicit instruction).

- 2026-09-25: flashjet `history._pseudojet_p4` had a padding bug (the last real particle was zeroed in padded jets). It is fixed ONLY on branch `lmkt` (`46e566d`). b-hive imports the FlastJetDemo working tree, which is now on `lmkt`, so new runs are not bit-identical to the old arms C/D/F/subjet. Vault: 2026-09-25-flashjet-pseudojet-p4-padding-bug.
- Current direction (2026-09-25): recursive merge-embedding ParT (vault 2026-09-25-recursive-tree-network-plan). Module at b-hive `utils/flashjet_tree_embed.py`, tests at lmkt/test_tree_embed.py.
