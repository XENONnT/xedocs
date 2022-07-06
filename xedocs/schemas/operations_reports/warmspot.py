import pydantic
import datetime
from typing import Literal, List
from .base_report import BaseOperationsReport



class WarmspotReport(BaseOperationsReport):
    """Warmspot report
    """

    _ALIAS = "warmspot_reports"
    
    intensity: int = pydantic.Field(lt=11, gt=0)
    pmts: List[int]