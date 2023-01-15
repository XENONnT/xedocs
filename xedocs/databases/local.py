import os
import json
import xedocs
import appdirs
import logging
import fsspec

from pathlib import Path
from tinydb import TinyDB
from pydantic import BaseSettings
from tinydb.storages import Storage
from typing import Any, Dict, Optional
from xedocs.database_interface import DatabaseInterface


XEDOCS_LOCAL_REPO_ENV = os.getenv(
    "XEDOCS_LOCAL_REPO_ENV", os.path.join(xedocs.settings.CONFIG_DIR, "local_repo.env")
)
logger = logging.getLogger(__name__)
dirs = appdirs.AppDirs("xedocs")


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


class LocalRepoSettings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_LOCAL_REPO_"
        env_file = XEDOCS_LOCAL_REPO_ENV

    PRIORITY: int = 3
    PATH: str = dirs.user_data_dir


class LocalRepoDatabase(DatabaseInterface):
    settings: LocalRepoSettings = LocalRepoSettings()
    database: str
    alias: str

    def __init__(
        self,
        database: str = None,
        alias: str = None,
        settings: LocalRepoSettings = None,
    ):
        self.database = database
        if alias is None:
            alias = database
        self.alias = alias
        if settings is None:
            settings = LocalRepoSettings()
        self.settings = settings

    def base_path_for_schema(self, schema):
        return (
            Path(self.settings.PATH) / self.database / schema._CATEGORY / schema._ALIAS
        )

    def datasource_for_schema(self, schema):
        path = self.base_path_for_schema(schema) / "*.json"

        if path.exists():
            db = TinyDB(path.absolute())
            return db.table(schema._ALIAS)
