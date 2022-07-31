import rframe
import datetime
from typing import List
from pydantic import Field, BaseModel


from .base_pmt_data import BasePmtData
from ..constants import DETECTOR


class VoltageChange(BasePmtData):

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)
    time: datetime.datetime = rframe.Index()

    old_voltage: float
    new_voltage: float
    operator: str = Field(max_length=60)
    comments: str
