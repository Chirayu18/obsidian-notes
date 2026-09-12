"""FastJet side of the ATLAS EVENT-regime timing sweep.

Clusters the EXACT ragged events saved by sweep_event_flashjet.py, and checks
agreement two ways (n_jets equality, and leading-jet pT within 1e-4 relative)
-- timing without agreement is meaningless.

ITERS is small because the classic loop over ~590-cluster events is slow.

Usage: python sweep_event_fastjet.py
"""
import json, os, sys, time
import numpy as np
import fastjet

SCRATCH = os.environ.get("EVSCRATCH", "/eos/home-c/cgupta/flashjet/bench_event/results")
ALGS = {"antikt": fastjet.antikt_algorithm,
        "kt": fastjet.kt_algorithm,
        "cambridge": fastjet.cambridge_algorithm}
RADII = [0.4, 0.6, 0.8, 1.0, 1.2]
BINS = ["lo", "mid", "hi", "vhi", "all"]
ITERS = 3


def main():
    out = []
    for bname in BINS:
        rag = f"{SCRATCH}/ev_{bname}.npy"
        if not os.path.exists(rag):
            print(f"skip bin {bname}: no ragged file", flush=True)
            continue
        events = np.load(rag, allow_pickle=True)
        B = len(events)
        ntot = int(sum(len(e) for e in events))

        for alg, fjalg in ALGS.items():
            for R in RADII:
                key = f"ev_{alg}_R{R}_{bname}"
                jd = fastjet.JetDefinition(fjalg, R)

                def classic():
                    nj = np.empty(B, np.int64)
                    lead = np.zeros(B)
                    for i, ev in enumerate(events):
                        pjs = [fastjet.PseudoJet(*map(float, r)) for r in ev]
                        js = fastjet.ClusterSequence(pjs, jd).inclusive_jets()
                        nj[i] = len(js)
                        if js:
                            lead[i] = max(j.pt() for j in js)
                    return nj, lead

                t0 = time.perf_counter()
                for _ in range(ITERS):
                    njc, leadc = classic()
                tc = (time.perf_counter() - t0) / ITERS

                rec = {"regime": "event", "alg": alg, "R": R, "bin": bname,
                       "n_events_input": B, "total_constituents": ntot,
                       "classic": {"ms_per_batch": round(tc * 1e3, 3),
                                   "us_per_event": round(tc / B * 1e6, 3),
                                   "Mpart_per_s": round(ntot / tc / 1e6, 4)}}

                try:
                    import awkward as ak
                    recs = ak.Array([[{"px": float(r[0]), "py": float(r[1]),
                                       "pz": float(r[2]), "E": float(r[3])}
                                      for r in ev] for ev in events])

                    def awk():
                        cs = fastjet.ClusterSequence(recs, jd)
                        return ak.num(cs.inclusive_jets(), axis=1)

                    awk()   # warmup
                    t0 = time.perf_counter()
                    for _ in range(ITERS):
                        awk()
                    ta = (time.perf_counter() - t0) / ITERS
                    rec["awkward"] = {"ms_per_batch": round(ta * 1e3, 3),
                                      "us_per_event": round(ta / B * 1e6, 3),
                                      "Mpart_per_s": round(ntot / ta / 1e6, 4)}
                except Exception as e:
                    rec["awkward"] = {"error": str(e)[:200]}

                # agreement vs flashjet
                fjf = f"{SCRATCH}/{key}_fj.npz"
                if os.path.exists(fjf):
                    z = np.load(fjf)
                    njf = z["njets"]
                    rec["n_jets_agreement"] = {
                        "matched": int((njf == njc).sum()), "total": B,
                        "pct": round(100 * float((njf == njc).mean()), 4)}
                    jp4 = z["jets_p4"]
                    ptf = np.hypot(jp4[..., 0], jp4[..., 1])
                    leadf = ptf.max(axis=1) if ptf.ndim > 1 else ptf
                    ok = leadc > 0
                    rel = np.abs(leadf[ok] - leadc[ok]) / leadc[ok]
                    rec["lead_pt_agreement"] = {
                        "frac_within_1e-4": round(float((rel < 1e-4).mean()), 5),
                        "frac_within_1e-2": round(float((rel < 1e-2).mean()), 5),
                        "median_rel": float(np.median(rel)),
                        "max_rel": float(rel.max())}
                out.append(rec)
                print(json.dumps(rec), flush=True)
                with open(f"{SCRATCH}/{key}_fastjet.json", "w") as fh:
                    json.dump(rec, fh, indent=1)

    with open(f"{SCRATCH}/summary_event_fastjet.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("DONE_FASTJET", flush=True)


if __name__ == "__main__":
    main()
