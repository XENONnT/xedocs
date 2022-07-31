from .base_calibrations import BaseCalibration


class IbeltCalibation(BaseCalibration):
    """Calibrations performed inside the utube"""

    _ALIAS = "ibelt_calibrations"

    z_cm: float
    plug: bool
