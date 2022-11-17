"""

"""
import datetime
from typing import Literal
import rframe

from .base_references import BaseResourceReference

class NaiveBayesClassifier(BaseResourceReference):
    _ALIAS = "bayes_models"
    fmt = "binary"
    
    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex()
    value: str
