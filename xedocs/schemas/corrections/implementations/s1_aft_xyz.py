"""
# S1 AFT (x,y,z) map
S1 area fraction top data driven map used for event_patternfit within straxen. 
The map is data-driven and depends on the PMT Gains and other observables. 
Should be treated like a normal correction for dependencies and should be updated last for each global version.

"""

from ..base_references import BaseResourceReference


class S1AFTXYZMap(BaseResourceReference):
    _ALIAS = "s1_aft_xyz_maps"
    fmt = "json"

    value: str
