from typing import Literal

import rframe

from .base_calibrations import BaseCalibration


class UtubeCalibration(BaseCalibration):
    """Calibrations performed inside the utube"""

    _ALIAS = "utube_calibrations"

    tube: Literal["top", "bottom"] = rframe.Index()
    direction: Literal["cw", "ccw"] = rframe.Index()

    depth_cm: float
