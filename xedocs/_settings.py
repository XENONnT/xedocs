import os
import appdirs
import logging
import pandas as pd
from rframe.types import TimeInterval

from .xenon_config import XenonConfig

logger = logging.getLogger(__name__)

from pydantic import BaseSettings

from .clock import SimpleClock

dirs = appdirs.AppDirs("xedocs")

XEDOCS_ENV = os.getenv("XEDOCS_ENV", os.path.join(dirs.user_config_dir, "settings.env"))


class Settings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_"
        env_file = XEDOCS_ENV
        env_file_encoding = "utf-8"

    _DATABASE_INTERFACE_CLASSES = {}
    _RUNDOC_CACHE = {}
    _MONGO_CLIENTS = {}

    CONFIG_DIR = dirs.user_config_dir
    DATA_DIR = dirs.user_data_dir
    DEFAULT_DATABASE = "straxen_db"
    GITHUB_TOKEN: str = None
    
    xenon_config: XenonConfig = XenonConfig()

    clock = SimpleClock()        

    def run_doc(self, run_id, fields=("start", "end")):
        key = (run_id,) + tuple(fields)
        
        if key in self._RUNDOC_CACHE:
            return self._RUNDOC_CACHE[key]
        
        rundb = self.xent_collection()

        if isinstance(run_id, str):
            run_id = int(run_id)

        query = {"number": run_id}

        doc = rundb.find_one(query, projection={f: 1 for f in fields})
        if not doc:
            raise KeyError(f"Run {run_id} not found.")
        
        self._RUNDOC_CACHE[key] = doc

        return doc

    def run_id_to_time(self, run_id):
        doc = self.run_doc(run_id)
        # use center time of run
        time = doc["start"] + (doc["end"] - doc["start"]) / 2
        return self.clock.normalize_tz(time)

    def run_id_to_interval(self, run_id):
        doc = self.run_doc(run_id)
        start = self.clock.normalize_tz(doc["start"]+pd.Timedelta("1s"))
        end = self.clock.normalize_tz(doc["end"]-pd.Timedelta("1s"))
        
        return TimeInterval(left=start, right=end)

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

    def _mongo_client(self, experiment, url=None, user=None, password=None):
        import pymongo

        if experiment not in ["xe1t", "xent"]:
            raise ValueError(
                f"experiment must be 'xe1t' or 'xent'. You passed f{experiment}"
            )

        if not url:
            url = getattr(self.xenon_config.RunDB, f"{experiment}_url")
        if not user:
            user = getattr(self.xenon_config.RunDB, f"{experiment}_user")
        if not password:
            password = getattr(self.xenon_config.RunDB, f"{experiment}_password")

        # build other client kwargs
        max_pool_size = getattr(self.xenon_config.RunDB, "max_pool_size", 100)

        socket_timeout = getattr(self.xenon_config.RunDB, "socket_timeout", 60000)
        connect_timeout = getattr(self.xenon_config.RunDB, "connect_timeout", 60000)

        uri = f"mongodb://{user}:{password}@{url}"
        if uri not in self._MONGO_CLIENTS:
            self._MONGO_CLIENTS[uri] = pymongo.MongoClient(
                uri,
                readPreference="secondaryPreferred",
                maxPoolSize=max_pool_size,
                socketTimeoutMS=socket_timeout,
                connectTimeoutMS=connect_timeout,
            )
        return self._MONGO_CLIENTS[uri]

    def _mongo_database(self, experiment, database=None, **kwargs):
        if not database:
            database = getattr(self.xenon_config.RunDB, f"{experiment}_database")
        client = self._mongo_client(experiment, **kwargs)
        return client[database]

    def _mongo_collection(self, experiment, collection, **kwargs):
        client = self._mongo_database(experiment, **kwargs)
        return client[collection]

    def xent_collection(self, collection="runs", **kwargs):
        return self._mongo_collection("xent", collection, **kwargs)

    def xe1t_collection(self, collection="runs_new", **kwargs):
        return self._mongo_collection("xe1t", collection, **kwargs)

settings = Settings()
