
import datetime

import rframe
from pydantic import validator
from typing import Literal

from ..base_schemas import XeDoc
from ..._settings import settings

SOURCE_TYPE = Literal['ambe',
 'ar-37',
 'kr-83m',
 'led',
 'noise',
 'none',
 'rn-220',
 'th-232',]

class BaseCalibration(XeDoc):
    """Base class for calibration metadata
    """
    _ALIAS = ""

    class Config:
        allow_population_by_field_name = True

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias='run_id')
    source: SOURCE_TYPE

    operator: str
    comments: str

    @validator('time', pre=True)
    def run_id_to_time(cls, v):
        """Convert run id to time"""
        if isinstance(v, (str, int)):
            try:
                v = settings.run_id_to_interval(v)
            except:
                pass
        return v


