import datetime
from pydantic import conint
from typing import Literal
from .base_calibrations import BaseCalibration
from ..constants import DIFFUSED_SOURCE


class DiffusedCalibration(BaseCalibration):
    """Internal diffused Calibrations"""

    _ALIAS = "diffused_calibrations"

    source: DIFFUSED_SOURCE

    nv_ticks: conint(ge=0)
    valve_opened: datetime.datetime
    valve_closed: datetime.datetime
