"""Per-particle Cambridge/Aachen merge-history features for ParT.

Each constituent is a leaf of the C/A tree and has a unique path to the root, so
any per-particle feature is "something about that path".  We walk ASCENDING from
each leaf to the FIRST node where its branch is the SOFTER child -- the emission
that merged it into the harder core -- and read the Lund coordinates of that
splitting.  Every particle emitted in the same prong therefore shares the same
values, which is what makes this a soft grouping label for attention: ParT's
existing per-particle features are all relative to a single jet axis and cannot
express "these particles were emitted together".

Computed at TRAIN TIME on the GPU batch (see get_inpt in base_model.py), not
baked into the dataset: no multi-hundred-GB rebuild, feature definitions stay
cheap to change, and the clustering overhead is directly measurable.

Missing values: a particle that is always on the harder side never has such a
node.  Those get ALL FIVE VALUES 0 and has_bp = 0.  A flag rather than a
sentinel because ln z is legitimately negative (~[-7, -0.69]), so any single
"missing" number either collides with real soft emissions or is read by the
network as an extreme measurement.
"""

import math
import os
import sys

import torch

# flashjet lives outside b-hive; add it lazily rather than at import time so
# configs that never ask for these features do not pay for it.
_FLASHJET_SRC = os.environ.get(
    "FLASHJET_SRC", "/eos/home-c/cgupta/flashjet/FlastJetDemo/src"
)

N_CA_FEATURES = 5
CA_FEATURE_NAMES = [
    "part_ca_lnkt",
    "part_ca_lnz",
    "part_ca_lndR",
    "part_ca_depth",
    "part_ca_has_bp",
]

_EPS = 1e-8


def _import_flashjet():
    if _FLASHJET_SRC not in sys.path:
        sys.path.insert(0, _FLASHJET_SRC)
    import flashjet
    from flashjet.history import _pseudojet_p4

    return flashjet, _pseudojet_p4


def _direct_parents(hist_p1, hist_p2, hist_child, M):
    """par[b, id] = id of the node this node merges INTO (itself if none).

    Same construction as flashjet's _resolve_parents but WITHOUT the pointer
    jumping: we need one hop at a time to walk the tree, not the final root.
    """
    device = hist_p1.device
    dummy = M - 1
    is_pair = hist_p2 >= 0
    child = hist_child.long()
    par = torch.arange(M, device=device).expand(hist_p1.shape[0], M).clone()
    idx1 = torch.where(is_pair, hist_p1.long(), torch.full_like(child, dummy))
    idx2 = torch.where(is_pair, hist_p2.long(), torch.full_like(child, dummy))
    val = torch.where(is_pair, child, torch.full_like(child, dummy))
    par.scatter_(1, idx1, val)
    par.scatter_(1, idx2, val)
    par[:, dummy] = dummy
    return par


def ca_branch_features(p4, mask, R=0.8):
    """Ascending per-particle C/A branch-point features.

    p4   : (B, N, 4) px, py, pz, E  -- padded, on any device
    mask : (B, N) bool, True for real particles
    ->   : (B, N, 5) float, columns = CA_FEATURE_NAMES, zeros on padded slots
    """
    flashjet, _pseudojet_p4 = _import_flashjet()
    B, N, _ = p4.shape
    device = p4.device
    out = torch.zeros(B, N, N_CA_FEATURES, dtype=p4.dtype, device=device)
    if N == 0 or not bool(mask.any()):
        return out

    # float64 is not supported by the triton path; cluster in float32.
    co = flashjet.cluster(p4.float(), mask, R=R, algorithm="cambridge")
    h1, h2, hc = co.hist_p1, co.hist_p2, co.hist_child
    M = 2 * N

    pj = _pseudojet_p4(h1, h2, hc, mask, p4.float())          # (B, M, 4)
    par = _direct_parents(h1, h2, hc, M)                      # (B, M)

    # sibling[id] = the other child of id's parent (id itself if none)
    sib = torch.arange(M, device=device).expand(B, M).clone()
    is_pair = h2 >= 0
    dummy = M - 1
    i1 = torch.where(is_pair, h1.long(), torch.full_like(h1.long(), dummy))
    i2 = torch.where(is_pair, h2.long(), torch.full_like(h2.long(), dummy))
    sib.scatter_(1, i1, i2)
    sib.scatter_(1, i2, i1)
    sib[:, dummy] = dummy

    pt = torch.hypot(pj[..., 0], pj[..., 1])                  # (B, M)

    # leaf ids: particles are numbered in mask order
    leaf = (mask.long().cumsum(1) - 1).clamp(0, M - 1)        # (B, N)

    cur = leaf.clone()
    found = torch.zeros(B, N, dtype=torch.bool, device=device)
    bp_node = torch.zeros(B, N, dtype=torch.long, device=device)
    depth = torch.zeros(B, N, dtype=p4.dtype, device=device)
    alive = mask.clone()

    # Ascend. A merge tree over N leaves has depth <= N, but is ~log N typically;
    # bound the loop by N so it always terminates.
    for _ in range(int(N)):
        if not bool(alive.any()):
            break
        parent = torch.gather(par, 1, cur)
        at_root = parent == cur                               # no parent: stop
        other = torch.gather(sib, 1, cur)
        pt_self = torch.gather(pt, 1, cur)
        pt_other = torch.gather(pt, 1, other)
        # "softer child" == this branch carries less pt than its sibling
        softer = (pt_self < pt_other) & (other != cur)

        newly = alive & softer & ~found & ~at_root
        bp_node = torch.where(newly, cur, bp_node)
        found = found | newly

        step = alive & ~at_root
        depth = depth + step.to(depth.dtype)
        # stop a particle once it has its branch point, or hit the root
        alive = step & ~found
        cur = torch.where(step, parent, cur)

    # --- kinematics at the branch point (both children are PSEUDOJETS) ---
    soft = bp_node
    hard = torch.gather(sib, 1, soft.clamp(0, M - 1))
    p_s = torch.gather(pj, 1, soft.unsqueeze(-1).expand(B, N, 4))
    p_h = torch.gather(pj, 1, hard.unsqueeze(-1).expand(B, N, 4))

    def _rap_phi(v):
        px, py, pz, E = v[..., 0], v[..., 1], v[..., 2], v[..., 3]
        pt_ = torch.hypot(px, py)
        rap = 0.5 * torch.log(
            ((E + pz).clamp_min(_EPS)) / ((E - pz).clamp_min(_EPS))
        )
        return rap, torch.atan2(py, px), pt_

    rap_s, phi_s, pt_s = _rap_phi(p_s)
    rap_h, phi_h, pt_h = _rap_phi(p_h)
    dphi = (phi_s - phi_h + math.pi) % (2 * math.pi) - math.pi
    dR = torch.sqrt((rap_s - rap_h) ** 2 + dphi ** 2)

    z = pt_s / (pt_s + pt_h).clamp_min(_EPS)                  # soft-side, <= 0.5
    kt = pt_s * dR

    lnkt = torch.log(kt.clamp_min(_EPS))
    lnz = torch.log(z.clamp_min(_EPS))
    lndR = torch.log((1.0 / dR.clamp_min(_EPS)).clamp_min(_EPS))

    keep = found & mask
    out[..., 0] = torch.where(keep, lnkt, torch.zeros_like(lnkt))
    out[..., 1] = torch.where(keep, lnz, torch.zeros_like(lnz))
    out[..., 2] = torch.where(keep, lndR, torch.zeros_like(lndR))
    out[..., 3] = torch.where(mask, depth, torch.zeros_like(depth))
    out[..., 4] = keep.to(out.dtype)
    return torch.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


# indices of part_px, part_py, part_pz, part_energy in jet_class.yml cpf_candidates
JETCLASS_P4_IDX = (12, 13, 14, 15)


def ca_features_from_cpf(cpf, R=0.8, p4_idx=JETCLASS_P4_IDX):
    """Convenience wrapper for the (B, N, F) cpf tensor inside get_inpt."""
    idx = torch.tensor(p4_idx, device=cpf.device, dtype=torch.long)
    p4 = cpf.index_select(-1, idx)
    mask = p4.abs().sum(-1) > 0
    return ca_branch_features(p4, mask, R=R)
