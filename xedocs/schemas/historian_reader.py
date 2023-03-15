
from typing import Literal
import rframe
from .base_schemas import XeDoc
from pydantic import validator


class HistorianTag(XeDoc):
    """Schema for historian tags to read into influxdb for grafana
    """
    _ALIAS = "historian_tags"
    _CATEGORY = "operations"

    tag_name: str = rframe.Index() # this is the tag name to read from in the historian
    measurement_name: str = rframe.Index() # this is the measurement name to use in influxdb
    bucket_name: str = rframe.Index() # this is the bucket name to use in influxdb
    
    description: str = ""
    
    query_type: Literal["LAB","RAWBYTIME"] = "LAB"
    query_interval: int = 1 # in seconds
    
    category: str = ""
    subsystem: str = ""


    @validator("measurement_name")
    def validate_measurement_name(cls, v, values):
        if v is None:
            v = values["tag_name"]
        return v
