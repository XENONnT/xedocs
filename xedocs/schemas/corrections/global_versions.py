import rframe

from .base_corrections import TimeIntervalCorrection


class GlobalVersion(TimeIntervalCorrection):
    _ALIAS = "global_versions"

    config_name: str = rframe.Index(max_length=80)

    url: str
