"""
Algorithm which uses a pretrained weightcube from the output of a 
Self-Organizing Map to classify peaklets as one of several SOM_types,
as well as classifying those types into either an S1 or an S2
"""

from ..base_references import BaseResourceReference


class SOMClassifier(BaseResourceReference):
    _ALIAS = 'som_classifiers'
    fmt = 'binary'
    
    value: str
    
