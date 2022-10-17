
from typing import Union
from abc import ABC, abstractmethod
from rframe import RestClient

from .api import ApiAuth
from .schemas import XeDoc
from xedocs import settings


class BaseStorage(ABC):
    @abstractmethod
    def get_datasource(self, name: Union[str,XeDoc]):
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
    DB_NAME: str = 'xedocs'

    def __init__(self, database=settings.DEFAULT_DATABASE):
        self.DB_NAME = database

    def get_datasource(self, name):
        try:
            import utilix
        except ImportError:
            return None
        return utilix.xent_collection(collection=name, 
                                      database=self.DB_NAME)

class ApiStorage(BaseStorage):
    URL: str
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
        
        if hasattr(self.TOKEN, 'access_token'):
            if self.TOKEN.expired:
                self.TOKEN.refresh()
            return self.TOKEN.access_token

        return self.TOKEN

    def __init__(self,
                    url=settings.API_URL, 
                    version=settings.API_VERSION, 
                    audience=settings.API_AUDIENCE, 
                    token=settings.API_TOKEN, 
                    username=settings.API_USERNAME, 
                    password=settings.API_PASSWORD, 
                    readonly=settings.API_TOKEN):
        self.URL = url
        self.VERSION = version
        self.READONLY = readonly
        self.AUDIENCE = audience
        self.TOKEN = token
        self.USERNAME = username
        self.PASSWORD = password
        
    def url_for(self, name: str):
        return "/".join([self.URL.rstrip("/"), self.VERSION, name])

    def get_datasource(self, name: str):
        url = self.url_for(name)
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
            audience=self.AUDIENCE
            )

        self.TOKEN = token

