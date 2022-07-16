import rframe
import datetime

from .base_schemas import VersionedXeDoc


class Bodega(VersionedXeDoc):
    """Detector parameters
    A collection of non-time dependent detector
    values.
    """

    _ALIAS = "bodega"

    field: str = rframe.Index(max_length=50)

    value: float
    uncertainty: float
    definition: str
    reference: str = ''
    date: datetime.datetime
