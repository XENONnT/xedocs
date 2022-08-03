import rframe
import datetime

from .base_schemas import VersionedXeDoc
from .constants import PARTITION

class Bodega(VersionedXeDoc):
    """Detector parameters
    A collection of non-time dependent detector
    values.
    """

    _ALIAS = "bodega"

    field: str = rframe.Index(max_length=80)
    partition: PARTITION = rframe.Index(default='all_tpc')

    value: float
    uncertainty: float
    definition: str
    reference: str = ""
    date: datetime.datetime
    comments: str = ""
