
from datetime import datetime
from .base_calibrations import BaseCalibation


class InternalCalibation(BaseCalibation):
    """Internal diffused Calibrations
    """

    _ALIAS = "internal_calibrations"

    valve_opened: datetime.datetime
    valve_closed: datetime.datetime
