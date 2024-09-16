from typing import Literal
from .base_report import BaseOperationsReport

class DetectorOperations(BaseOperationsReport):
    """ Detector Operations Reports """

    _ALIAS="detector_operations"

    system:Literal["CRY", "PUR", "LXePUR", "RSX", "RSX_2", "DST", "RAD", "DAQ"]
    subject: str
    