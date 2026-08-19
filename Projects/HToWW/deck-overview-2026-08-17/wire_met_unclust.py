"""Wire the MET-unclustered-energy shift for Run 3 PuppiMET.

The existing gate looks for `MET_UnclusteredEnergy` in met.fields, which is the
CorrectedMETFactory/PF-MET convention. Run 3 takes the PuppiMET branch (line ~196),
which builds MET by hand via corrected_polar_met and never calls the factory -- so
that field is never attached and the shift could never fire.

NanoAODv12 ships the variation directly as PuppiMET_pt/phiUnclusteredUp/Down, so we
attach it from the branches instead of recomputing it.
"""
import pathlib

p = pathlib.Path("/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm/analysis/corrections/jerc.py")
s = p.read_text()

# 1) attach the unclustered variations onto the hand-built PuppiMET object
old_build = """        met["orig_pt"], met["orig_phi"] = nocorrmet["pt"], nocorrmet["phi"]"""
new_build = """        met["orig_pt"], met["orig_phi"] = nocorrmet["pt"], nocorrmet["phi"]
        # NanoAODv12 ships the unclustered-energy variation as ready-made branches on
        # PuppiMET. The CorrectedMETFactory path below never runs for Run 3, so the
        # `MET_UnclusteredEnergy` field the shift loop looks for is never attached --
        # take the branches directly instead. (AN-23-102 Table 16: MET unclustered.)
        if "ptUnclusteredUp" in nocorrmet.fields:
            unclust = {}
            for _dirn, _suf in (("up", "Up"), ("down", "Down")):
                _v = copy.copy(met)
                _v["pt"] = ak.values_astype(
                    nocorrmet[f"ptUnclustered{_suf}"], np.float32
                )
                _v["phi"] = ak.values_astype(
                    nocorrmet[f"phiUnclustered{_suf}"], np.float32
                )
                unclust[_dirn] = _v
            met["MET_UnclusteredEnergy"] = ak.zip(
                {"up": unclust["up"], "down": unclust["down"]}, depth_limit=1
            )"""
assert old_build in s, "build anchor not found"
s = s.replace(old_build, new_build)

p.write_text(s)
print("patched jerc.py")
