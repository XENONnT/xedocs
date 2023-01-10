from abc import ABC, abstractmethod
from rframe import DataAccessor

from .schemas import XeDoc
from ._settings import settings


class DatabaseInterface(ABC):
    priority = -1

    @abstractmethod
    def datasource_for_schema(schema: XeDoc):
        pass

    def __getitem__(self, key):
        schema = XeDoc._XEDOCS.get(key, None)
        if schema is None:
            raise KeyError(f"No schema named {key} found")

        source = self.datasource_for_schema(key)
        if source is None:
            raise KeyError(f"No datasource for {key} found")

        return DataAccessor(schema, source)

    def __getattr__(self, attr):
        if attr in XeDoc._XEDOCS.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return list(XeDoc._XEDOCS.keys()) + super().__dir__()


def load_db_interfaces():

    from .entrypoints import load_entry_points

    hooks = load_entry_points("xedocs_db_interfaces")

    for name, hook in hooks.items():
        if isinstance(hook, type) and issubclass(hook, DatabaseInterface):
            settings.register_database_interface_class(name, hook)
