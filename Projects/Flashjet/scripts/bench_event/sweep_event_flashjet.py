"""flashjet side of the ATLAS Open Data EVENT-regime timing sweep.

The jet-regime sweep (sweep_flashjet.py) times ONE LARGE-R JET per unit.
This one times ONE WHOLE EVENT per unit (~590 calorimeter clusters), on the
2020 ATLAS JetReco open dataset.

Sweeps algorithm x radius x multiplicity bin, exactly like the jet-regime pair,
so the two can be compared on Mpart/s (the only cross-regime-comparable number:
a jet and an event are different units, so us/unit is NOT comparable).

Writes, per (alg, R, bin):
  <SCRATCH>/ev_<bin>.npy                    ragged events (float64) for FastJet
  <SCRATCH>/ev_<alg>_R<R>_<bin>_fj.npz      flashjet n_jets + jet p4
  <SCRATCH>/ev_<alg>_R<R>_<bin>_flashjet.json

Usage:  python sweep_event_flashjet.py [maxevents_per_bin]
"""
import json, os, sys, time
import numpy as np
import torch
import flashjet

DATA    = "/eos/home-c/cgupta/flashjet/data/opendata"
SCRATCH = os.environ.get("EVSCRATCH", "/eos/home-c/cgupta/flashjet/bench_event/results")
ALGS    = ["antikt", "kt", "cambridge"]
RADII   = [0.4, 0.6, 0.8, 1.0, 1.2]
# multiplicity bins on n_clusters/event (mean ~592, range 150-1431)
BINS    = [("lo", 150, 400), ("mid", 400, 600), ("hi", 600, 800),
           ("vhi", 800, 1500), ("all", 150, 1500)]
ITERS   = 20


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    os.makedirs(SCRATCH, exist_ok=True)

    z = np.load(f"{DATA}/opendata_constit_atlasevent_ak4.npz", allow_pickle=True)
    P_all, n_all = z["p4"], z["ncon"].astype(np.int64)

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    gpu = torch.cuda.get_device_name(0) if dev == "cuda" else "CPU"
    print(f"device={dev} gpu={gpu}", flush=True)
    results = []

    for bname, blo, bhi in BINS:
        sel = (n_all >= blo) & (n_all < bhi)
        idx = np.flatnonzero(sel)[:cap]
        if len(idx) < 20:
            print(f"skip bin {bname}: only {len(idx)} events", flush=True)
            continue
        ncon = n_all[idx]
        Nmax = int(ncon.max())
        P = P_all[idx][:, :Nmax]
        B = len(ncon)
        ntot = int(ncon.sum())

        p4_t = torch.from_numpy(P.astype("float32")).to(dev)
        mask = (torch.arange(Nmax)[None, :] < torch.from_numpy(ncon)[:, None]).to(dev)

        # save the ragged input ONCE per bin -- FastJet reads this exact file
        rag = f"{SCRATCH}/ev_{bname}.npy"
        if not os.path.exists(rag):
            ev = np.array([P[i, :ncon[i]].astype("float64") for i in range(B)],
                          dtype=object)
            np.save(rag, ev, allow_pickle=True)

        for alg in ALGS:
            for R in RADII:
                key = f"ev_{alg}_R{R}_{bname}"

                flashjet.cluster(p4_t, mask, R=R, algorithm=alg)   # warmup
                if dev == "cuda":
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                for _ in range(ITERS):
                    out = flashjet.cluster(p4_t, mask, R=R, algorithm=alg)
                if dev == "cuda":
                    torch.cuda.synchronize()
                dt = (time.perf_counter() - t0) / ITERS

                njets = out.n_jets.cpu().numpy()
                jp4 = out.jets_p4(p4_t).detach().cpu().numpy()
                np.savez(f"{SCRATCH}/{key}_fj.npz", njets=njets, jets_p4=jp4)

                rec = {"regime": "event", "alg": alg, "R": R, "bin": bname,
                       "bin_lo": blo, "bin_hi": bhi,
                       "device": dev, "gpu": gpu,
                       "n_events_input": B, "total_constituents": ntot,
                       "mean_const_per_event": round(float(ncon.mean()), 2),
                       "max_const": Nmax,
                       "ms_per_batch": round(dt * 1e3, 4),
                       "us_per_event": round(dt / B * 1e6, 4),
                       "Mpart_per_s": round(ntot / dt / 1e6, 3),
                       "iters": ITERS}
                results.append(rec)
                with open(f"{SCRATCH}/{key}_flashjet.json", "w") as fh:
                    json.dump(rec, fh, indent=1)
                print(json.dumps(rec), flush=True)

    with open(f"{SCRATCH}/summary_event_flashjet.json", "w") as fh:
        json.dump(results, fh, indent=1)
    print("DONE_FLASHJET", flush=True)


if __name__ == "__main__":
    main()
