
def write_root_v2(root_path, proc_hists, channels, processes, variations, edges_by_ch):
    """As base.write_root but with per-channel edges."""
    histograms = {}
    for ch in channels:
        edges = edges_by_ch[ch]
        for cp in processes:
            for var_name, _ in variations:
                counts, sumw2 = proc_hists[ch][cp][var_name]
                hname = f"{ch}_{cp}" if var_name == "nominal" else f"{ch}_{cp}_{var_name}"
                histograms[hname] = base.to_uproot_th1(counts, sumw2, edges, hname)
    root_path.parent.mkdir(parents=True, exist_ok=True)
    with base.uproot.recreate(str(root_path)) as f:
        for name, h in histograms.items():
            f[name] = h
    return len(histograms)


def write_data_obs_v2(root_path, proc_hists, channels, backgrounds, edges_by_ch):
    """As base.write_data_obs but with per-channel edges."""
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
    return {ch: data[ch][0].sum() for ch in channels}
