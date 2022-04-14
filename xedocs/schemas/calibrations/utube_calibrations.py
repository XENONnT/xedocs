
import datetime
from typing import List, Literal

import rframe
from pydantic import validator

from .base_calibrations import BaseCalibation


class UtubeCalibation(BaseCalibation):
    """Calibrations performed inside the utube
    """

    _ALIAS = "utube_calibrations"

    tube: Literal['top','bottom'] = rframe.Index()
    direction: Literal['cw','ccw'] = rframe.Index()

    depth_cm: float
