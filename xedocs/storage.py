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

    def __init__(self, database=settings.DEFAULT_DATABASE):
        self.DB_NAME = database

    def get_datasource(self, name):
        try:
            import utilix
        except ImportError:
            return None
        return utilix.xent_collection(collection=name, database=self.DB_NAME)


class ApiStorage(BaseStorage):
    BASE_URL: str
    PATH: str
    VERSION: str
    AUDIENCE: str
    READONLY: bool
    TOKEN: str
    USERNAME: str
    PASSWORD: str

    @property
    def token(self):
        if self.TOKEN is None:
            self.login()

        if hasattr(self.TOKEN, "access_token"):
            if self.TOKEN.expired:
                self.TOKEN.refresh()
            return self.TOKEN.access_token

        return self.TOKEN

    def __init__(
        self,
        url=settings.API_BASE_URL,
        path=settings.API_PATH,
        version=settings.API_VERSION,
        audience=settings.API_AUDIENCE,
        token=settings.API_TOKEN,
        username=settings.API_USERNAME,
        password=settings.API_PASSWORD,
        readonly=settings.API_TOKEN,
    ):
        self.BASE_URL = url
        self.PATH = path
        self.VERSION = version
        self.READONLY = readonly
        self.AUDIENCE = audience
        self.TOKEN = token
        self.USERNAME = username
        self.PASSWORD = password

    def get_datasource(self, name: str):
        url = settings.api_url_for_schema(name, base_url=self.BASE_URL, version=self.VERSION)
        return RestClient(url, auth=ApiAuth(authenticator=self))

    def login(self):
        import xeauth

        if self.READONLY:
            scopes = ["read:all", "write:all"]
        else:
            scopes = ["read:all"]

        token = xeauth.login(
            username=self.USERNAME,
            password=self.PASSWORD,
            scopes=scopes,
            audience=self.AUDIENCE,
        )

        self.TOKEN = token
