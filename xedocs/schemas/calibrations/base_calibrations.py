
import datetime
import pydantic
import rframe
from pydantic import validator
from typing import Literal

from ..base_schemas import XeDoc
from ..._settings import settings

from ..constants import SOURCE

class BaseCalibration(XeDoc):
    """Base class for calibration metadata
    """
    _ALIAS = ""
    _CATEGORY = "calibration"

    class Config:
        allow_population_by_field_name = True

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias='run_id')
    source_id: str = rframe.Index(min_length=1, max_length=60)

    source_type: SOURCE

    operator: str = pydantic.Field(min_length=1, max_length=60)
    comments: str = ''

    @validator('time', pre=True)
    def run_id_to_time(cls, v):
        """Convert run id to time"""
        if isinstance(v, (str, int)):
            try:
                v = settings.run_id_to_interval(v)
            except:
                pass
        return v
