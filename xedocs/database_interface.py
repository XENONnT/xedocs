from abc import ABC, abstractmethod
from typing import Iterable
from rframe import DataAccessor
from collections import UserDict

from .schemas import XeDoc
from ._settings import settings
from .utils import DatasetCollection


class DatabaseInterface(ABC):
    @abstractmethod
    def datasource_for_schema(schema: XeDoc):
        pass

    def __getitem__(self, key):
        schema = XeDoc._XEDOCS.get(key, None)
        if schema is None:
            raise KeyError(f"No schema named {key} found")

        source = self.datasource_for_schema(schema)

        if source is None:
            raise KeyError(f"No datasource for {key} found")

        return DataAccessor(schema, source)

    def __getattr__(self, attr):
        if attr in XeDoc._XEDOCS.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return list(XeDoc._XEDOCS.keys()) + super().__dir__()


class DatabasesCollection(UserDict):
    def __getitem__(self, key):
        if key in settings.DATABASES:
            interfaces = settings.database_interfaces(key)
            return DatasetCollection(interfaces)
        raise KeyError(f"No database named {key} found.")

    def __getattr__(self, attr):
        if attr in settings.DATABASES:
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self) -> Iterable[str]:
        return list(settings.DATABASES)


def load_db_interfaces():

    from .entrypoints import load_entry_points

    hooks = load_entry_points("xedocs_db_interfaces")

    for name, hook in hooks.items():
        if isinstance(hook, type) and issubclass(hook, DatabaseInterface):
            settings.register_database_interface_class(name, hook)
