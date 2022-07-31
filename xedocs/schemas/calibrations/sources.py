import datetime

import rframe
from pydantic import validator, BaseModel, constr
from typing import Literal, List

from ..base_schemas import XeDoc
from ..._settings import settings
from ..constants import SOURCE


class ActivityMeasurement(BaseModel):
    time: datetime.datetime
    activity: float
    uncertainty: float
    units: constr(max_length=10) = "Bq"


class CalibrationSource(XeDoc):
    _ALIAS = "calibration_sources"
    _CATEGORY = "calibration"

    source_id: str = rframe.Index(max_length=50)
    lngs_id: constr(max_length=30)
    kind: SOURCE
    ref: str
    comments: str

    activity_measurements: List[ActivityMeasurement]
