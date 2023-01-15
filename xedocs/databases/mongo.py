import pymongo
import logging
from xedocs.schemas import XeDoc
from xedocs.database_interface import DatabaseInterface

from pydantic import BaseSettings


logger = logging.getLogger(__name__)


class MongoSettings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_MONGO_"

    PRIORITY: int = -1
    URL: str = "mongodb://localhost:27017"

    def client(self):
        return pymongo.MongoClient(self.URL)


class MongoDatabase(DatabaseInterface):
    settings: MongoSettings = MongoSettings()
    database: str
    alias: str
    _client: pymongo.MongoClient = None

    def __init__(
        self,
        database: str = None,
        alias: str = None,
        settings: MongoSettings = None,
        client: pymongo.MongoClient = None,
    ):
        self.database = database
        if alias is None:
            alias = database
        self.alias = alias
        if settings is not None:
            self.settings = settings
        if client is not None:
            self._client = client

    @property
    def client(self):
        if self._client is None:
            self._client = self.settings.client()
        return self._client

    def datasource_for_schema(self, schema: XeDoc):
        return self.client[self.database][schema._ALIAS]
