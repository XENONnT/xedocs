from pydantic import BaseSettings
from rframe import DataAccessor


class MongoDB(BaseSettings):
    CLIENT_CACHE = {}

    class Config:
        env_prefix = "xedocs_mongo_"

    username: str = None
    password: str = None
    db_name: str = "xedocs"
    auth_db: str = "admin"
    host: str = None
    connection_uri: str = None

    @property
    def client(self):
        if self.connection_uri is None:
            self.connection_uri = f"mongodb://{self.username}:{self.password}@{self.host}?authSource={self.auth_db}&readPreference=secondary"
        if self.connection_uri not in self.CLIENT_CACHE:
            self.CLIENT_CACHE[self.connection_uri] = self.make_client(self.connection_uri)
        return self.CLIENT_CACHE[self.connection_uri]

    def make_client(self, connection_uri):
        import pymongo
        return pymongo.MongoClient(connection_uri)

    @classmethod
    def from_utilix(cls):
        from utilix import uconfig
        host = uconfig.get('RunDB', 'xent_url')
        username = uconfig.get('RunDB', 'xent_user')
        password = uconfig.get('RunDB', 'xent_password')
        auth_db = uconfig.get('RunDB', 'xent_database')
        return cls(host=host, username=username, 
                   password=password, auth_db=auth_db)

    def data_accessor(self, schema):
        datasource = self.client[self.db_name][schema._ALIAS]
        return DataAccessor(schema, datasource)

