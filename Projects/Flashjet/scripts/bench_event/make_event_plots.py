"""Event-regime plots for the ML4Jets deck, plus the cross-regime comparison.

Produces:
  event_abs_timing.png   -- us/event vs mean clusters/event, flashjet vs FastJet
  regime_throughput.png  -- Mpart/s for BOTH regimes on one axis (the money plot)

Mpart/s is the ONLY cross-regime-comparable number: a jet and an event are
different units, so us/unit must never be compared across the two.
"""
import json, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EV  = os.environ.get("EVSCRATCH", "/eos/home-c/cgupta/flashjet/bench_event/results")
JET = "/eos/home-c/cgupta/flashjet/bench_atlas/results_v100"
OUT = "/eos/home-c/cgupta/flashjet/bench_event"
ALGL = {"antikt": r"anti-$k_t$", "kt": r"$k_t$", "cambridge": "C/A"}
BINS = ["lo", "mid", "hi", "vhi"]


def load(pat):
    d = {}
    for p in glob.glob(pat):
        j = json.load(open(p))
        d[(j["alg"], j["R"], j["bin"])] = j
    return d


def main():
    evf = load(f"{EV}/ev_*_flashjet.json")
    evs = load(f"{EV}/ev_*_fastjet.json")
    if not evf:
        print("no event-regime results yet"); return

    # ---- Plot 1: absolute timing, event regime, anti-kt R=1.0 ----
    fig, ax = plt.subplots(figsize=(7, 4.6))
    xs, yf, ya, yc = [], [], [], []
    for b in BINS:
        k = ("antikt", 1.0, b)
        if k not in evf: continue
        xs.append(evf[k]["mean_const_per_event"])
        yf.append(evf[k]["us_per_event"])
        s = evs.get(k, {})
        ya.append((s.get("awkward") or {}).get("us_per_event", np.nan))
        yc.append((s.get("classic") or {}).get("us_per_event", np.nan))
    o = np.argsort(xs); xs = np.array(xs)[o]
    ax.plot(xs, np.array(yf)[o], "o-", label="flashjet (GPU)", lw=2)
    if not np.all(np.isnan(ya)):
        ax.plot(xs, np.array(ya)[o], "s-", label="FastJet vectorised (CPU)", lw=2)
    if not np.all(np.isnan(yc)):
        ax.plot(xs, np.array(yc)[o], "^-", label="FastJet per-event (CPU)", lw=2)
    ax.set_yscale("log"); ax.set_xlabel("mean clusters per event")
    ax.set_ylabel(r"time per event [$\mu$s]")
    ax.set_title(r"ATLAS Open Data, event regime -- anti-$k_t$ $R=1.0$")
    ax.grid(alpha=.3, which="both"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT}/event_abs_timing.png", dpi=140)
    print("wrote event_abs_timing.png")

    # ---- Plot 2: throughput, BOTH regimes ----
    jf = load(f"{JET}/at_atlastop-top_*_flashjet.json")
    fig, ax = plt.subplots(figsize=(7, 4.6))
    jx = [(jf[k]["mean_const_per_jet"], jf[k]["Mpart_per_s"])
          for k in jf if k[0] == "antikt" and k[1] == 1.0 and k[2] in BINS]
    if jx:
        jx.sort()
        ax.plot([p[0] for p in jx], [p[1] for p in jx], "o-", lw=2,
                label="jet regime (one jet per unit)")
    ex = [(evf[k]["mean_const_per_event"], evf[k]["Mpart_per_s"])
          for k in evf if k[0] == "antikt" and k[1] == 1.0 and k[2] in BINS]
    if ex:
        ex.sort()
        ax.plot([p[0] for p in ex], [p[1] for p in ex], "s-", lw=2,
                label="event regime (one event per unit)")
    ax.set_xscale("log")
    ax.set_xlabel("particles per unit, N")
    ax.set_ylabel("throughput [Mparticles/s]")
    ax.set_title(r"flashjet throughput: many small units fill the GPU")
    ax.grid(alpha=.3, which="both"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT}/regime_throughput.png", dpi=140)
    print("wrote regime_throughput.png")

    # ---- text summary ----
    print("\n=== EVENT REGIME (anti-kt R=1.0) ===")
    print(f"{'bin':6s} {'<N>':>8s} {'us/event':>10s} {'Mpart/s':>9s} "
          f"{'FJvec us':>10s} {'speedup':>8s} {'njet %':>8s}")
    for b in BINS + ["all"]:
        k = ("antikt", 1.0, b)
        if k not in evf: continue
        f = evf[k]; s = evs.get(k, {})
        base = (s.get("awkward") or {}).get("us_per_event")
        sp = f"{base/f['us_per_event']:.1f}x" if base else "--"
        ag = (s.get("n_jets_agreement") or {}).get("pct", float("nan"))
        print(f"{b:6s} {f['mean_const_per_event']:8.1f} {f['us_per_event']:10.1f} "
              f"{f['Mpart_per_s']:9.2f} {base if base else float('nan'):10.1f} "
              f"{sp:>8s} {ag:8.3f}")


if __name__ == "__main__":
    main()
