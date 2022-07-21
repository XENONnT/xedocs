

import rframe
import datetime
from typing import List
from pydantic import Field, BaseModel


from .base_pmt_data import BasePmtData, DETECTOR_TYPE


class VoltageChange(BasePmtData):
    
    detector: DETECTOR_TYPE = rframe.Index()
    pmt: int = rframe.Index(ge=0)
    time: datetime.datetime = rframe.Index()

    old_voltage: float
    new_voltage: float
    operator: str = Field(max_length=60)
    comments: str