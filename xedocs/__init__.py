"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.1.23"
import logging

logger = logging.getLogger(__name__)

from ._settings import settings
from ._frames import frames
from . import schemas
from .schemas import *
from .utils import *
from .xedocs import *
from . import api

try:
    from . import widgets

    gui = widgets.XedocsEditor()
except ImportError:
    logger.warning("Could not import editors, GUI not available.")
