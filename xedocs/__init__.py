"""Top-level package for xedocs."""

__author__ = """Yossi Mosbacher"""
__email__ = "joe.mosbacher@gmail.com"
__version__ = "0.1.6"

from ast import Import
from ._settings import settings
from ._frames import frames
from . import schemas
from .schemas import *
from .utils import *
from .xedocs import *

try:
    from . import panel_editor
except ImportError:
    pass