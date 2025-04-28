"""
Peak Reconstruction Bias

Atul Prajapati, Carlo Fuselli, Chiara Di Donato

https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xennont:peak_reconstruction_bias_sr2
Description: We know that there are multiple effects that introduce a bias in the reconstructed area. We estimate this bias with simulations produced with fuse. We compare the raw area that is the input, with the reconstrcuted area. We observe that effects like thresholds, afterpulses (AP) and noise introduce an energy dependent bias of the order of 2-3%. We want to provide a correction for the S1 and S2 areas to take these effects into account. Note that photo-ionisation also induces a similar bias, but this topic is not addressed in this notes (for now). 

"""
import rframe

from ..base_references import BaseResourceReference
from ...constants import SIGNAL

class PeakReconstructionBias(BaseResourceReference):
    _ALIAS = "peak_reconstruction_bias"
    fmt = "json"

    signal: SIGNAL = rframe.Index()

    value: str