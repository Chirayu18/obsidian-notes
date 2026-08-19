# Top-pT reweighting, applied to tt only.
#
# AN-23-102 Table 16 lists "top pT reweight" as a shape systematic, and line 566
# applies it to the tt sample only. AN-24-091 (Run 3, HH->bbWW) states the
# convention used here: "The full effect of the correction is applied as
# uncertainty, i.e. the difference between the nominal and the corrected
# distributions is considered the 1 sigma interval."
#
# The NNLO/NLO data-driven SF is the standard TOP-POG parameterisation
# (https://twiki.cern.ch/twiki/bin/view/CMS/TopPtReweighting):
#     SF(pT) = exp(a + b * pT)   per top quark, with the event weight the
#     geometric mean sqrt(SF(t) * SF(tbar)).
# We use the data-based fit values a = 0.0615, b = -0.0005 (GeV^-1), the
# parameterisation recommended for the "data/NLO" comparison and used widely in
# Run 2 ttbar analyses.
import awkward as ak
import numpy as np


TOP_PT_A = 0.0615
TOP_PT_B = -0.0005  # GeV^-1


def _sf(pt):
    # cap at 500 GeV: the fit is only validated in the measured range and grows
    # unphysically small beyond it.
    pt = ak.where(pt > 500.0, 500.0, pt)
    return np.exp(TOP_PT_A + TOP_PT_B * pt)


def add_toppt_weight(events, weights_container, shift, dataset):
    """Add the top-pT reweighting nuisance for tt samples.

    The nominal weight is left at 1 and the *corrected* distribution is supplied as
    the Up variation (Down mirrored), so the full size of the correction becomes the
    +-1 sigma interval -- the AN-24-091 convention. This keeps the nominal prediction
    un-reweighted, which is what `rate_tt` is fitted against.
    """
    if shift is not None:
        return
    if not dataset.startswith("TT"):
        return
    if "GenPart" not in events.fields:
        print("No GenPart in dataset, skip systematic: top pT reweight")
        return
    try:
        gp = events.GenPart
        # last-copy top quarks: statusFlags bit 13 (isLastCopy)
        is_last = (gp.statusFlags & (1 << 13)) != 0
        tops = gp[(gp.pdgId == 6) & is_last]
        atops = gp[(gp.pdgId == -6) & is_last]

        pt_t = ak.fill_none(ak.firsts(tops.pt), 0.0)
        pt_tb = ak.fill_none(ak.firsts(atops.pt), 0.0)

        # events without a well-defined ttbar pair get no correction
        has_pair = (ak.num(tops) > 0) & (ak.num(atops) > 0)
        w = np.sqrt(_sf(pt_t) * _sf(pt_tb))
        w = ak.where(has_pair, w, 1.0)
        w = ak.to_numpy(ak.values_astype(w, np.float64))

        weights_container.add(
            name="top_pt",
            weight=np.ones(len(events)),
            weightUp=w,
            weightDown=2.0 - w,  # mirror about the nominal
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to build top pT reweight, skipping systematic: {exc}")
