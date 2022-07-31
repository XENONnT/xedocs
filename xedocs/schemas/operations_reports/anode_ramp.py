from typing import Literal
from .base_report import BaseOperationsReport


class AnodeRampReport(BaseOperationsReport):
    """Anode ramp - report"""

    _ALIAS = "anode_ramps"

    direction: Literal["up", "down"]
    starting_voltage: float
    final_voltage: float
    voltage_unit: str = "volts"
