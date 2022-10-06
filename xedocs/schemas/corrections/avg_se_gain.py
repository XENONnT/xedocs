'''
Correction: Average single electron gain
Affects: Corrected areas

Average of the single electron corrections. This correction my also have two partitions as this average is a temporal average not a spatial one.

wiki:
'''

import rframe

from .base_corrections import TimeSampledCorrection
from ..constants import PARTITION

class AvgSEGain(TimeSampledCorrection):
    
    _ALIAS = "avg_se_gain"
    #PARTITION = Literal["all_tpc", "ab", "cd"]
    partition: PARTITION = rframe.Index(default='all_tpc')
    value: float