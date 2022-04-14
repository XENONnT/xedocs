
import datetime
from typing import List, Literal

import rframe
from pydantic import validator

from ..base_schemas import XeDoc
from ..._settings import settings

class UtubeCalibation(XeDoc):
    """Calibrations performed inside the utube
    """
    class Config:
        allow_population_by_field_name = True

    _ALIAS = "utube_calibrations"

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias='run_id')
    source: str = rframe.Index()
    tube: Literal['top','bottom'] = rframe.Index()
    direction: Literal['cw','ccw'] = rframe.Index()

    depth_cm: float
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
