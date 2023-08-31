"""
# cS2 AFT
Due to photoionizations, the cS2_bottom has a time-dependent charge yield.

https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:zihao:sr1_s2aft_photonionization_correction

"""

from .base_corrections import TimeSampledCorrection


class cS2AFTCorrection(TimeSampledCorrection):
    _ALIAS = "cs2_aft_corrections"
    value: float
    