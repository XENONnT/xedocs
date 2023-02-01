import rframe

from .base_corrections import TimeSampledCorrection
from ..constants import DETECTOR


class PmtAreaToPE(TimeSampledCorrection):
    _ALIAS = "pmt_area_to_pes"

    # Here we use a simple indexer (matches on exact value)
    # to define the pmt field
    # this will add the field to all documents and enable
    # selections on the pmt number. Since this is a index field
    # versioning will be indepentent for each pmt

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)

    value: float
