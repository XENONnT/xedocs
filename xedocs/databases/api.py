import os
import logging
import xedocs
from rframe import BaseSchema
from pydantic import BaseSettings
from xedocs.database_interface import DatabaseInterface


logger = logging.getLogger(__name__)
XEDOCS_API_ENV = os.getenv(
    "XEDOCS_API_ENV", os.path.join(xedocs.settings.CONFIG_DIR, "api.env")
)


class ApiSettings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_API_"
        env_file = XEDOCS_API_ENV

    PRIORITY: int = -1
    URL_TEMPLATE: str = "{base_url}/{version}/{database}/{name}"
    BASE_URL: str = "https://api.xedocs.yossisprojects.com"
    VERSION: str = "v1"
    AUDIENCE: str = "https://api.cmt.xenonnt.org"
    READONLY: bool = False
    TOKEN: str = None
    USERNAME: str = None
    PASSWORD: str = None

    @property
    def token(self):
        if hasattr(self.TOKEN, "access_token"):
            if self.TOKEN.expired:
                self.TOKEN.refresh()
            return self.TOKEN.access_token
        return self.TOKEN

    def login(self):
        import xeauth

        if self.READONLY:
            scopes = ["read:all"]
        else:
            scopes = ["read:all", "write:all"]

        token = xeauth.login(
            username=self.USERNAME,
            password=self.PASSWORD,
            scopes=scopes,
            audience=self.AUDIENCE,
        )

        self.TOKEN = token

    def api_url_for_schema(self, schema: str, database="development"):

        if hasattr(schema, "_ALIAS"):
            schema = schema._ALIAS

        if isinstance(schema, BaseSchema):
            schema = type(schema)

        if not isinstance(schema, str):
            schema = schema.__name__.lower()

        return self.URL_TEMPLATE.format(
            base_url=self.BASE_URL.strip("/"),
            version=self.VERSION.strip("/"),
            name=schema.strip("/"),
            database=database.strip("/"),
        )


class APIDatabase(DatabaseInterface):
    settings: ApiSettings = ApiSettings()
    database: str
    alias: str

    def __init__(
        self, database: str = None, alias: str = None, settings: ApiSettings = None
    ):
        self.database = database
        if alias is None:
            alias = database
        self.alias = alias
        if settings is not None:
            self.settings = settings

    def datasource_for_schema(self, schema):
        import xedocs

        url = self.settings.api_url_for_schema(schema, database=self.database)

        return xedocs.api.api_client(
            url, token=self.settings.TOKEN, authenticator=self.settings
        )
