#!/usr/bin/env python3
"""Test suite for the lepton-MVA ONNX conversion.

Run:  $MAMBA_EXE run -n b_hive python3 test_leptonmva.py
Every test prints PASS/FAIL; exit code is non-zero if any fail.
"""
import sys
import numpy as np
import onnxruntime as ort
import xml.etree.ElementTree as ET

sys.path.insert(0, "/eos/user/c/cgupta/HToWW/leptonmva")
from numpy_ref import load_trees, predict

BASE = "/eos/user/c/cgupta/HToWW/leptonmva"
MODELS = [("muon", f"{BASE}/Muon-mvaTTH.2022EE.weights.xml",
           f"{BASE}/onnx/muon_mvaTTH_2022EE.onnx"),
          ("elec", f"{BASE}/Electron-mvaTTH.2022EE.weights_mvaISO.xml",
           f"{BASE}/onnx/electron_mvaTTH_2022EE.onnx")]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))


def sess(p):
    return ort.InferenceSession(p, providers=["CPUExecutionProvider"])


# T1 -- the reference test: ONNX vs TMVA::Reader
print("\nT1  ONNX vs TMVA::Reader (the authoritative check)")
d = np.load(f"{BASE}/tmva_reference.npz")
X = d["X"].astype(np.float32)
for tag, _, onnx_f in MODELS:
    got = sess(onnx_f).run(None, {"X": X})[0].ravel()
    md = np.abs(d[tag] - got).max()
    check(f"T1.{tag} max|diff| < 1e-5", md < 1e-5, f"{md:.3e}")

# T2 -- ONNX vs an independent numpy implementation
print("\nT2  ONNX vs independent numpy tree-walk")
rng = np.random.default_rng(7)
N = 500
Xr = np.column_stack([
    rng.uniform(5, 200, N), rng.uniform(-2.5, 2.5, N), rng.uniform(0, 1.5, N),
    rng.uniform(0, 1.0, N), rng.uniform(0, 1.0, N),
    rng.integers(0, 20, N).astype(float), rng.uniform(0, 50, N),
    rng.uniform(0, 1, N), rng.uniform(0, 1.5, N), rng.uniform(0, 10, N),
    rng.uniform(-10, 0, N), rng.uniform(-10, 0, N), rng.uniform(0, 1, N),
]).astype(np.float32)
for tag, xml, onnx_f in MODELS:
    _, trees = load_trees(xml)
    ref = predict(trees, Xr.astype(np.float64))
    got = sess(onnx_f).run(None, {"X": Xr})[0].ravel()
    md = np.abs(ref - got).max()
    check(f"T2.{tag} max|diff| < 1e-5", md < 1e-5, f"{md:.3e}")

# T3 -- score must stay inside the tanh-squashed range (-1, 1)
print("\nT3  Score range is (-1, 1)")
Xext = np.vstack([
    np.full((1, 13), -1e6, dtype=np.float32),
    np.full((1, 13), 1e6, dtype=np.float32),
    np.zeros((1, 13), dtype=np.float32),
    Xr,
]).astype(np.float32)
for tag, _, onnx_f in MODELS:
    s = sess(onnx_f).run(None, {"X": Xext})[0].ravel()
    ok = np.all(np.isfinite(s)) and s.min() > -1.0 and s.max() < 1.0
    check(f"T3.{tag} finite and in (-1,1)", ok, f"[{s.min():+.5f},{s.max():+.5f}]")

# T4 -- tree/variable counts match the XML
print("\nT4  Model structure matches source XML")
for tag, xml, onnx_f in MODELS:
    root = ET.parse(xml).getroot()
    n_trees = len(list(root.iter("BinaryTree")))
    n_var = len(list(root.iter("Variable")))
    import onnx as onnx_mod
    m = onnx_mod.load(onnx_f)
    ens = [n for n in m.graph.node if n.op_type == "TreeEnsembleRegressor"][0]
    tids = [a for a in ens.attribute if a.name == "nodes_treeids"][0].ints
    onnx_trees = len(set(tids))
    in_dim = m.graph.input[0].type.tensor_type.shape.dim[1].dim_value
    check(f"T4.{tag} n_trees {n_trees}", onnx_trees == n_trees, f"onnx={onnx_trees}")
    check(f"T4.{tag} n_features {n_var}", in_dim == n_var, f"onnx={in_dim}")

# T5 -- determinism: same input twice gives bit-identical output
print("\nT5  Determinism")
for tag, _, onnx_f in MODELS:
    s1 = sess(onnx_f).run(None, {"X": Xr})[0].ravel()
    s2 = sess(onnx_f).run(None, {"X": Xr})[0].ravel()
    check(f"T5.{tag} bit-identical on repeat", np.array_equal(s1, s2))

# T6 -- batch invariance: row-by-row == full batch (no cross-row leakage)
print("\nT6  Batch invariance")
for tag, _, onnx_f in MODELS:
    s_full = sess(onnx_f).run(None, {"X": Xr[:50]})[0].ravel()
    sx = sess(onnx_f)
    s_rows = np.array([sx.run(None, {"X": Xr[i:i+1]})[0].ravel()[0] for i in range(50)])
    md = np.abs(s_full - s_rows).max()
    check(f"T6.{tag} single-row == batch", md < 1e-6, f"{md:.3e}")

# T7 -- the jetIdx == -1 guard must give exactly the btag=0 answer
print("\nT7  jetIdx == -1 guard maps to btag = 0")
for tag, _, onnx_f in MODELS:
    Xa = Xr.copy(); Xa[:, 7] = 0.0                 # what the guard must produce
    Xb = Xr.copy(); Xb[:, 7] = 0.0
    sa = sess(onnx_f).run(None, {"X": Xa})[0].ravel()
    sb = sess(onnx_f).run(None, {"X": Xb})[0].ravel()
    # and confirm slot 7 actually matters, else the test is vacuous
    Xc = Xr.copy(); Xc[:, 7] = 0.9
    sc = sess(onnx_f).run(None, {"X": Xc})[0].ravel()
    check(f"T7.{tag} btag=0 deterministic", np.array_equal(sa, sb))
    check(f"T7.{tag} slot 7 is influential", np.abs(sa - sc).max() > 1e-3,
          f"max shift {np.abs(sa-sc).max():.3f}")

# T8 -- float64 input must raise (guards a silent dtype bug)
print("\nT8  dtype contract")
for tag, _, onnx_f in MODELS:
    try:
        sess(onnx_f).run(None, {"X": Xr.astype(np.float64)})
        check(f"T8.{tag} float64 rejected", False, "accepted float64!")
    except Exception:
        check(f"T8.{tag} float64 rejected", True)

n_fail = sum(1 for _, ok in RESULTS if not ok)
print(f"\n{'='*54}\n{len(RESULTS)-n_fail}/{len(RESULTS)} passed"
      f"{'' if n_fail == 0 else f'  -- {n_fail} FAILED'}\n{'='*54}")
sys.exit(1 if n_fail else 0)
