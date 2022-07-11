import datetime
from pydantic import conint
from typing import Literal
from .base_calibrations import BaseCalibration

DIFFUSED_SOURCE_TYPE = Literal['rn-220','kr-83m','ar-37']


class DiffusedCalibration(BaseCalibration):
    """Internal diffused Calibrations
    """

    _ALIAS = "diffused_calibrations"

    source: DIFFUSED_SOURCE_TYPE

    nv_ticks: conint(ge=0)
    valve_opened: datetime.datetime
    valve_closed: datetime.datetime
