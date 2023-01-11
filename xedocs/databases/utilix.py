from utilix import xent_collection, uconfig

from xedocs.database_interface import DatabaseInterface
from pydantic import BaseSettings


class UtilixSettings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_UTILIX_"

    PRIORITY: int = 1
    DATABASE_NAMES = {"straxen_db": "xedocs", "development_db": "xedocs-dev"}


class UtilixDatabase(DatabaseInterface):
    settings: UtilixSettings = UtilixSettings()
    database: str
    alias: str

    def __init__(
        self, database: str = None, alias: str = None, settings: UtilixSettings = None
    ):
        if alias is None:
            alias = database
        self.alias = alias
        if settings is not None:
            self.settings = settings
        database = self.settings.DATABASE_NAMES.get(database, database)
        self.database = database

    def datasource_for_schema(self, schema):
        if uconfig is None:
            return None
        collection_name = schema._ALIAS
        return xent_collection(collection=collection_name, database=self.database)
