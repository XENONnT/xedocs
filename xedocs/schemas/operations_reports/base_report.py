import datetime
import pandas as pd
import pydantic
import rframe
from rframe.types import TimeInterval
from pydantic import root_validator, validator

from ..base_schemas import XeDoc
from ..._settings import settings


class BaseOperationsReport(XeDoc):
    """Base class for operations report metadata"""

    _ALIAS = ""
    _CATEGORY = "operations"

    class Config:
        allow_population_by_field_name = True

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex()

    operator: str = pydantic.Field(min_length=1, max_length=60)
    comments: str

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
