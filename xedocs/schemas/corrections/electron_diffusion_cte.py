"""
# Correction: Electron diffusion
# What is it correction: S2 width cut (cutax)
# Description: This correction is to take into account how wide out S2s can be as higher diffusion implies longer S2s. While we do not directly correct our waveforms with this information it is used in cutax for the cut_s2_width cut.
# Latest wiki reference: 
"""

import rframe

from .base_corrections import TimeSampledCorrection


class ElectronDiffusionCte(TimeSampledCorrection):

    _ALIAS = "electron_diffusion_cte"
    value: float
