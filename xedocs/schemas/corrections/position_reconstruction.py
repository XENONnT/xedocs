"""
# Position reconstruction with NNs or Likelihoods
Inspired by impressive process in AI industry, we performed deep-learning based approach for position reconstruction. It so far is the fastest reconstruction algorithm, and is less sensitive to the imperfect input pattern. We have a working version of neural network for XENONnT already, but we need someone to optimize it when simulation/data is updated.

In theory, maximum likelihood is the best discriminator for inference. Hence Likelihood-Fitter has always been one of the approach we used to reconstruct position. In XENONnT we will try to improve the likelihood.

See description in the Team C overview page [here](https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:analysis:reconstruction_team#position_reconstruction_with_neural_network) and [here](https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:analysis:reconstruction_team#maximum_likelihood_fitter)

Mostly following the "OFF PMTs" list [here](https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:dsg:pmt:gains:pmtsoff)


"""

import datetime
from typing import Literal

import rframe

from .base_references import BaseResourceReference


class PosRecModel(BaseResourceReference):
    _ALIAS = "posrec_models"
    fmt = "binary"

    kind: Literal["cnn", "gcn", "mlp"] = rframe.Index()

    value: str
