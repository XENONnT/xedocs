import os
from pathlib import Path
import appdirs

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

dirs = appdirs.AppDirs('xedocs')


def default_github_username():
    try:
        from git import config
        cfg_path = config.get_config_path('global')
        cfg = config.GitConfigParser(cfg_path)
        return cfg.get('github', 'user')
    except:
        return None

def default_github_token():
    try:
        from git import config
        cfg_path = config.get_config_path('global')
        cfg = config.GitConfigParser(cfg_path)
        return cfg.get('github', 'token')
    except:
        return None

class Settings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_"

    ANALYST_DB: str = "xedocs-dev"
    STRAXEN_DB: str = "xedocs"
    API_URL_FORMAT: str = "{base_url}/{version}/{mode}/{name}"
    API_BASE_URL: str = "https://api.xedocs.yossisprojects.com"
    API_VERSION: str = "v1"
    API_AUDIENCE: str = "https://api.cmt.xenonnt.org"
    API_READONLY: bool = False
    API_TOKEN: str = None
    API_USERNAME: str = None
    API_PASSWORD: str = None
    GITHUB_URL: str = "github://XENONnT:xedocs-data@/data/{category}/{name}.json"
    GITHUB_USERNAME: str = default_github_username()
    GITHUB_TOKEN: str = default_github_token()
    LOCAL_DB_PATH: str = os.path.join(dirs.user_data_dir, "data")

    clock = SimpleClock()

    datasources = {}

    @property
    def token(self):
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

    def api_url_for_schema(self, schema: BaseSchema, base_url=None, version=None, mode='staging'):
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

    def local_path_for_schema(self, schema: BaseSchema):
        return Path(self.LOCAL_DB_PATH) / schema._CATEGORY / f"{schema._ALIAS}.json"

    def github_url_for_schema(self, schema: BaseSchema):
        return self.GITHUB_URL.format(category=schema._CATEGORY, name=schema._ALIAS)

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
        time = doc["start"] + (doc["end"] - doc["start"]) / 2
        return self.clock.normalize_tz(time)

    def run_id_to_interval(self, run_id):
        doc = self.run_doc(run_id)
        start = self.clock.normalize_tz(doc["start"])
        end = self.clock.normalize_tz(doc["end"])
        return start, end

    def extract_time(self, kwargs):
        if "time" in kwargs:
            time = kwargs.pop("time")
        elif "run_id" in kwargs:
            time = self.run_id_to_time(kwargs.pop("run_id"))
        else:
            return None
        time = pd.to_datetime(time)
        time = self.clock.normalize_tz(time)
        return time


settings = Settings()
