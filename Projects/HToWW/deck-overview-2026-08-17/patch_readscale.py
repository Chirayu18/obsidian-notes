"""Rewrite read_scale to use the SELF-NORMALIZING sumw_records (source #1),
falling back to the sidecar only for legacy samples that have no records."""
from pathlib import Path
P = Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/"
         "scripts/combine/make_combine_inputs.py")
s = P.read_text()

old_start = s.index("def read_scale(sample, year, base_dir, lumi):")
old_end   = s.index("def gather_samples(year, process_map):")
new = '''def read_scale(sample, year, base_dir, lumi):
    """lumi*xsec/sumw for an MC/signal sample; 1.0 for data.

    SELF-NORMALISING (source #1): sumw comes from the per-chunk sumw_records written
    by dump_chunk_sumw on the PRE-selection events of every read chunk -- including
    chunks that select zero events and therefore write no data shard. This is the
    repo's own read_parquet_sumw() logic and is the correct generator sumw.

    Legacy samples produced before dump_chunk_sumw have no sumw_records; for those we
    fall back to the sidecar analysis/filesets/sumw_<year>.json. Every fallback is
    logged so the set is explicit.

    NOT USED: the per-shard schema metadata in parquets_<sample>/base/. It undercounts
    low-efficiency samples badly (WtoLNu_2Jets 5.4x, TbarQto2Q 72x) precisely because
    zero-selection chunks wrote no shard.
    """
    info = get_dataset_config(year).get(sample, {})
    era = info.get("era")
    if era not in ("mc", "signal"):
        return 1.0
    xsec = float(info["xsec"])

    import json, re as _re

    # --- source #1: sumw_records (self-normalising) ---
    rec_dirs = glob.glob(f"{base_dir}/{sample}_*/sumw_records") + glob.glob(
        f"{base_dir}/{sample}/sumw_records"
    )
    # guard against prefix collisions (DYto2L_2Jets_50 vs ..._50_ext)
    rec_dirs = [
        d for d in rec_dirs
        if _re.fullmatch(rf"{_re.escape(sample)}(_\\d+)?", Path(d).parent.name)
    ]
    rec_files = [f for d in rec_dirs for f in glob.glob(f"{d}/*.parquet")]
    sumw = 0.0
    for f in rec_files:
        sumw += float(sum(pq.read_table(f, columns=["sumw"])["sumw"].to_pylist()))

    if sumw > 0:
        return lumi * xsec / sumw

    # --- fallback: sidecar, for legacy samples with no sumw_records ---
    sidecar = json.load(open(Path.cwd() / "analysis" / "filesets" / f"sumw_{year}.json"))
    sumw = sidecar.get(sample)
    if not sumw:
        raise ValueError(
            f"no sumw for MC sample {sample!r}: no sumw_records under "
            f"{base_dir}/{sample}*/sumw_records and not in sumw_{year}.json"
        )
    print(f"    [sumw] {sample}: no sumw_records -> sidecar fallback ({float(sumw):.4e})")
    return lumi * xsec / float(sumw)


'''
P.write_text(s[:old_start] + new + s[old_end:])
print("patched read_scale -> sumw_records primary, sidecar fallback")
