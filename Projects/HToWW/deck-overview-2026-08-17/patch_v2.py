import pathlib
p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/scripts/combine/make_combine_inputs_v2.py")
s = p.read_text()

# need glob for the shift-dir discovery
s = s.replace("import logging\nimport sys", "import glob\nimport logging\nimport sys", 1)

old = """    base.clip_negative_bins(proc_hists, channels, processes, variations)
"""
new = """    # --- Object-shift (kinematic) systematics -------------------------------------
    # Same logic as the original builder, but filled with each channel's own edges.
    # JES/JER/lepton-scale live in <syst>Up / <syst>Down parquet dirs with SHIFTED
    # kinematics -> shifted MVA scores -> events migrate argmax channels. MC-only,
    # weight_nominal only. A (channel, process) with no shift events falls back to its
    # nominal template so combine does not see a fake 100% shape.
    obj_shift_systs = []
    for d in sorted(glob.glob(str(base_dir / "*Up"))):
        nm = Path(d).name
        if nm.endswith("Up") and (Path(d) / "mva").is_dir() \\
                and (base_dir / f"{nm[:-2]}Down" / "mva").is_dir():
            obj_shift_systs.append(nm[:-2])
    obj_shift_vars = [(f"{sname}{dn}", "weight_nominal")
                      for sname in obj_shift_systs for dn in ("Up", "Down")]

    for ch in channels:
        nb = len(edges_by_ch[ch]) - 1
        for cp in processes:
            for vn, _ in obj_shift_vars:
                proc_hists[ch][cp][vn] = (np.zeros(nb), np.zeros(nb))

    for vn, _ in obj_shift_vars:
        sdir = base_dir / vn / "mva"
        for cp in processes:
            for sample in combine_to_samples.get(cp, []):
                pq_path = sdir / f"{sample}.parquet"
                if not pq_path.exists():
                    continue
                for edges_t, chs in distinct.items():
                    edges = np.array(edges_t, dtype=float)
                    res = base.process_sample(
                        pq_path, sample, args.year, base_dir, classes, score_cols,
                        channels_by_class, [(vn, "weight_nominal")],
                        len(edges) - 1, edges, lumi, is_vjets=(cp == "vjets"),
                    )
                    if res is None:
                        continue
                    for ch in chs:
                        ac, as2 = proc_hists[ch][cp][vn]
                        hh = res[ch][vn]
                        proc_hists[ch][cp][vn] = (ac + hh[0], as2 + hh[1])

    for ch in channels:
        for cp in processes:
            nom_c, nom_s2 = proc_hists[ch][cp]["nominal"]
            for vn, _ in obj_shift_vars:
                c, _s2 = proc_hists[ch][cp][vn]
                if c.sum() <= 0 < nom_c.sum():
                    proc_hists[ch][cp][vn] = (nom_c.copy(), nom_s2.copy())

    variations = variations + obj_shift_vars
    logging.info("Folded %d object-shift systematics: %s",
                 len(obj_shift_systs), obj_shift_systs)

    n_clip = base.clip_negative_bins(proc_hists, channels, processes, variations)
    logging.info("Clipped %d non-positive nominal bins to floor", n_clip)

    if combine.get("smooth_shapes"):
        n_sm = base.smooth_shape_variations(proc_hists, channels, processes, variations)
        logging.info("Smoothed %d shape variations (LOWESS)", n_sm)
        base.clip_negative_bins(proc_hists, channels, processes, variations)
"""
assert old in s, "clip anchor missing"
s = s.replace(old, new, 1)

# pass obj_shift_systs through to the datacard writer
s = s.replace(
    "    yields = write_datacard_v2(out_card, out_root.name, combine, proc_hists, processes)",
    "    yields = write_datacard_v2(out_card, out_root.name, combine, proc_hists,\n"
    "                               processes, obj_shift_systs=obj_shift_systs)",
    1,
)
p.write_text(s)
print("patched v2: object-shift pass + smoothing added")
