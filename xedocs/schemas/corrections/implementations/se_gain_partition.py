"""
Correction: Region linear and circular for AB/Cd partitions
Affects: Corrected areas

Two distinct patterns of evolution of single electron corrections between A+B and C+D. Distinguish thanks to linear and circular regions

SR0 wiki: https://xe1t-wiki.lngs.infn.it/doku.php?id=jlong:sr0_2_region_se_correction
SR1 wiki: https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:noahhood:corrections:se_gain_ee_final
"""

import rframe

from ..base_corrections import TimeIntervalCorrection
from ...constants import PARTITION


class RegionLinear(TimeIntervalCorrection):

    _ALIAS = "region_linear"
    value: float

class RegionCircular(TimeIntervalCorrection):

    _ALIAS = "region_circular"
    value: float
