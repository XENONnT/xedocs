import pydantic
import datetime
from typing import Literal, List
from .base_report import BaseOperationsReport


class LevelChange(pydantic.BaseModel):
    time: datetime.datetime
    liquid_level: float = pydantic.Field(lt=8, ge=0)


class AnodeWashingReport(BaseOperationsReport):
    """Anode washing report"""

    _ALIAS = "anode_washes"

    washes: List[LevelChange]
