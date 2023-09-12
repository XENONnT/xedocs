"""
# Photoionization strengths
https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt_sr1:photoionization_origin
"""

from ..base_corrections import TimeSampledCorrection


class PhotoionizationStrength(TimeSampledCorrection):
    _ALIAS = "photoionization_strengths"
    value: float
