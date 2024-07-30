# This will be a correction designed for testing purposes.
# This SHOULD NOT be used in production.

import rframe

from ..base_corrections import TimeSampledCorrection
from ...constants import DETECTOR

class TestCorrection(TimeSampledCorrection):
    _ALIAS = "test_corrections"

    # Correction identical to PMT gains.
    # Used for testing

    detector: DETECTOR = rframe.Index()
    pmt: int = rframe.Index(ge=0)

    value: float
