"""Is the ablation drop real dependence, or an off-distribution artifact?

A class falling BELOW the 10% random baseline (HToWW4Q -> 3.95%) cannot be
explained by "the model lost useful information" -- random guessing would give
10%. It means the ablated model is making a SYSTEMATIC wrong prediction. Two
candidates:

 (a) real dependence: the tokens carry signal, removing them degrades sensibly
 (b) off-manifold artifact: masking all 48 tokens is an input the model NEVER saw
     in training, so the residual stream lands somewhere unphysical and the
     output collapses onto one class.

The discriminator is the PREDICTION DISTRIBUTION. Under (a) errors spread across
plausible confusions; under (b) they pile onto one or two classes.

Rai & Ganguly (2605.09881) hit exactly this and say so: they document "a
structural incompatibility between off-manifold (Gaussian) corruption and the
standard recovery-score formulation ... for any kinematically narrow physics
dataset", and use ON-MANIFOLD corruption instead.
"""
import os, sys, glob, functools
import numpy as np, torch, lz4.frame
print = functools.partial(print, flush=True)
BH = "/eos/user/c/cgupta/flashjet/b-hive"
os.environ.setdefault("B_HIVE_DIR", BH)
os.environ.setdefault("FLASHJET_SRC", "/eos/home-c/cgupta/flashjet/FlastJetDemo/src")
sys.path.insert(0, BH); os.chdir(BH)
CFG, VER, MODEL = "jet_class_plum", "b_hive_paper_plum_1", "ParticleTransformer_PLuM_JetClass"
IT = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
CLASSES = ["TTBarLep","TTBar","HToWW2Q1L","HToWW4Q","HToBB","HToCC","HToGG",
           "ZJetsToNuNu","ZToQQ","WToQQ"]
from utils.models.models import BTaggingModels
from utils.config.config_loader import ConfigLoader
cfg = ConfigLoader.load_config(CFG); dev="cpu"
ABL={"on":False}
model = BTaggingModels(MODEL, cfg)
ck=f"{BH}/output/TrainingTask/{CFG}/JetClass_train_100_mod/{VER}/{MODEL}/epochs_0/nominal/model_{IT}.pt"
sd=torch.load(ck,map_location="cpu",weights_only=False)["model_state_dict"]
sd={(k[10:] if k.startswith("_orig_mod.") else k):v for k,v in sd.items()}
model.load_state_dict(sd,strict=False); model.to(dev).eval()
core = model.model if hasattr(model,"model") else model
M = core.m_splits
for bl in (core.blocks, core.cls_blocks):
    for b in bl:
        o=b.forward
        def f(x,x_cls=None,padding_mask=None,attn_mask=None,_o=o,_M=M):
            if ABL["on"] and padding_mask is not None:
                padding_mask=padding_mask.clone(); padding_mask[:,-_M:]=True
            return _o(x,x_cls=x_cls,padding_mask=padding_mask,attn_mask=attn_mask)
        b.forward=f
files=sorted(glob.glob(f"{BH}/output/DatasetConstructorTask/{CFG}/JetClass_test_mod/file_*.lz4"))
rng=np.random.default_rng(7)
with lz4.frame.open(files[0],"r") as fh: raw=fh.read()
s=np.frombuffer(raw,dtype=np.float32).copy(); s=s[2:].reshape(-1,int(s[1]),order="C")
truth=s[:,-11:-1].argmax(1).astype(np.int8); feats=s[:,:-12]
idx=rng.permutation(len(truth))[:2048]; feats,truth=feats[idx],truth[idx]
P_in=[];P_ab=[]
with torch.no_grad():
    for b in range(0,len(truth),256):
        inpt,_=model.get_inpt(torch.from_numpy(np.ascontiguousarray(feats[b:b+256])).to(dev),device=dev)
        ABL["on"]=False; P_in.append(model(inpt).argmax(1).numpy())
        ABL["on"]=True;  P_ab.append(model(inpt).argmax(1).numpy())
P_in=np.concatenate(P_in); P_ab=np.concatenate(P_ab)
print(f"checkpoint {IT}, {len(truth)} jets\n")
print("PREDICTION DISTRIBUTION (what the model outputs, regardless of truth)")
print("  %-12s %8s %8s"%("class","intact","ablated"))
for c in range(10):
    print("  %-12s %7d %8d"%(CLASSES[c],(P_in==c).sum(),(P_ab==c).sum()))
coll=np.bincount(P_ab,minlength=10).max()/len(P_ab)
print(f"\nlargest single predicted class, ablated: {100*coll:.1f}% of all jets")
print("(intact: %.1f%%)"%(100*np.bincount(P_in,minlength=10).max()/len(P_in)))
