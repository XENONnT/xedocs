import pydantic
import datetime
from typing import Literal, List
from .base_report import BaseOperationsReport


class HotPmt(pydantic.BaseModel):
    pmt: int = pydantic.Field(lt=494, ge=0)
    avg_rate_kbps: float


class HotReport(BaseOperationsReport):
    """Hotspot report
    """

    _ALIAS = "hotspot_reports"
    
    pmts: List[HotPmt]
