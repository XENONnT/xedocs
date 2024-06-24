"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.2.29"


import logging

logger = logging.getLogger(__name__)


from ._settings import settings
from . import utils
from . import schemas
from . import data_locations
from . import databases
from .xedocs import *
from .databases import *

try:
    from . import _straxen_plugin
    del _straxen_plugin
except ImportError:
    logger.warning(
        "XEDOCS: Could not register straxen protocol, \
                     most likely straxen not installed."
    )

except ValueError:
    pass

try:
    from . import widgets

    gui = widgets.XedocsEditor()
except ImportError:
    logger.debug("XEDOCS: Could not import editors, GUI not available.")

try:
    from .entrypoints import load_entry_points

    hooks = load_entry_points("xedocs")

    for name, hook in hooks.items():
        if callable(hook):
            hook()
except Exception as e:
    logger.warning(f"XEDOCS: Could not load plugins. Failed with error: {e}")
