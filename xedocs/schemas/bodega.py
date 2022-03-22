import datetime

import rframe

from .base_schemas import XeDoc


class Bodega(XeDoc):
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
