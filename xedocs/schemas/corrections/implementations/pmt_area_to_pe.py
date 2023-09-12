    # represents a correction factor for converting PMT
    # (photomultiplier tube) area to photoelectrons (PE). It is a subclass of
    # `TimeSampledCorrection`, which means that it is a correction that varies with time.
    # The class has fields for `detector`, `pmt`, and `value`. The `detector` field is an
    # index field that specifies the detector (tpc/neutron_veto/muon_veto), while the `pmt` field is an index field
    # that specifies the PMT number. The `value` field is a float that represents the
    # correction factor. (Previously known as gain_models)

import rframe

from ..base_corrections import TimeSampledCorrection
from ...constants import DETECTOR


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
