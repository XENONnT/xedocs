"""
id=xenon:xenonnt:analysis:hot_spot_cut_summary
"""

class HotspotVeto(xd.schemas.corrections.TimeIntervalCorrection):
    _ALIAS = 'hotspot_vetos'
    value: float