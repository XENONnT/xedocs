import os
from typing import Any, Dict
from pydantic import BaseSettings
from rframe import DataAccessor


def xenon_config_source(settings: BaseSettings) -> Dict[str, Any]:
    from xedocs import settings

    cfg = settings.xenon_config.RunDB
    data = {}
    if cfg.xent_url:
        data['host'] = cfg.xent_url
    if cfg.xent_user:
        data['username'] = cfg.xent_user
    if cfg.xent_password:
        data['password'] = cfg.xent_password
    if cfg.xent_database:
        data['auth_db'] = cfg.xent_database
    return data


class MongoDB(BaseSettings):
    CLIENT_CACHE = {}

    class Config:
        env_prefix = "xedocs_mongo_"
        secrets_dir = '/run/secrets'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            sources = (
                init_settings,
                env_settings,
                xenon_config_source,
            )
            if os.path.isdir("/run/secrets"):
                sources = sources + (file_secret_settings,)
            return sources
        
    username: str = None
    password: str = None
    db_name: str = "xedocs"
    auth_db: str = "admin"
    host: str = "localhost"
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
    def from_utilix(cls, **kwargs):
        from utilix import uconfig
        host = uconfig.get('RunDB', 'xent_url')
        username = uconfig.get('RunDB', 'xent_user')
        password = uconfig.get('RunDB', 'xent_password')
        auth_db = uconfig.get('RunDB', 'xent_database')
        config = dict(host=host, username=username,
                           password=password, auth_db=auth_db)
        config.update(kwargs)
        return cls(**config)

    def data_accessor(self, schema):
        datasource = self.client[self.db_name][schema._ALIAS]
        return DataAccessor(schema, datasource)
