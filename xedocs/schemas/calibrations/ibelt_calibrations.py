
from typing import Literal

import rframe

from .base_calibrations import BaseCalibation


class IbeltCalibation(BaseCalibation):
    """Calibrations performed inside the utube
    """

    _ALIAS = "ibelt_calibrations"

    z_cm: float
    plug: bool
