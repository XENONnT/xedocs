import pydantic
import datetime
from typing import Literal, List
from .base_report import BaseOperationsReport


class WarmPmt(pydantic.BaseModel):
    pmt: int = pydantic.Field(lt=494, ge=0)
    avg_rate_kbps: float


class WarmspotReport(BaseOperationsReport):
    """Warmspot report
    """

    _ALIAS = "warmspot_reports"
    
    pmts: List[WarmPmt]
