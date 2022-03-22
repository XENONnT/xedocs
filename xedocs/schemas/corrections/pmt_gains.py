from typing import Literal

import rframe

from .base_corrections import TimeSampledCorrection


class PmtGain(TimeSampledCorrection):
    _NAME = "pmt_gains"

    # Here we use a simple indexer (matches on exact value)
    # to define the pmt field
    # this will add the field to all documents and enable
    # selections on the pmt number. Since this is a index field
    # versioning will be indepentent for each pmt

    detector: Literal["tpc", "nveto", "muveto"] = rframe.Index()
    pmt: int = rframe.Index()

    value: float
