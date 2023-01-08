
import tinydb
import fsspec
import json

from typing import Any, Dict, Optional

from xedocs import settings
from xedocs.schemas import XeDoc

from tinydb.storages import Storage


class FsspecStorage(Storage):
    def __init__(self, path, **storage_kwargs):
        self.path = path
        self.storage_kwargs = storage_kwargs

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        datasets = {}
        with fsspec.open_files(self.path, **self.storage_kwargs) as fs:
            for f in fs:
                if not f.size:
                    continue
                if not f.readable():
                    continue
                filedata = json.load(f)
                for table, data in filedata.items():
                    if table in datasets:
                        datasets[table].update(data)
                    else:
                        datasets[table] = data
                        
        if not datasets:
            return None
        return datasets

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        with fsspec.open(self.path, "rb", **self.storage_kwargs) as f:
            if not f.writable():
                raise IOError(
                    f'Cannot write to the database. Access mode is "{f.mode}"'
                )
            json.dump(data, f)


def github_source_for(schema: XeDoc, db='analyst_db'):
    url = settings.github_url_for_schema(schema, db=db)
    db = tinydb.TinyDB(url, 
        storage=FsspecStorage,
        username=settings.GITHUB_USERNAME, 
        token=settings.GITHUB_TOKEN)
    return db.table(schema._ALIAS)


def analyst_db_api_source(schema: XeDoc):
    return github_source_for(schema, db='analyst_db')


def straxen_db_api_source(schema: XeDoc):
    return github_source_for(schema, db='straxen_db')
