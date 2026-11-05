---
name: lxplus-coffea-env
description: How to get a working coffea/pandas python env on lxplus (b_hive micromamba env)
metadata: 
  node_type: memory
  type: reference
  originSessionId: bdb78af7-745b-4328-9066-cbbfcefa3761
---

To read higgscharm/coffea outputs (`.coffea` files, cutflows) on lxplus, activate the
`b_hive` micromamba env — it has coffea 0.7.22 + pandas. There is no dedicated higgscharm
coffea env; the plain condor `python3` won't have coffea.

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(micromamba shell hook --shell bash)"
micromamba activate b_hive
```

micromamba envs live under `/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/`
(`b_hive`, `fjbench`, `test`; `base` is the root). Only `b_hive` has coffea.

Note: over ssh in a non-interactive heredoc, use `micromamba shell hook` + `activate`
(not `micromamba run -n`, and not `micromamba activate` alone — the shell function isn't
loaded). Avoid f-strings inside `ssh '... << EOF'` heredocs — quoting gets mangled; write
the script to a /tmp file first, then run it. See [[Meta/claude-memory/_history/workflow/vault/lxplus-workflow|lxplus-workflow]].
