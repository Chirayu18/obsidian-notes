#!/usr/bin/env python3
"""Measure how much of ParT's attention lands on the 48 Lund tokens, per class,
across training checkpoints.

THE QUESTION (Sitian, ML4Jets 2026): PLuM works as an INDUCTIVE BIAS -- it
re-directs attention toward the Lund plane. If so, the Lund attention share
should be HIGH EARLY and DECAY as the baseline learns the same allocation from
four-vectors alone. That decay is the mechanism behind our measured gain decay.
A FLAT share falsifies the mechanism regardless of per-class ranking.

WHAT IS MEASURED
Two distinct things, because they answer different questions:

1. CLS share  -- in the 2 class-attention blocks the CLS token attends over
   [cls | 128 particles | 48 lund]. The fraction of that attention mass landing
   on the lund block is the jet-level decision's reliance on Lund tokens.
   THIS IS THE PRIMARY NUMBER: it is what "the tagger uses the Lund plane" means.

2. Self share -- in the 8 encoder blocks every token attends over
   [128 particles | 48 lund]. Averaged over particle queries only, this is how
   much particle representations are shaped by Lund tokens.

BASELINE FOR "HIGH": with 48 lund + N_valid particle tokens, a model that
attended UNIFORMLY would put 48/(48+N_valid) of its mass on lund. Every share
is reported against that null, as a ratio. A share above 1.0 means lund tokens
are attended MORE than their token count warrants. Without this the raw
fraction is uninterpretable -- 27% sounds large but is exactly uniform at N=128.

MASKING: padded particles and invalid lund slots are excluded from both the
numerator and the uniform null, per jet, so jets with few constituents do not
bias the share.
"""
import os, sys, glob, time, functools, json
import numpy as np, torch, lz4.frame
print = functools.partial(print, flush=True)

BH = "/eos/user/c/cgupta/flashjet/b-hive"
os.environ.setdefault("B_HIVE_DIR", BH)
os.environ.setdefault("FLASHJET_SRC", "/eos/home-c/cgupta/flashjet/FlastJetDemo/src")
sys.path.insert(0, BH); os.chdir(BH)

CFG, VER, MODEL = "jet_class_plum", "b_hive_paper_plum_1", "ParticleTransformer_PLuM_JetClass"
ITERS = [int(a) for a in (sys.argv[1:] or ["40000","100000","300000","1000000"])]
NJETS = int(os.environ.get("NJETS", "20000"))     # per checkpoint, across shards
OUT   = "/eos/user/c/cgupta/flashjet/lund_attn"
# GPU and CPU runs can be in flight at once; keep their results apart so a
# cheaper/noisier CPU run cannot clobber the full-statistics GPU one.
TAG   = os.environ.get("LUND_OUT_TAG", "")
JSON  = OUT + "/lund_attention" + (("_" + TAG) if TAG else "") + ".json"
os.makedirs(OUT, exist_ok=True)

CLASSES = ["TTBarLep","TTBar","HToWW2Q1L","HToWW4Q","HToBB","HToCC","HToGG",
           "ZJetsToNuNu","ZToQQ","WToQQ"]

from utils.models.models import BTaggingModels
from utils.config.config_loader import ConfigLoader
cfg = ConfigLoader.load_config(CFG)
dev = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", dev, torch.cuda.get_device_name(0) if dev == "cuda" else "")

# ---------------------------------------------------------------- hooks
# nn.MultiheadAttention returns weights only when need_weights=True, which the
# model never sets. Rather than patch the model source (it is the trained
# artefact -- editing it risks changing what we measure), wrap each block's
# .attn in a shim that forces need_weights and stashes the averaged weights.
STASH = {}
class AttnProbe(torch.nn.Module):
    def __init__(self, mha, name):
        super().__init__(); self.mha = mha; self.name = name
    def forward(self, q, k, v, **kw):
        kw = dict(kw); kw["need_weights"] = True; kw["average_attn_weights"] = True
        out, w = self.mha(q, k, v, **kw)
        STASH[self.name] = w.detach()          # (B, Lq, Lk), head-averaged
        return out, w

def load(it):
    model = BTaggingModels(MODEL, cfg)
    ck = (f"{BH}/output/TrainingTask/{CFG}/JetClass_train_100_mod/{VER}/{MODEL}"
          f"/epochs_0/nominal/model_{it}.pt")
    sd = torch.load(ck, map_location="cpu", weights_only=False)["model_state_dict"]
    sd = {(k[10:] if k.startswith("_orig_mod.") else k): v for k, v in sd.items()}
    miss, unexp = model.load_state_dict(sd, strict=False)
    assert not [m for m in miss if "lund" in m], f"lund weights missing: {miss}"
    print(f"  loaded model_{it}.pt  missing={len(miss)} unexpected={len(unexp)}")
    model.to(dev).eval()
    core = model.model if hasattr(model, "model") else model
    for i, b in enumerate(core.blocks):
        b.attn = AttnProbe(b.attn, f"enc{i}")
    for i, b in enumerate(core.cls_blocks):
        b.attn = AttnProbe(b.attn, f"cls{i}")
    return model, core

NUM_ELE = 10
files = sorted(glob.glob(f"{BH}/output/DatasetConstructorTask/{CFG}/JetClass_test_mod/file_*.lz4"))
print("test shards:", len(files))

def shard(f):
    with lz4.frame.open(f, mode="r") as fh: raw = fh.read()
    s = np.frombuffer(raw, dtype=np.float32).copy(); s = s[2:].reshape(-1, int(s[1]), order="C")
    labels = s[:, -(NUM_ELE+1):-1]; truth = labels.argmax(1).astype(np.int8)
    feats = s[:, :-(NUM_ELE+2)]
    return feats, truth

BS = 256
results = {}
for it in ITERS:
    print(f"\n=== checkpoint {it} ===")
    model, core = load(it)
    M = core.m_splits
    # accumulators, per class
    acc = {c: dict(n=0, cls_num=0.0, cls_unif=0.0, self_num=0.0, self_unif=0.0,
                   nvalid=0.0, nlund=0.0) for c in range(10)}
    seen = 0; t0 = time.time()
    # Test shards are grouped by class, so reading them in order fills the
    # budget with one class. Take a few batches from EVERY shard instead.
    per_shard = max(1, NJETS // max(len(files), 1))
    for f in files:
        if seen >= NJETS: break
        feats, truth = shard(f)
        took = 0
        for b in range(0, len(truth), BS):
            if seen >= NJETS or took >= per_shard: break
            flat = torch.from_numpy(np.ascontiguousarray(feats[b:b+BS])).to(dev)
            tb = truth[b:b+BS]
            with torch.no_grad():
                inpt, _ = model.get_inpt(flat, device=dev)
                STASH.clear()
                _ = model(inpt)
                # reconstruct the masks the forward pass used
                cpf_features = inpt[1]
                cpf_4v = cpf_features[:, :, -4:]
                pad = torch.eq(cpf_4v[:, :, 0], 0.0)        # (B,P) True=pad
                P = pad.shape[1]
                nvalid = (~pad).sum(1).float()              # (B,)

                # lund validity: recompute exactly as the model does
                from utils.flashjet_lund_tokens import lund_split_tokens
                _, lvalid = lund_split_tokens(
                    cpf_4v, ~pad, R=core.lund_R,
                    algorithm=core.lund_algorithm, m_splits=M)
                nlund = lvalid.sum(1).float()               # (B,)

                # ---- CLS blocks: query is the single cls token,
                #      keys are [cls | P particles | M lund]
                cls_share = torch.zeros_like(nvalid)
                ncls = 0
                for k, w in STASH.items():
                    if not k.startswith("cls"): continue
                    # w: (B, 1, 1+P+M)
                    wl = w[:, 0, 1+P:].sum(1)               # mass on lund keys
                    cls_share += wl; ncls += 1
                cls_share /= max(ncls, 1)

                # ---- encoder blocks: average over PARTICLE queries only
                self_share = torch.zeros_like(nvalid); nenc = 0
                for k, w in STASH.items():
                    if not k.startswith("enc"): continue
                    # w: (B, P+M, P+M); rows = queries
                    wl = w[:, :P, P:].sum(-1)               # (B,P) mass on lund
                    qm = (~pad).float()
                    self_share += (wl * qm).sum(1) / qm.sum(1).clamp(min=1)
                    nenc += 1
                self_share /= max(nenc, 1)

                # uniform null: lund fraction of the attendable token count
                unif_cls  = nlund / (1.0 + nvalid + nlund)
                unif_self = nlund / (nvalid + nlund)

            for c in range(10):
                m = (tb == c)
                if not m.any(): continue
                mi = torch.from_numpy(np.where(m)[0]).to(dev)
                a = acc[c]
                a["n"]         += int(m.sum())
                a["cls_num"]   += float(cls_share[mi].sum())
                a["cls_unif"]  += float(unif_cls[mi].sum())
                a["self_num"]  += float(self_share[mi].sum())
                a["self_unif"] += float(unif_self[mi].sum())
                a["nvalid"]    += float(nvalid[mi].sum())
                a["nlund"]     += float(nlund[mi].sum())
            seen += len(tb); took += len(tb)
        del feats, truth
    print(f"  {seen} jets in {(time.time()-t0)/60:.1f} min")
    row = {}
    for c in range(10):
        a = acc[c]
        if a["n"] == 0: continue
        n = a["n"]
        row[CLASSES[c]] = dict(
            n=n,
            cls_share=a["cls_num"]/n,   cls_unif=a["cls_unif"]/n,
            self_share=a["self_num"]/n, self_unif=a["self_unif"]/n,
            cls_ratio=(a["cls_num"]/n)/(a["cls_unif"]/n),
            self_ratio=(a["self_num"]/n)/(a["self_unif"]/n),
            nvalid=a["nvalid"]/n, nlund=a["nlund"]/n)
    results[it] = row
    for cname, r in row.items():
        print(f"  {cname:12s} n={r['n']:6d}  CLS {r['cls_share']*100:6.2f}% "
              f"(unif {r['cls_unif']*100:5.2f}%, ratio {r['cls_ratio']:5.2f})   "
              f"self {r['self_share']*100:6.2f}% (ratio {r['self_ratio']:5.2f})")
    del model, core
    if dev == "cuda": torch.cuda.empty_cache()

with open(JSON, "w") as fh:
    json.dump(results, fh, indent=1)
print("\nwrote", JSON)
