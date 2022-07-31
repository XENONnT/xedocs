import datetime
import pydantic
import rframe
from pydantic import validator

from ..base_schemas import XeDoc
from ..._settings import settings


class BaseOperationsReport(XeDoc):
    """Base class for operations report metadata"""

    _ALIAS = ""
    _CATEGORY = "operations"

    class Config:
        allow_population_by_field_name = True

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias="run_id")

    operator: str = pydantic.Field(min_length=1, max_length=60)
    comments: str

    @validator("time", pre=True)
    def run_id_to_time(cls, v):
        """Convert run id to time"""
        if isinstance(v, (str, int)):
            try:
                v = settings.run_id_to_interval(v)
            except:
                pass
        return v
