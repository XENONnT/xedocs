
import rframe

from .base_schemas import VersionedXeDoc


class ContextConfig(VersionedXeDoc):
    _ALIAS = "context_configs"

    config_name: str = rframe.Index()
    value: str

    