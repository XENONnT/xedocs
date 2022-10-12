
from collections import defaultdict
import requests


from rframe import DataAccessor, RestClient
from xedocs import settings, all_schemas
from xedocs.xedocs import find_schema

from .api import ApiAuth
from .utils import DatasetCollection
from .schemas import XeDoc


class XedocsContext:
    _datasets: dict = None

    @property
    def datasets(self):
        return dict(self._datasets)

    def __init__(self, schemas=None):

        if not schemas:
            schemas = all_schemas()

        if isinstance(schemas, dict):
            schemas = list(schemas.values())

        self._datasets = self.make_datasets(*schemas)

    def make_datasets(self, *schemas):
        dsets = defaultdict(DatasetCollection)

        for schema in schemas:
            if isinstance(schema, str):
                schema = find_schema(schema)

            if not issubclass(schema, XeDoc):
                raise TypeError('Wrong type for schema spec, '
                                f'expected a XeDoc or string got {type(schema)}')
            dsource = self.make_datasource(schema)
            dsets[schema._CATEGORY][schema._ALIAS] = DataAccessor(schema, dsource)
        return dsets

    def make_datasource(self, schema):
        raise NotImplementedError

    def __getitem__(self, key):
        return self._datasets.get(key)

    def __getattr__(self, attr):
        if attr in self._datasets.keys():
            return self[attr]
        raise AttributeError(attr)
    
    def __dir__(self):
        return super().__dir__() + list(self._datasets.keys())


class ApiContext(XedocsContext):
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

    def __init__(self, *schemas,
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
        
        super().__init__(*schemas)

    def url_for(self, schema):
        return "/".join([self.URL.rstrip("/"), self.VERSION, schema._ALIAS])

    def make_datasource(self, schema):
        url = self.url_for(schema)
        return RestClient(url, auth=ApiAuth(context=self))

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

class UtilixContext(XedocsContext):
    DB_NAME = settings.DEFAULT_DATABASE

    def __init__(self, *schemas, database=None):
        self.DB_NAME = database
        super().__init__(*schemas)

    def make_datasource(self, schema):
        import utilix
        database = self.DATABASE
        collection = schema.default_collection_name()
        return utilix.xent_collection(collection=collection, 
                                    database=database)

class MongoContext(XedocsContext):

    def __init__(self, *schemas, database=None):
        import pymongo
        self.db = pymongo.MongoClient()[database]
        super().__init__(*schemas)

    def make_datasource(self, schema):
        collection = schema.default_collection_name()
        return self.db[collection]


staging_api = ApiContext()
production_api = ApiContext()

try:
    staging = UtilixContext()
    production = UtilixContext(database='cmt2')
except ImportError:
    pass

production_local = MongoContext(database='cmt2')
staging_local = MongoContext(database='xedocs')
