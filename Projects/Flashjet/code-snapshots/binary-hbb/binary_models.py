"""Binary Hbb-vs-QCD variants of the paper ParT and PLuM arms.

Reproduces Gouskos & Maier's setup on the task axis: they train BINARY taggers
("50 epochs in binary classification mode"), 8M signal + 8M background per epoch.

THE TRAP THIS AVOIDS
--------------------
LZ4Dataset assigns `truths = np.zeros(...)` and then only reassigns rows whose
label is in `model_classes`.  With a 2-entry classes dict the other EIGHT signal
classes (Hcc, Hgg, H4q, Hqql, Zqq, Wqq, Tbqq, Tbl) would silently be labelled
QCD -- a background 9x contaminated with other signals, which is NOT the paper's
task and would give a meaningless rejection number.

So these classes pair with BinaryFilteredLZ4Dataset, which DROPS rows that are
neither the signal class nor QCD before any truth assignment happens.
"""
from utils.models.particletransformer_paper import ParticleTransformer_Paper_JetClass
from utils.models.particletransformer_plum import ParticleTransformer_PLuM_JetClass


class ParticleTransformer_Paper_JetClass_HbbBinary(ParticleTransformer_Paper_JetClass):
    """Paper ParT, binary Hbb vs QCD."""
    classes = {"QCD": ["label_QCD"], "Hbb": ["label_Hbb"]}

    def __init__(self, config, *args, num_classes=2, **kwargs):
        kwargs.pop("num_classes", None)
        super().__init__(config, *args, num_classes=2, **kwargs)


class ParticleTransformer_PLuM_JetClass_HbbBinary(ParticleTransformer_PLuM_JetClass):
    """PLuM (48 kT Lund tokens), binary Hbb vs QCD."""
    classes = {"QCD": ["label_QCD"], "Hbb": ["label_Hbb"]}

    def __init__(self, config, *args, num_classes=2, **kwargs):
        kwargs.pop("num_classes", None)
        super().__init__(config, *args, num_classes=2, **kwargs)
