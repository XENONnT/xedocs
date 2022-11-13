from typing import Union
from abc import ABC, abstractmethod
from rframe import RestClient

from .api import ApiAuth
from .schemas import XeDoc
from xedocs import settings


class BaseStorage(ABC):
    @abstractmethod
    def get_datasource(self, name: Union[str, XeDoc]):
        pass


class DictStorage(BaseStorage):
    def __init__(self, datasources=None):
        if datasources is None:
            datasources = {}
        self.datasources = datasources

    def get_datasource(self, name: str):
        return self.datasources.get(name, None)


class MongoDBStorage(BaseStorage):
    def __init__(self, db):
        self.db = db

    def get_datasource(self, name: str):
        return self.db[name]


class UtilixStorage(BaseStorage):
    DB_NAME: str = "xedocs"

    def __init__(self, database=settings.STAGING_DB):
        self.DB_NAME = database

    def get_datasource(self, name):
        try:
            import utilix
        except ImportError:
            return None
        return utilix.xent_collection(collection=name, database=self.DB_NAME)


class ApiStorage(BaseStorage):
    MODE: str = "staging"

    def __init__(self, mode="staging"):
        self.MODE = mode

    def get_datasource(self, name: str):
        import xedocs
        return xedocs.api_client(name, mode=self.MODE)
