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
from .contexts import *
from . import database_interface

try:
    from . import _straxen_plugin

except ImportError:
    logger.warning(
        "Could not register straxen protocol, \
                     most likely straxen not installed."
    )
except ValueError:
    pass

try:
    from . import widgets

    gui = widgets.XedocsEditor()
except ImportError:
    logger.warning("Could not import editors, GUI not available.")

try:
    from .entrypoints import load_entry_points

    hooks = load_entry_points("xedocs")

    for name, hook in hooks.items():
        if callable(hook):
            hook()
except Exception as e:
    logger.warning(f"Could not load plugins. Failed with error: {e}")

try:
    from .database_interface import load_db_interfaces

    load_db_interfaces()

except Exception as e:
    logger.warning(f"Could not load database interfaces. Failed with error: {e}")


for schema in xedocs.all_schemas().values():
    try:
        settings.register_databases(schema)
    except Exception as e:
        logger.warning(
            f"Could not load databases for {schema._ALIAS}. Failed with error: {e}"
        )
