import datetime
import pydantic
import rframe
import pandas as pd
from pydantic import root_validator, validator
from typing import List
from rframe.types import TimeInterval

from ..base_schemas import XeDoc
from ..._settings import settings

from ..constants import SOURCE


class BaseCalibration(XeDoc):
    """Base class for calibration metadata"""

    _ALIAS = ""
    _CATEGORY = "calibration"

    class Config:
        allow_population_by_field_name = True

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex()
    source_id: str = rframe.Index(min_length=1, max_length=60)

    source_type: SOURCE

    operator: str = pydantic.Field(min_length=1, max_length=60, default="")
    comments: str = ""
    run_ids: List[str] = []
    filled_by: str = pydantic.Field(min_length=1, max_length=60, default="")


    @validator("time", pre=True)
    def time_string_to_interval(cls, v):
        """Convert str to time interval"""
        if isinstance(v, str):
            try:
                if "," in v:
                    left, right = v.split(",")
                    left, right = pd.to_datetime(left), pd.to_datetime(right)
                    v = TimeInterval(left=left, right=right)
                else:
                    v = pd.to_datetime(v)
            except:
                pass
        return v

    @root_validator(pre=True)
    def run_id_to_time_interval(cls, values):
        if "run_id" in values:
            run_id = values.pop("run_id")
            try:
                values["time"] = settings.run_id_to_interval(run_id)
            except:
                values["time"] = run_id
        return values
