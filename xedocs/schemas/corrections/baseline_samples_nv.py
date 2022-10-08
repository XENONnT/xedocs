"""
Correction: Baseline Sample neutron veto
Affects: records_nv

Baseline samples get subtracted from the neutron veto records, similar to the baseline we use for processing recrods. There is a separate array corrections that handles the individual thresholds for each light detector in the Neutron veto

wiki:
"""


from .base_corrections import TimeSampledCorrection


class BaselineSamplesNV(TimeSampledCorrection):

    _ALIAS = "baseline_samples_nv"
    value: float
