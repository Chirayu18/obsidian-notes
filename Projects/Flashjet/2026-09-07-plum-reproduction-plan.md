---
tags: [reference]
status: active
date: 2026-09-07
source: lxplus
---

# Can we get PLuM's gains? — reproduction plan

Question after reading [[2026-09-07-plum-paper-vs-our-result]]: our CA5 arm got
nothing from the same three Lund variables; PLuM reports +12% Hbb rejection. Can we
reproduce that by implementing what they actually did?

**Short answer: yes, and most of the work is already done.** The gap between our CA5
arm and PLuM is the *representation*, not the physics — and the physics side is
already implemented and FastJet-validated in flashjet.

## What separates our CA5 arm from PLuM

| | our CA5 | PLuM |
|---|---|---|
| representation | 5 numbers per **particle** | up to 48 **splitting tokens** |
| ordering | **C/A** | **kT** |
| variables | ln kT, ln z, ln dR, depth, has_bp | log kT, log dR, log z |
| embedding | concatenated to 23 cpf features | MLP 3→64→256→128 |
| attends? | no — a feature of a leaf | yes — full cross-attention |
| task | 10-class | **binary** |
| seeds | 1 | 10 (top-5 quoted) |

Their C/A ablation found no gain, matching us. **The two changes that plausibly
matter are kT ordering and the token representation.**

## What already exists (verified in the code, 2026-09-07)

- **`lund_coordinates_from_history(...)`** in
  `/eos/home-c/cgupta/flashjet/FlastJetDemo/src/flashjet/history.py:313` already
  returns **`(B, J, S, 6)`** — per-jet, per-**splitting**, in de-clustering order
  (slot 0 = widest split), zero-padded past each jet's split count. Channels:
  `z, dR, kt, ln(1/dR), ln(kt), d`. **This is exactly PLuM's token input**, already
  cross-checked against FastJet in `tests/test_substructure.py`.
- **kT clustering is supported**: `api.py:190` `cluster(..., algorithm=...)` accepts
  `'antikt' | 'kt' | 'cambridge'` (`api.py:199`). We only ever used `cambridge`.
- ParT's forward pass (`utils/models/particletransformer2.py:730`) has a clean
  injection point — see below.

**So there is no new physics code to write.** We need a model change and a config.

## The model change

In `ParticleTransformer2.forward` (particletransformer2.py:~743):

```python
enc = self.InputProcess(cpf, npf, vtx)          # (B, N, embed_dim)
```

Add after this:
1. `lund = lund_embed(lund_feats)` — MLP 3→64→256→128 on `[ln kt, ln 1/dR, ln z]`,
   giving `(B, M, embed_dim)` with M=48.
2. `enc = torch.cat([enc, lund], dim=1)` — tokens joined to particles.
3. Extend `padding_mask` by the splitting-validity mask (S < actual split count).

**The one real subtlety: `attn_mask`.** ParT's `pair_embed` produces an
`(B, heads, N, N)` bias from the particle 4-vectors, added to the attention matrix.
With M extra tokens the attention matrix becomes `(N+M, N+M)`, so the bias must be
padded. PLuM's stated choice is *no prior bias* on the splitting rows/columns:

> "the model learns to weigh Lund-plane-derived tokens purely based on learned
> self-attention dynamics"

So **zero-pad `attn_mask` to (N+M, N+M)** — zeros in the splitting block, not
`-inf`. Getting this wrong (padding with the `finfo.min` used for real padding)
silently masks the new tokens out entirely and reproduces the baseline exactly —
which would look like "no gain" and be a bug, not a result.

Param cost should land near their 2.14M → 2.19M.

## Plan

**Phase 1 — sanity (cheap, do first).** Before any training: confirm the kT-ordered
Lund tokens carry Hbb-vs-QCD information *at all*, with a small probe on cached
features. Reuses the probe discipline from [[2026-09-04-subjet-verdict]].
**Note the prior:** probe signal has **failed to predict trainable gain three times**
in this study (share_bp AUC 0.87 → nothing; DeepSets R²=0.232 → nothing; subjet
probe +0.0077 → parity). Treat a positive probe as *necessary, not sufficient*.

**Phase 2 — implement.** `utils/flashjet_lund_tokens.py` (kT clustering, top-48
splittings by de-clustering order, 3 channels), the forward-pass change above gated
on a config flag, and `config/jet_class_plum.yml`. Verify: input token count is
N+48, the attn_mask block is zeros not -inf, and one training step runs.

**Phase 3 — train, matching their setup where it matters.** Their gains are in
**binary** mode; our infrastructure is 10-class. Run **binary Hbb-vs-QCD** first — it
is their strongest channel, the cheapest to train, and the most direct test of the
claim. Then 10-class if binary reproduces.

**Phase 4 — seeds.** At least 3, ideally 5. The effect size at stake (~12% rejection
at 50% eff) is well above our noise floor, so 3 seeds should resolve it — but
**quote the full-sample mean and spread, not a top-k subsample**, which is the
methodological gap in their Table I.

## What to expect, stated in advance

Their gain is attributed to **b-lifetime / displaced-hadron** patterns, not branching
hierarchy — and obtained **without secondary-vertex inputs** in Delphes. Our JetClass
cpf features **do include `d0val`, `d0err`, `dzval`, `dzerr`** (see the
`cpf_candidates` list in `particletransformer2.py`), i.e. per-particle impact
parameters. **If their gain is really an SV proxy, we may reproduce it only partly,
because our baseline already sees track displacement.** Writing this down now so the
result is interpretable either way:

- **Reproduce ~+12% Hbb** ⇒ the token representation is what matters; our CA5 null
  was a representation failure, not a redundancy result. **This would weaken the
  arity argument** and is the outcome that changes the talk most.
- **Get little or nothing** ⇒ consistent with the SV-proxy reading, and the arity
  argument stands. Then the honest talk statement is that the gain depends on the
  baseline's access to displacement information.

**Prior: ~50%** that we see a clear (>5%) Hbb rejection gain in binary mode. Genuinely
uncertain — their result is a real measurement on the same dataset, but the mechanism
they describe is one our inputs partly cover.

## Cost

Phase 1–2 are ~a day of work with no new physics code. Phase 3 binary training is
much cheaper than our 980k 10-class runs. The expensive part is Phase 4 (seeds).

## Do not

Reuse `_at980k` checkpoints — this is a new architecture and must train from scratch.
Quote a top-k-of-n subsample as a mean.
