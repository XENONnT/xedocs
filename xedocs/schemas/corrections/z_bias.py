"""
The 'z_bias_map' calculate the z correction due to non-uniform drift velocity based on
the observed r(r_obs) and z(z_obs).

Reference: xenon:xenonnt:terliuk:drift_field_z_bias_correction
"""

from .base_corrections import TimeIntervalCorrection

class ZBias(TimeIntervalCorrection):
    _ALIAS = 'z_bias_map'
