"""
# S1 area-fraction top (AFT) (x,y,z) map
S1 area fraction top data driven map used for event_patternfit within straxen. The map is data-driven and depends on the PMT Gains and other observables. Should be treated like a normal correction for dependencies and should be updated last for each global version.

"""

import rframe

from .base_references import TimeIntervalCorrection

class S1AFTXYZMap(TimeIntervalCorrection):
    _ALIAS = "s1_aft_xyz_maps"
    
    value: str
    version: str = rframe.Index()