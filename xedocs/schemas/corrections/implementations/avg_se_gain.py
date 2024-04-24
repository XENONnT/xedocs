"""
This schema incorporates two iece of inforamtion for the SEG & EE correciont. Namely the average single electron gain
and the definition of the AB and CD partitions

Correction: Average single electron gain
Affects: Corrected areas

Average of the single electron corrections. This correction my also have two partitions as this average is a temporal average not a spatial one.

Correction: Region linear and circular for AB/CD partitions
Affects: Corrected areas

Two distinct patterns of evolution of single electron corrections between A+B and C+D. Distinguish thanks to linear and circular regions
SR0 wiki: https://xe1t-wiki.lngs.infn.it/doku.php?id=jlong:sr0_2_region_se_correction
SR1 wiki: https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:noahhood:corrections:se_gain_ee_final

"""

import rframe

from ..base_corrections import TimeIntervalCorrection
from ...constants import PARTITION


class AvgSingleElectronGain(TimeIntervalCorrection):

    _ALIAS = "avg_se_gains"
    field: str = rframe.Index(max_length=80)
    partition: PARTITION = rframe.Index(default="all_tpc")
    
    value: float
