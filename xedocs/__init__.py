"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.2.4"
import logging

logger = logging.getLogger(__name__)

from . import api
from ._settings import settings
from .datasources import *
from . import schemas
from .utils import *
from .xedocs import *

from .contexts import *

try:
    from . import _straxen_plugin

except ImportError:
    logger.warning("Could not register straxen protocol, \
                     most likely straxen not installed.")
except ValueError:
    pass

try:
    from . import widgets

    gui = widgets.XedocsEditor()
except ImportError:
    logger.warning("Could not import editors, GUI not available.")
