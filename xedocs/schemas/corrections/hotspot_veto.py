"""
id=xenon:xenonnt:analysis:hot_spot_cut_summary
"""

from .base_corrections import TimeIntervalCorrection

class HotspotVeto(TimeIntervalCorrection):
    _ALIAS = 'hotspot_vetos'
    value: float
