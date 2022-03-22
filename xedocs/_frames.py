from typing import Any

import pytz
import rframe
import utilix

from .schemas import XeDoc
from ._settings import settings


class SchemaFrames:
    db: Any

    def __init__(self, db=None):
        self.db = db

    @classmethod
    def default(cls, **kwargs):
        try:
            import admix

            return cls.from_utilix(**kwargs)
        except:
            return cls.from_mongodb(**kwargs)

    @classmethod
    def from_mongodb(cls, url="localhost", db="cmt2", **kwargs):
        import pymongo

        db = pymongo.MongoClient(url, **kwargs)[db]
        return cls(db)

    @classmethod
    def from_utilix(cls, experiment="xent", db="cmt2"):
        coll = utilix.rundb._collection(
            collection="dummy", experiment=experiment, database=db
        )
        db = coll.database
        return cls(db)

    @property
    def schemas(self):
        return dict(XeDoc._XEDOCS)

    @property
    def schema_names(self):
        return list(self.schemas)

    def get_df(self, name):
        schema = self.schemas[name]
        if self.db is None:
            datasource = settings.get_datasource_for(name)
        else:
            datasource = self.db[name]
        return rframe.RemoteFrame(schema, datasource)

    def __getitem__(self, key):
        if isinstance(key, tuple) and key[0] in self.schemas:
            return self.get_df(key[0])[key[1:]]

        if key in self.schemas:
            return self.get_df(key)
        raise KeyError(key)

    def __dir__(self):
        return super().__dir__() + list(self.schemas)

    def __getattr__(self, name):
        if name != "schemas" and name in self.schemas:
            return self.get_df(name)
        return super().__getattribute__(name)

    def sel(self, schema_name, *args, **kwargs):
        return self.get_df(schema_name).sel(*args, **kwargs)

    def set(self, schema_name, *args, **kwargs):
        return self.get_df(schema_name).set(*args, **kwargs)

    def insert(self, schema_name, records):
        return self.get_df(schema_name).insert(records=records)


def run_id_to_time(run_id):
    run_id = int(run_id)
    runsdb = utilix.rundb.xent_collection()
    rundoc = runsdb.find_one({"number": run_id}, {"start": 1})
    if rundoc is None:
        raise ValueError(f"run_id = {run_id} not found")
    time = rundoc["start"]
    return time.replace(tzinfo=pytz.utc)


frames = SchemaFrames()
