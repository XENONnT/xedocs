from collections import defaultdict


from rframe import DataAccessor
from xedocs import all_schemas
from xedocs.storage import ApiStorage, DictStorage, UtilixStorage
from xedocs.xedocs import find_schema

from .utils import DatasetCollection
from .schemas import XeDoc

from ._settings import settings


class XedocsContext:
    _schemas: dict
    storage: list
    _accessors: dict

    def __init__(self, schemas: dict = None, storage=None, by_category=True):
        if by_category:
            self._accessors = defaultdict(dict)
        else:
            self._accessors = {}

        if storage is None:
            storage = []
        self.storage = storage

        if schemas is None:
            schemas = all_schemas()

        for name, schema in schemas.items():
            if by_category:
                category = schema._CATEGORY
            else:
                category = None
            self.register_schema(schema, name=name, category=category)

    def register_schema(self, schema, name=None, category=None):
        if isinstance(schema, str):
            schema = find_schema(schema)

        if not issubclass(schema, XeDoc):
            raise TypeError(
                "Wrong type for schema spec, "
                f"expected a XeDoc or string got {type(schema)}"
            )

        if name is None:
            name = schema._ALIAS

        datasource = self.get_accessor(schema, name=name)

        if datasource is None:
            raise ValueError(f"No datasource found for {name}")

        if category is None:
            self._accessors[name] = datasource
        else:
            self._accessors[category][name] = datasource

    def get_accessor(self, schema, name=None):
        if name is None:
            name = schema._ALIAS
        for store in self.storage:
            datasource = store.get_datasource(name)
            if datasource is not None:
                return DataAccessor(schema, datasource)

    def __getitem__(self, key):
        dset = self._accessors.get(key, None)
        if dset is None:
            raise KeyError(f"No dataset named {key} found")
        if isinstance(dset, dict):
            return DatasetCollection(dset)
        return self._accessors.get(key)

    def __getattr__(self, attr):
        if attr in self._accessors.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return super().__dir__() + list(self._accessors.keys())


def production_db(schemas=None, datasource_overrides=None, by_category=False):
    if schemas is None:
        schemas = all_schemas()

    storage = [
        DictStorage(datasource_overrides),
        UtilixStorage(database=settings.PRODUCTION_DB),
        ApiStorage(mode='production'),
    ]

    return XedocsContext(storage=storage, schemas=schemas, by_category=by_category)


def staging_db(schemas=None, datasource_overrides=None, by_category=False):
    if schemas is None:
        schemas = all_schemas()

    storage = [
        DictStorage(datasource_overrides),
        UtilixStorage(database="xedocs"),
        ApiStorage(mode='staging'),
    ]

    return XedocsContext(storage=storage, schemas=schemas, by_category=by_category)
