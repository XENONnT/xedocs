"""
The 'hotspot_veto_threshold' provides a per-run cut threshold of the 'hotspot_veto_cut',
which vetos the events with local single electron rate above the threshold in each run.
Reference: xenon:xenonnt:analysis:hot_spot_cut_summary
"""

from ..base_corrections import TimeIntervalCorrection

class HotspotVetoThreshold(TimeIntervalCorrection):
    _ALIAS = 'hotspot_veto_thresholds'
    value: float
