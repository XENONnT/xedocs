"""
Correction: Single Electron Gain
Affects: Corrected Areas

The single electron gain is a correction which affects the corrected S2 signals. It discribes the number of photons produced by a single electron (corresponding to an S2 signal).

Wiki:
"""

import rframe

from .base_corrections import TimeSampledCorrection
from ..constants import PARTITION

class SEGain(TimeSampledCorrection):
    #from typing import Literal
    
    _ALIAS = "se_gain"
    partition: PARTITION = rframe.Index(default='all_tpc')
    value: float