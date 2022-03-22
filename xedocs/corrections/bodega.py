

import rframe
import datetime

from .base_corrections import BaseCorrectionSchema



class Bodega(BaseCorrectionSchema):
    '''Detector parameters
       A collection of non-time dependent detector
       values.
    '''
    _NAME = 'bodega'
    
    field: str = rframe.Index()

    value: float
    uncertainty: float
    definition: str
    reference: str
    date: datetime.datetime

