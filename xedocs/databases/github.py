import os
import xedocs
import tinydb
import logging

from pydantic import BaseSettings
from xedocs.schemas import XeDoc
from xedocs.database_interface import DatabaseInterface

from .local import FsspecStorage

XEDOCS_GITHUB_ENV = os.getenv(
    "XEDOCS_GITHUB_ENV", os.path.join(xedocs.settings.CONFIG_DIR, "github.env")
)
logger = logging.getLogger(__name__)


def default_github_username():
    try:
        from git import config

        cfg_path = config.get_config_path("global")
        cfg = config.GitConfigParser(cfg_path)
        return cfg.get("github", "user")
    except:
        return None


def default_github_token():
    try:
        from git import config

        cfg_path = config.get_config_path("global")
        cfg = config.GitConfigParser(cfg_path)
        return cfg.get("github", "token")
    except:
        return None


class GithubSettings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_GITHUB_"
        env_file = XEDOCS_GITHUB_ENV

    PRIORITY: int = -1
    ORG: str = "XENONnT"
    REPO: str = "xedocs-data"
    URL_TEMPLATE: str = "github://{org}:{repo}@/{database}/{category}/{name}/*.json"
    USERNAME: str = default_github_username()
    TOKEN: str = default_github_token()


class GithubDatabase(DatabaseInterface):
    settings: GithubSettings = GithubSettings()

    def __init__(
        self, database: str = None, alias: str = None, settings: GithubSettings = None
    ):
        self.database = database
        if alias is None:
            alias = database
        self.alias = alias
        if settings is not None:
            self.settings = settings

    def github_url_for_schema(self, schema: XeDoc):
        return self.settings.URL_TEMPLATE.format(
            org=self.settings.ORG,
            repo=self.settings.REPO,
            category=schema._CATEGORY,
            name=schema._ALIAS,
            database=self.database,
        )

    def datasource_for_schema(self, schema):
        url = self.github_url_for_schema(schema)
        db = tinydb.TinyDB(
            url,
            storage=FsspecStorage,
            username=self.settings.USERNAME,
            token=self.settings.TOKEN,
        )
        return db.table(schema._ALIAS)
