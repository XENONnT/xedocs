import pydantic
import datetime
from typing import Literal
from .base_report import BaseOperationsReport



class AnodeRampReport(BaseOperationsReport):
    """Anode ramp- report
    """

    _ALIAS = "anode_ramp_reports"
    
    direction: Literal['up','down']
