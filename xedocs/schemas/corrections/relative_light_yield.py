'''
# Correction: Relative light yield
# What is it correction: Corrected areas (cS1)

# Description: Correction done to the area of S1s in our detector. The relative light yield corresponds to the number of photons in the visible light spectrum released by an interaction per energy. This correction helps us convert from the number of photons observed in an S1 event to an energy.

# Latest wiki reference: 

'''


import rframe

from .base_corrections import TimeSampledCorrection

class RelativeLightYield(TimeSampledCorrection):
    
    _ALIAS = "relative_light_yield"
    value: float 