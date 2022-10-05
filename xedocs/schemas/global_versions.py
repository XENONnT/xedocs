import rframe

from .base_schemas import VersionedXeDoc


class GlobalVersion(VersionedXeDoc):
    _ALIAS = "global_versions"

    config_name: str = rframe.Index(max_length=80)
    correction: str = rframe.Index(max_length=80)

    url: str
