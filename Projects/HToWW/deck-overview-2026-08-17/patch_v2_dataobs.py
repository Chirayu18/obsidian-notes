import sys

p = 'scripts/combine/make_combine_inputs_v2.py'
s = open(p).read()

# ---- 1. write_root_v2 gains an optional extra_hists argument -------------
old_wr = '''    root_path.parent.mkdir(parents=True, exist_ok=True)
    with base.uproot.recreate(str(root_path)) as f:
        for name, h in histograms.items():
            f[name] = h
    return len(histograms)'''
new_wr = '''    if extra_hists:
        histograms.update(extra_hists)
    root_path.parent.mkdir(parents=True, exist_ok=True)
    with base.uproot.recreate(str(root_path)) as f:
        for name, h in histograms.items():
            f[name] = h
    return len(histograms)'''
if old_wr not in s:
    sys.exit('ANCHOR 1 MISSING (write_root_v2 body)')
s = s.replace(old_wr, new_wr, 1)

# add the parameter to the signature
old_sig = 'def write_root_v2(root_path, proc_hists, channels, processes, variations, edges_by_ch):'
new_sig = ('def write_root_v2(root_path, proc_hists, channels, processes, variations,\n'
           '                  edges_by_ch, extra_hists=None):')
if old_sig not in s:
    sys.exit('ANCHOR 2 MISSING (write_root_v2 signature)')
s = s.replace(old_sig, new_sig, 1)

# ---- 2. write_data_obs_v2 -> build_data_obs_v2 (no file I/O) -------------
old_do = '''def write_data_obs_v2(root_path, proc_hists, channels, backgrounds, edges_by_ch):
    data = {}
    for ch in channels:
        counts = np.sum([proc_hists[ch][b]["nominal"][0] for b in backgrounds], axis=0)
        sumw2 = np.sum([proc_hists[ch][b]["nominal"][1] for b in backgrounds], axis=0)
        data[ch] = (counts, sumw2)
    with base.uproot.update(str(root_path)) as f:
        for ch, (counts, sumw2) in data.items():
            f[f"{ch}_data_obs"] = base.to_uproot_th1(
                counts, sumw2, edges_by_ch[ch], f"{ch}_data_obs"
            )
    return {ch: data[ch][0].sum() for ch in channels}'''
new_do = '''def build_data_obs_v2(proc_hists, channels, backgrounds, edges_by_ch):
    """Build per-channel Asimov bkg-only data_obs histograms IN MEMORY.

    Returns (hists, totals) so the caller can hand `hists` to write_root_v2 and
    have everything written in ONE uproot.recreate pass.

    Why not append with uproot.update(): the previous implementation wrote the
    file with recreate(), closed it, then reopened it with update() to append
    data_obs. Reopening makes uproot re-parse the file's free-segments record,
    which fails on files written to EOS:

        struct.error: unpack requires a buffer of 10 bytes
        (uproot/writing/_cascade.py, FreeSegmentsData.deserialize)

    The crash happened AFTER all histogram content was already on disk, so the
    build had in fact succeeded -- it just exited non-zero, which is worse than
    a clean failure because it sends you looking for a problem that is not
    there. Building in memory and writing once removes the reopen entirely.
    """
    hists, totals = {}, {}
    for ch in channels:
        counts = np.sum([proc_hists[ch][b]["nominal"][0] for b in backgrounds], axis=0)
        sumw2 = np.sum([proc_hists[ch][b]["nominal"][1] for b in backgrounds], axis=0)
        hists[f"{ch}_data_obs"] = base.to_uproot_th1(
            counts, sumw2, edges_by_ch[ch], f"{ch}_data_obs"
        )
        totals[ch] = counts.sum()
    return hists, totals'''
if old_do not in s:
    sys.exit('ANCHOR 3 MISSING (write_data_obs_v2)')
s = s.replace(old_do, new_do, 1)

# ---- 3. main(): single write pass ---------------------------------------
old_main = '''    n = write_root_v2(out_root, proc_hists, channels, processes, variations, edges_by_ch)
    write_data_obs_v2(out_root, proc_hists, channels, backgrounds, edges_by_ch)'''
new_main = '''    data_obs_hists, _ = build_data_obs_v2(proc_hists, channels, backgrounds, edges_by_ch)
    n = write_root_v2(out_root, proc_hists, channels, processes, variations,
                      edges_by_ch, extra_hists=data_obs_hists)'''
if old_main not in s:
    sys.exit('ANCHOR 4 MISSING (main write calls)')
s = s.replace(old_main, new_main, 1)

open(p, 'w').write(s)
print('patched: data_obs now written in the same recreate pass')
