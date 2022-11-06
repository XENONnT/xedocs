

import rframe
import datetime

from .base_pmt_data import BasePmtData
from ..constants import DETECTOR


class GainCalculation(BasePmtData):
    _ALIAS = "pmt_gain_calculations"

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)
    time: datetime.datetime = rframe.Index()

    voltage: float
    gain: float
    gain_error: float
    gain_stat_error: float
    gain_sys_error: float
    occupancy: float
    occupancy_error: float
