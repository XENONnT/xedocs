"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.2.7"
import logging

logger = logging.getLogger(__name__)


from ._settings import settings
from .utils import *

from . import schemas
from .xedocs import *
from . import api
from . import datasources
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

try:
    from .entrypoints import load_entry_points
    datasource_hooks = load_entry_points()

    for key, value in datasource_hooks.items():
        XeDoc.register_datasource_hook(key, value)

    del load_entry_points
except Exception as e:
    logger.warning(f"Could not register entrypoints. Failed with error: {e}")
