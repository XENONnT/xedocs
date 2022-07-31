import rframe
import datetime
from typing import List
from pydantic import Field, BaseModel


from .base_pmt_data import BasePmtData
from ..constants import DETECTOR


class VoltageSetting(BasePmtData):
    _ALIAS = "voltage_settings"

    name: str = rframe.Index(min_length=4, max_length=60)
    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)

    active: bool = True
    created_by: str
    comments: str
    created_date: datetime.datetime

    voltage: float
