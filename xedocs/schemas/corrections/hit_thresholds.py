"""
# TPC PMT hitfinder thresholds
`hit_thresholds` are the per-channel thresholds in unit of ADC to define a hit in `strax`, and they should be updated while DAQ thresholds and noise condition change. This folder contains essential info and source codes of `straxen` hit thresholds for TPC PMTs (both normal channels and high energy channels) and Neutron Veto PMTs. `hitfinder_thresholds.py` in this folder contains the thresholds of different versions. 

"""

import rframe

from .base_corrections import TimeSampledCorrection
from ..constants import DETECTOR


class HitThreshold(TimeSampledCorrection):
    _ALIAS = "hit_thresholds"
    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index()

    value: int
