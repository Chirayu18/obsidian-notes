#!/usr/bin/env python3
"""Are the Lund tokens LOAD-BEARING? Ablate them and measure the accuracy drop.

WHY THIS AND NOT ATTENTION SHARE: attention share says where attention goes, not
whether the model depends on it. A token can receive little attention and still
carry the decision (attention is a weighted average -- a small weight on a large,
distinctive value vector still moves the output). measure_lund_attention.py found
the Lund tokens are attended 2-5x LESS than chance yet the PLuM arm gains early;
those are only compatible if attention share is the wrong proxy for importance.
This measures importance directly.

THE ABLATION: mask the 48 Lund tokens out of attention entirely (set their
padding_mask entries True) and re-run the SAME checkpoint on the SAME jets. The
model then sees exactly the baseline's 128 particle tokens. The accuracy drop is
how much the trained model was relying on them.

Read against two references, because the drop alone is not interpretable:
  * PLuM intact vs PLuM ablated  -- what the tokens are worth to this model
  * PLuM ablated vs the BASELINE arm -- if ablated PLuM ~ baseline, the tokens
    are the ONLY thing the two arms disagree about, as intended.

Predicted by the redundancy account (rising self-attention, falling CLS
attention): the drop should be LARGE early (40k) and SMALL at 1M, because by then
the encoder has folded the information into the particle representations and the
tokens are no longer the only route to it.
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
NJETS = int(os.environ.get("NJETS", "20000"))
OUT   = "/eos/user/c/cgupta/flashjet/lund_attn"
TAG   = os.environ.get("LUND_OUT_TAG", "")
JSON  = OUT + "/lund_ablation" + (("_" + TAG) if TAG else "") + ".json"
os.makedirs(OUT, exist_ok=True)

CLASSES = ["TTBarLep","TTBar","HToWW2Q1L","HToWW4Q","HToBB","HToCC","HToGG",
           "ZJetsToNuNu","ZToQQ","WToQQ"]

from utils.models.models import BTaggingModels
from utils.config.config_loader import ConfigLoader
cfg = ConfigLoader.load_config(CFG)
dev = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", dev, torch.cuda.get_device_name(0) if dev == "cuda" else "")

ABLATE = {"on": False}

def patch(core):
    """Wrap forward so the lund tokens can be masked out without touching weights.

    The model builds padding_mask = cat(particle_pad, ~lvalid) internally, so the
    cleanest hook is on the Block: mark the trailing M entries as padding. Every
    block (encoder and class-attention) receives padding_mask, so one wrapper on
    each covers the whole forward pass.
    """
    M = core.m_splits
    for blist in (core.blocks, core.cls_blocks):
        for b in blist:
            if getattr(b, "_abl_wrapped", False): continue
            orig = b.forward
            def fwd(x, x_cls=None, padding_mask=None, attn_mask=None, _o=orig, _M=M):
                if ABLATE["on"] and padding_mask is not None:
                    padding_mask = padding_mask.clone()
                    padding_mask[:, -_M:] = True      # lund tokens -> padding
                return _o(x, x_cls=x_cls, padding_mask=padding_mask, attn_mask=attn_mask)
            b.forward = fwd; b._abl_wrapped = True

def load(it):
    model = BTaggingModels(MODEL, cfg)
    ck = (f"{BH}/output/TrainingTask/{CFG}/JetClass_train_100_mod/{VER}/{MODEL}"
          f"/epochs_0/nominal/model_{it}.pt")
    sd = torch.load(ck, map_location="cpu", weights_only=False)["model_state_dict"]
    sd = {(k[10:] if k.startswith("_orig_mod.") else k): v for k, v in sd.items()}
    miss, unexp = model.load_state_dict(sd, strict=False)
    print(f"  loaded model_{it}.pt  missing={len(miss)} unexpected={len(unexp)}")
    model.to(dev).eval()
    core = model.model if hasattr(model, "model") else model
    patch(core)
    return model

NUM_ELE = 10
files = sorted(glob.glob(f"{BH}/output/DatasetConstructorTask/{CFG}/JetClass_test_mod/file_*.lz4"))
BS = 256
rng = np.random.default_rng(12345)

def shard(f):
    with lz4.frame.open(f, mode="r") as fh: raw = fh.read()
    s = np.frombuffer(raw, dtype=np.float32).copy(); s = s[2:].reshape(-1, int(s[1]), order="C")
    labels = s[:, -(NUM_ELE+1):-1]; truth = labels.argmax(1).astype(np.int8)
    return s[:, :-(NUM_ELE+2)], truth

results = {}
for it in ITERS:
    print(f"\n=== checkpoint {it} ===")
    model = load(it)
    per_shard = max(BS, NJETS // max(len(files), 1))
    # per class: [n, correct_intact, correct_ablated]
    acc = np.zeros((10, 3), dtype=np.int64)
    seen = 0; t0 = time.time()
    for f in files:
        if seen >= NJETS: break
        feats, truth = shard(f)
        idx = rng.permutation(len(truth))[:per_shard]
        feats, truth = feats[idx], truth[idx]
        for b in range(0, len(truth), BS):
            if seen >= NJETS: break
            flat = torch.from_numpy(np.ascontiguousarray(feats[b:b+BS])).to(dev)
            tb = truth[b:b+BS]
            with torch.no_grad():
                inpt, _ = model.get_inpt(flat, device=dev)
                ABLATE["on"] = False; p_in = model(inpt).argmax(1).cpu().numpy()
                ABLATE["on"] = True;  p_ab = model(inpt).argmax(1).cpu().numpy()
                ABLATE["on"] = False
            for c in range(10):
                m = tb == c
                if not m.any(): continue
                acc[c, 0] += int(m.sum())
                acc[c, 1] += int((p_in[m] == c).sum())
                acc[c, 2] += int((p_ab[m] == c).sum())
            seen += len(tb)
        del feats, truth
    tot = acc.sum(0)
    print(f"  {seen} jets in {(time.time()-t0)/60:.1f} min")
    print(f"  OVERALL  intact {100*tot[1]/tot[0]:6.3f}%   ablated {100*tot[2]/tot[0]:6.3f}%"
          f"   drop {100*(tot[1]-tot[2])/tot[0]:+6.3f}")
    row = {"overall": {"n": int(tot[0]), "intact": float(tot[1]/tot[0]),
                       "ablated": float(tot[2]/tot[0]),
                       "drop": float((tot[1]-tot[2])/tot[0])}}
    for c in range(10):
        if acc[c,0] == 0: continue
        n, ci, ca = acc[c]
        row[CLASSES[c]] = {"n": int(n), "intact": float(ci/n), "ablated": float(ca/n),
                           "drop": float((ci-ca)/n)}
        print(f"    {CLASSES[c]:12s} n={n:6d}  intact {100*ci/n:6.2f}%  "
              f"ablated {100*ca/n:6.2f}%  drop {100*(ci-ca)/n:+6.2f}")
    results[it] = row
    del model
    if dev == "cuda": torch.cuda.empty_cache()

with open(JSON, "w") as fh: json.dump(results, fh, indent=1)
print("\nwrote", JSON)
