import re
from pathlib import Path
p = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/scripts/combine/make_combine_inputs.py")
s = p.read_text()

# 1) process_sample signature: accept channel_cuts
old_sig = """def process_sample(pq_path, sample, year, base_dir, classes, score_cols,
                   channels_by_class, variations, nbins, edges, lumi,
                   is_vjets=False, negrw_shape_name=None):"""
new_sig = """def process_sample(pq_path, sample, year, base_dir, classes, score_cols,
                   channels_by_class, variations, nbins, edges, lumi,
                   is_vjets=False, negrw_shape_name=None, channel_cuts=None):"""
assert old_sig in s
s = s.replace(old_sig, new_sig)

# 2) AND the per-channel kinematic cut into channel_idx
old = """    channel_idx = {channels_by_class[cls]: (argmax == i) for i, cls in enumerate(classes)}"""
new = '''    channel_idx = {channels_by_class[cls]: (argmax == i) for i, cls in enumerate(classes)}

    # Optional per-channel kinematic cuts (yaml `channel_cuts:`). Each entry is a
    # python expression over parquet columns, ANDed into that channel's argmax mask.
    # Everything it needs (mll/mTll/mTl2, scores, weights) is already in the scored
    # MVA parquets, so redefining a control region needs NO workflow re-run.
    # Absent block -> untouched behaviour.
    if channel_cuts:
        env = {"np": np, "df": df}
        env.update({c: df[c].to_numpy() for c in df.columns
                    if df[c].dtype.kind in "fiub"})
        # convenient aliases matching the workflow's object names
        if "dilepton_mass" in df.columns:
            env["mll"] = env["dilepton_mass"]
        for ch, expr in channel_cuts.items():
            if ch not in channel_idx:
                raise KeyError(f"channel_cuts references unknown channel '{ch}'")
            m = np.asarray(eval(expr, env), dtype=bool)
            if m.shape != channel_idx[ch].shape:
                raise ValueError(f"channel_cuts[{ch}] gave shape {m.shape}, "
                                 f"expected {channel_idx[ch].shape}")
            channel_idx[ch] = channel_idx[ch] & m'''
assert old in s
s = s.replace(old, new)

# 3) thread channel_cuts from the combine block through both call sites
s = s.replace(
    '''    combine_to_samples = gather_samples(args.year, process_map)''',
    '''    channel_cuts = combine.get("channel_cuts") or {}
    if channel_cuts:
        logging.info("channel_cuts active:")
        for _ch, _e in channel_cuts.items():
            logging.info(f"  {_ch}: {_e}")

    combine_to_samples = gather_samples(args.year, process_map)''')

s = s.replace(
    '''                                    is_vjets=(cp == "vjets"),
                                    negrw_shape_name=NEGRW_SHAPE)''',
    '''                                    is_vjets=(cp == "vjets"),
                                    negrw_shape_name=NEGRW_SHAPE,
                                    channel_cuts=channel_cuts)''')

p.write_text(s)
print("patched OK")
print("channel_cuts occurrences:", s.count("channel_cuts"))
