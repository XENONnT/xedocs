
import rframe
import datetime
from typing import Optional
from pydantic import Field


from .base_pmt_data import BasePmtData
from ..constants import DETECTOR


class PmtInstall(BasePmtData):
    _ALIAS = "pmt_installs"

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)
    array: str = rframe.Index()
    sector: str = rframe.Index()
    time: datetime.datetime = rframe.Index()

    serial_number: str = Field(max_length=60)

    position_x: float
    position_y: float
    position_z: Optional[float]

    signal_channel: Optional[int]
    signal_connector: Optional[int]
    signal_feedthrough: Optional[str]

    amplifier_crate: Optional[int]
    amplifier_fan: Optional[int]
    amplifier_plug: Optional[int]
    amplifier_serial: Optional[int]
    amplifier_slot: Optional[int]
    amplifier_channel: Optional[int]

    digitizer_channel: Optional[int]
    digitizer_crate: Optional[int]
    digitizer_module : Optional[int]
    digitizer_slot: Optional[int]

    high_voltage_crate: Optional[int]
    high_voltage_board: Optional[int]
    high_voltage_channel: Optional[int]
    high_voltage_connector: Optional[int]
    high_voltage_feedthrough: Optional[str]
    high_voltage_return: Optional[int]
