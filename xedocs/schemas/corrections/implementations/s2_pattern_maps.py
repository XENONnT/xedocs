"""

The pattern likelihood cut defined in SR0 was defined with a data-driven S2 map and a Gaussian 
smeared likelihood definition, using the Tensorflow framework. The data-driven S2 map is trained 
using a neural network, using S2 optical Monte Carlo simulation as an initial guess, to best-fit 
event_area_per_channel. Details can be found in the SR0 note. As the SR0 method relied on trainable 
parameters for each PMT the S2 pattern likelihood needs to be retrained to reflect the changed PMT list in SR1.

SR0 S2 pattern map note
https://xe1t-wiki.lngs.infn.it/doku.php?id=shenyang:s2_pattern_likelihood (Shenyang)

SR1 S2 pattern map note
https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenon1t:jacques:nt_sr1_s2pl (Jacques)


"""

from ..base_references import BaseMap


class S2PatternMap(BaseMap):
    _ALIAS = "s2_pattern_maps"
    fmt = "binary"
