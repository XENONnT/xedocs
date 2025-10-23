"""
# Correction: Relative charge yield
# What is it correction: Corrected areas (cS2)

# Description: Correction done to the area of cS2s in our detector. The relative charge yield corresponds to the number of electrons released by an interaction per energy. This correction helps us convert from the number of electrons observed in an S2 event to an energy.

# Latest wiki reference: https://xe1t-wiki.lngs.infn.it/doku.php?id=caio:analysis:sr2:v18.5_relative_cy_map

"""


import rframe

from ..base_corrections import TimeSampledCorrection


class RelativeChargeYield(TimeSampledCorrection):

    _ALIAS = "relative_charge_yield"
    value: float
