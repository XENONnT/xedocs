
from ..base_schemas import XeDoc


class BasePmtData(XeDoc):
    _ALIAS = ""
    _CATEGORY = "pmt_data"

    @classmethod
    def default_database_name(cls):
        return "xepmts"
