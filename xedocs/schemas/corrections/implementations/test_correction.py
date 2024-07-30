# This will be a correction designed for testing purposes.
# This SHOULD NOT be used in production.

import rframe

from ..base_corrections import TimeSampledCorrection
from ...constants import DETECTOR

class TestCorrection(TimeSampledCorrection):
    _ALIAS = "test_corrections"

    # Here we use a simple indexer (matches on exact value)
    # to define the pmt field
    # this will add the field to all documents and enable
    # selections on the pmt number. Since this is a index field
    # versioning will be indepentent for each pmt

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)

    value: float