from typing import Any, Dict

import pytz
import rframe

from rframe import RemoteFrame

from .schemas import XeDoc
from ._settings import settings


class SchemaFrames:
    _cache: Dict[str, RemoteFrame] = {}
    db: Any

    def __init__(self, db=None):
        self.db = db

    @classmethod
    def from_mongodb(cls, url="localhost", db="cmt2", **kwargs):
        import pymongo

        db = pymongo.MongoClient(url, **kwargs)[db]
        return cls(db)

    @property
    def schemas(self):
        return dict(XeDoc._XEDOCS)

    @property
    def schema_names(self):
        return list(self.schemas)

    def get_rf(self, name):
        if name not in self._cache:
            import xedocs

            schema = xedocs.find_schema(name)
            self._cache[name] = schema.rframe()

        return self._cache[name]

    def __getitem__(self, key):
        if isinstance(key, tuple) and key[0] in self.schemas:
            return self.get_rf(key[0])[key[1:]]

        if key in self.schemas:
            return self.get_rf(key)
        raise KeyError(key)

    def __dir__(self):
        return super().__dir__() + list(self.schemas)

    def __getattr__(self, name):
        if name != "schemas" and name in self.schemas:
            return self.get_rf(name)
        return super().__getattribute__(name)

    def sel(self, schema_name, *args, **kwargs):
        return self.get_rf(schema_name).sel(*args, **kwargs)

    def set(self, schema_name, *args, **kwargs):
        return self.get_rf(schema_name).set(*args, **kwargs)

    def insert(self, schema_name, records):
        return self.get_rf(schema_name).insert(records=records)


frames = SchemaFrames()
