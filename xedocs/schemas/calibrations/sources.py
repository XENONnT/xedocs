
import datetime

import rframe
from pydantic import validator, BaseModel
from typing import Literal, List

from ..base_schemas import XeDoc
from ..._settings import settings


class ActivityMeasurement(BaseModel):
    time: datetime.datetime
    activity: float
    uncertainty: float
    units: str


class CalibrationSource(XeDoc):
    _ALIAS = 'calibration_sources'
    
    source_id: str = rframe.Index()
    lngs_id: str
    kind: str
    ref: str
    activity_measurements: List[ActivityMeasurement]
