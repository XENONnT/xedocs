import rframe

from .base_pmt_data import BasePmtData


class Pmt(BasePmtData):
    _ALIAS = "pmts"

    serial_number: str = rframe.Index(max_length=60)
    manufacturer: str = rframe.Index(max_length=60)
    location: str
    datasheet: str = ""
    comments: str = ""
