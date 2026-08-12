"""Retrieval evaluation: vault-search vs plain grep.

Ground truth is the note(s) a physicist would want for each question. Queries
are phrased the way you'd actually ask mid-session -- deliberately NOT using
the note's own distinctive vocabulary, since that is the case where lexical
search already wins and semantic search adds nothing.

Each query is tagged with how much lexical overlap it has with its target:
  paraphrase -- query shares no distinctive term with the target note
  partial    -- query shares one common term
  literal    -- query names the exact term the note uses
"""

QUERIES = [
    # --- paraphrase: the case semantic search exists for -------------------
    dict(
        q="why did the upper limit come out wrong because of event weights",
        gold=["Projects/HToWW/2026-06-23-automcstats-rootcause.md",
              "Projects/HToWW/2026-06-17-LIMIT-ISSUE.md"],
        kind="paraphrase",
    ),
    dict(
        q="the yield looked right but the uncertainty was inflated",
        gold=["Projects/HToWW/2026-06-23-automcstats-rootcause.md",
              "Projects/HToWW/2026-06-17-LIMIT-ISSUE.md"],
        kind="paraphrase",
    ),
    dict(
        q="normalisation was silently wrong because the totals came from the wrong place",
        gold=["Projects/HToWW/2026-07-31-sumw-normalization-trap.md"],
        kind="paraphrase",
    ),
    dict(
        q="grid jobs died because they asked for too little memory",
        gold=["Projects/HToWW/2026-07-08-hplusc-hplusb-crab-status.md"],
        kind="paraphrase",
    ),
    dict(
        q="how much signal survives the charm jet requirement",
        gold=["Projects/HToWW/cjet-acceptance-2026-08-08/2026-08-08-cjet-acceptance-study.md"],
        kind="paraphrase",
    ),
    dict(
        q="which knobs did we decide to treat as one nuisance instead of splitting",
        gold=["Projects/HToWW/2026-07-19-ctag2d-full-documentation.md",
              "Projects/HToWW/2026-07-24-systematics-master-list.md"],
        kind="paraphrase",
    ),
    dict(
        q="converting the trained model so it runs inside the framework",
        gold=["Projects/HToWW/2026-08-12-lepton-mva-onnx-conversion.md",
              "Projects/HToWW/leptonmva-2026-08-12/lepton-mva-onnx.md"],
        kind="paraphrase",
    ),
    dict(
        q="what order do I run things in to get from ntuples to a limit",
        gold=["Projects/HToWW/2026-07-24-run-analysis-steps.md"],
        kind="paraphrase",
    ),

    # --- partial: one shared common word -----------------------------------
    dict(
        q="trigger efficiency measurement",
        gold=["Projects/HToWW/2026-07-07-trigger-efficiency.md"],
        kind="partial",
    ),
    dict(
        q="cutflow numbers for 2022postEE",
        gold=["Projects/HToWW/2026-07-07-cutflow-2022postEE.md"],
        kind="partial",
    ),
    dict(
        q="control regions and the vjets degeneracy",
        gold=["Projects/HToWW/2026-08-12-CR-structure-and-vjets-degeneracy.md"],
        kind="partial",
    ),
    dict(
        q="nonprompt lepton diagnostic",
        gold=["Projects/HToWW/2026-08-12-lepton-mva-nonprompt-diagnostic.md"],
        kind="partial",
    ),

    # --- literal: exact term the note uses (grep should do fine) ------------
    dict(
        q="blacklist memoryless re-admits failed sites",
        gold=["Projects/HToWW/2026-08-12-master-task-list.md",
              "Projects/HToWW/2026-07-31-sumw-normalization-trap.md"],
        kind="literal",
    ),
    dict(
        q="autoMCStats",
        gold=["Projects/HToWW/2026-06-23-automcstats-rootcause.md",
              "Projects/HToWW/ProposedFix-Automcstats.md",
              "Projects/HToWW/2026-06-17-LIMIT-ISSUE.md"],
        kind="literal",
    ),
    dict(
        q="kappa hce loss math",
        gold=["Projects/HToWW/2026-07-01-kappa-hce-loss-math.md"],
        kind="literal",
    ),
    dict(
        q="systematics master list",
        gold=["Projects/HToWW/2026-07-24-systematics-master-list.md"],
        kind="literal",
    ),
]
