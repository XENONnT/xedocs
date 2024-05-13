import rframe
import datetime

from .corrections.base_corrections import TimeIntervalCorrection
from .constants import PARTITION

class DetectorNumber(TimeIntervalCorrection):
    """Detector parameters
    A collection of non-time dependent detector
    values.
    """

    _ALIAS = "detector_numbers"

    field: str = rframe.Index(max_length=80)
    partition: PARTITION = rframe.Index(default="all_tpc")
    science_run: str = rframe.Index(max_length=80)
    definition: str=""
    value: float
    uncertainty: float
    reference: str = ""
