import sys

p = 'scripts/combine/make_combine_inputs.py'
s = open(p).read()

old_doc = '''    SELF-NORMALISING (source #1): sumw comes from the per-chunk sumw_records written
    by dump_chunk_sumw on the PRE-selection events of every read chunk -- including
    chunks that select zero events and therefore write no data shard. This is the
    repo's own read_parquet_sumw() logic and is the correct generator sumw.

    Legacy samples produced before dump_chunk_sumw have no sumw_records; for those we
    fall back to the sidecar analysis/filesets/sumw_<year>.json. Every fallback is
    logged so the set is explicit.
'''
new_doc = '''    SELF-NORMALISING: sumw comes from the per-chunk sumw_records written by
    dump_chunk_sumw on the PRE-selection events of every read chunk -- including
    chunks that select zero events and therefore write no data shard. This is the
    repo's own read_parquet_sumw() logic and is the correct generator sumw.
'''
if old_doc not in s:
    sys.exit('DOCSTRING ANCHOR MISSING')
s = s.replace(old_doc, new_doc, 1)

old_fb = '''    if sumw > 0:
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
new_fb = '''    if sumw <= 0:
        raise ValueError(
            f"no sumw for MC sample {sample!r}: no sumw_records under "
            f"{base_dir}/{sample}*/sumw_records. Reprocess the sample -- "
            f"dump_chunk_sumw writes these unconditionally."
        )
    return lumi * xsec / sumw
'''
if old_fb not in s:
    sys.exit('FALLBACK ANCHOR MISSING')
s = s.replace(old_fb, new_fb, 1)

s = s.replace('    # --- source #1: sumw_records (self-normalising) ---\n',
              '    # --- sumw_records (self-normalising) ---\n', 1)

# 'json' import was only needed for the sidecar read; check before touching it
open(p, 'w').write(s)
print('read_scale cleaned')
print('remaining json uses in file:', s.count('json.'))
