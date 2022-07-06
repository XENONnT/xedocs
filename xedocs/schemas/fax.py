from typing import Literal, Union

import rframe

from .base_schemas import VersionedXeDoc


class FaxConfig(VersionedXeDoc):
    """fax configuration values for WFSim"""

    _ALIAS = "fax_configs"

    class Config:
        smart_union = True

    field: str = rframe.Index()
    experiment: Literal["1t", "nt", "nt_design"] = rframe.Index(default="nt")
    detector: Literal["tpc", "muon_veto", "neutron_veto"] = rframe.Index(default="tpc")
    science_run: str = rframe.Index()
    version: str = rframe.Index(default="v1")

    value: Union[int, float, bool, str, list, dict]
    resource: str
