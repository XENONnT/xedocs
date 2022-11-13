import pandas as pd
from rframe import BaseSchema


def xent_collection(**kwargs):
    pass

try:
    import utilix

    uconfig = utilix.uconfig
    from utilix import xent_collection

except ImportError:
    uconfig = None

from pydantic import BaseSettings

from .clock import SimpleClock

    
class Settings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_"

    STAGING_DB: str = "xedocs"
    PRODUCTION_DB: str = "cmt2"
    API_URL_FORMAT: str = "{base_url}/{version}/{mode}/{name}"
    API_BASE_URL: str = "https://api.xedocs.yossisprojects.com"
    API_VERSION: str = "v1"
    API_AUDIENCE: str = "https://api.cmt.xenonnt.org"
    API_READONLY: bool = False
    API_TOKEN: str = None
    API_USERNAME: str = None
    API_PASSWORD: str = None

    clock = SimpleClock()

    datasources = {}

    @property
    def token(self):
        if self.API_TOKEN is None:
            self.login()

        if hasattr(self.API_TOKEN, "access_token"):
            if self.API_TOKEN.expired:
                self.API_TOKEN.refresh()
            return self.API_TOKEN.access_token
        return self.API_TOKEN

    def login(self):
        import xeauth

        if self.API_READONLY:
            scopes = ["read:all"]
        else:
            scopes = ["read:all", "write:all"]
            
        token = xeauth.login(
            username=self.API_USERNAME,
            password=self.API_PASSWORD,
            scopes=scopes,
            audience=self.API_AUDIENCE,
        )

        self.API_TOKEN = token

    def api_url_for_schema(self, schema, base_url=None, version=None, mode='staging'):
        if base_url is None:
            base_url = self.API_BASE_URL
        
        if version is None:
            version = self.API_VERSION

        if hasattr(schema, "_ALIAS"):
            schema = schema._ALIAS

        return self.API_URL_FORMAT.format(
            base_url=base_url.strip('/'), version=version.strip('/'),
            name=schema.strip('/'), mode=mode.strip('/')
        )

    def run_doc(self, run_id, fields=("start", "end")):
        if uconfig is None:
            raise KeyError(f"Rundb not configured.")

        rundb = xent_collection()

        if isinstance(run_id, str):
            run_id = int(run_id)

        query = {"number": run_id}

        doc = rundb.find_one(query, projection={f: 1 for f in fields})
        if not doc:
            raise KeyError(f"Run {run_id} not found.")

        return doc

    def run_id_to_time(self, run_id):
        doc = self.run_doc(run_id)
        # use center time of run
        return doc["start"] + (doc["end"] - doc["start"]) / 2

    def run_id_to_interval(self, run_id):
        doc = self.run_doc(run_id)
        return doc["start"], doc["end"]

    def extract_time(self, kwargs):
        if "time" in kwargs:
            time = kwargs.pop("time")
        elif "run_id" in kwargs:
            time = self.run_id_to_time(kwargs.pop("run_id"))
        else:
            return None
        return pd.to_datetime(time)


settings = Settings()
