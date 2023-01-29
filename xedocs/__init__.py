"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.2.10"


import logging

logger = logging.getLogger(__name__)


from ._settings import settings
from . import utils

from . import schemas
from . import xedocs
from .xedocs import *
from . import api
from . import database_interface

__all__ = [
    "settings",
    "utils",
    "schemas",
] + xedocs.__all__

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


def __getattr__(name: str):
    if name in settings.DATABASES:
        interfaces = settings.database_interfaces(name)
        return utils.DatasetCollection(interfaces)
    raise AttributeError(name)


def __dir__():
    return list(settings.DATABASES) + __all__
