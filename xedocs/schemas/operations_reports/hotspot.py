import pydantic
import datetime
from typing import Literal, List
from .base_report import BaseOperationsReport


class PmtRate(pydantic.BaseModel):
    pmt: int = pydantic.Field(lt=494, ge=0)
    avg_rate_kbps: float


class HotspotReport(BaseOperationsReport):
    """Hotspot report"""

    _ALIAS = "hotspot_reports"
    severity: Literal["hotspot", "warmspot"] = "hotspot"
    anode_voltage_kv: float
    disppeared_by_itself: bool
    action_taken: str
    plot: str

    pmt_rates: List[PmtRate]
