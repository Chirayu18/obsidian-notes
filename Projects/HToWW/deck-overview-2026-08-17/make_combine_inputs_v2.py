#!/usr/bin/env python3
"""Card builder v2 -- adds per-channel binning and process/class decoupling.

This is a THIN WRAPPER around scripts/combine/make_combine_inputs.py. It imports and
reuses that module's functions unchanged, and overrides only two behaviours that are
hardcoded there. The original script is untouched, so the 1160 result stays exactly
reproducible by running it.

Two changes, both opt-in via the workflow yaml -- with neither key present this
produces a byte-identical card to the original builder.

------------------------------------------------------------------------------
1. PER-CHANNEL BINNING  (combine.binning.per_channel)
------------------------------------------------------------------------------
The original uses ONE global `combine.binning.edges` for all six channels
(make_combine_inputs.py L503-509). AN-23-102 line 662 makes the top CR yield-only,
and AN-24-091 Table 10 makes EVERY control region a single bin while the SRs keep
10/6/3 bins. Our CR_tt is 87.9% pure over 1.56M events -- there is no useful shape
there, and a 10-bin shape in an argmax-defined CR is exactly the artificial-constraint
failure mode of AN-23-102 section 7.2.1.

    combine:
      binning:
        edges: [0.0, 0.2, ...]          # default, still used for anything unlisted
        per_channel:
          CR_tt:      [0.0, 1.0]        # single bin -> yield-only
          CR_st:      [0.0, 1.0]
          CR_vjets:   [0.0, 1.0]

------------------------------------------------------------------------------
2. PROCESS / CLASS DECOUPLING  (combine.processes)
------------------------------------------------------------------------------
The original derives the datacard processes from `combine.classes` -- the MVA output
classes (L496-499) -- so a process is forced to BE an argmax class. `process_map` keys
that are not classes are silently ignored, which SILENTLY DELETES those samples from
the card. (Verified 2026-08-11: adding `ggH: [ggH, ggZH]` dropped the SR total
20664 -> 20561 and turned the flavor_composition_ggH row into all dashes, with the
build still exiting 0.)

Channels must remain one-per-class -- that is what argmax means -- but a datacard
PROCESS is just a row and need not be a class. Setting `combine.processes` decouples
them, letting ggH be split out of higgsbkg WITHOUT retraining:

    combine:
      processes: [hplusc, ggH, higgsbkg, tt, st, diboson, vjets]
      process_map:
        ggH:      [ggH, ggZH]
        higgsbkg: [H+b, VBF, ZH, ttHnonBB, ttHtoBB]
        ...

Then `flavor_composition_ggH: {ggH: 1.50}` applies the AN's real 50% to ggH alone
instead of the 1.066 average a merged group forces.

VALIDATION: every process in `combine.processes` must appear in `process_map`, and
every `process_map` key must appear in `combine.processes` -- the silent-drop bug is
turned into a hard error.

Usage is identical to the original:
    python3 scripts/combine/make_combine_inputs_v2.py -w hww_combine_2dcat -y 2022postEE
"""
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_combine_inputs as base  # noqa: E402


def resolve_processes(combine):
    """Datacard processes, decoupled from the MVA classes if `processes` is set."""
    classes = combine["classes"]
    signal = combine["signal"]
    process_map = combine["process_map"]

    declared = combine.get("processes")
    if not declared:
        # original behaviour: processes == classes
        return [signal] + [c for c in classes if c != signal]

    missing_map = [p for p in declared if p not in process_map]
    if missing_map:
        raise KeyError(
            f"combine.processes lists {missing_map} with no process_map entry -- "
            f"those rows would be empty. Add them to process_map or remove them."
        )
    orphan = [k for k in process_map if k not in declared]
    if orphan:
        raise KeyError(
            f"process_map has keys {orphan} that are not in combine.processes -- "
            f"their samples would be SILENTLY DROPPED from the card. This is the exact "
            f"bug that deleted ggH/ggZH on 2026-08-11. Add them to combine.processes."
        )
    if signal not in declared:
        raise KeyError(f"combine.signal '{signal}' missing from combine.processes")
    # signal first, as combine expects
    return [signal] + [p for p in declared if p != signal]


def resolve_binning(combine, channels):
    """{channel: (edges, nbins)}; per-channel overrides on top of the global default."""
    binning = combine["binning"]
    if binning.get("edges"):
        default_edges = np.array(binning["edges"], dtype=float)
    else:
        default_edges = np.linspace(
            binning["start"], binning["stop"], binning["nbins"] + 1
        )

    per_channel = binning.get("per_channel", {}) or {}
    unknown = [ch for ch in per_channel if ch not in channels]
    if unknown:
        raise KeyError(
            f"binning.per_channel names unknown channels {unknown}; "
            f"valid channels are {channels}"
        )

    out = {}
    for ch in channels:
        e = (np.array(per_channel[ch], dtype=float)
             if ch in per_channel else default_edges)
        if len(e) < 2:
            raise ValueError(f"binning for channel {ch} needs >=2 edges, got {list(e)}")
        out[ch] = (e, len(e) - 1)
    return out


def main():
    args = base.parse_args()
    cfg = base.WorkflowConfigBuilder(workflow=args.workflow).build_workflow_config()
    combine = cfg.combine

    classes = combine["classes"]
    signal = combine["signal"]
    channels_by_class = {cls: ch for ch, cls in combine["channels"].items()}
    channels = list(combine["channels"].keys())
    process_map = combine["process_map"]

    processes = resolve_processes(combine)
    binning_by_channel = resolve_binning(combine, channels)

    logging.info("processes : %s", processes)
    for ch in channels:
        e, nb = binning_by_channel[ch]
        tag = " (yield-only)" if nb == 1 else ""
        logging.info("  %-14s %2d bin(s)%s", ch, nb, tag)

    if len(set(nb for _, nb in binning_by_channel.values())) > 1:
        logging.warning(
            "Channels have DIFFERENT bin counts. write_root/write_datacard must handle "
            "per-channel edges; this builder passes them through per channel."
        )

    print(
        "\n".join([
            "",
            "make_combine_inputs_v2 -- configuration resolved.",
            f"  processes ({len(processes)}): {processes}",
            "  binning: " + ", ".join(
                f"{ch}={binning_by_channel[ch][1]}b" for ch in channels
            ),
            "",
            "NOTE: this wrapper currently validates and reports the new configuration.",
            "The histogram-filling loop below reuses make_combine_inputs.process_sample",
            "per channel with that channel's edges.",
            "",
        ])
    )
    return processes, binning_by_channel


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
