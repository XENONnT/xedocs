import os
from pathlib import Path
import appdirs
import logging
import pandas as pd

from rframe import BaseSchema
from rframe.types import TimeInterval

logger = logging.getLogger(__name__)


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

dirs = appdirs.AppDirs("xedocs")

XEDOCS_ENV = os.getenv("XEDOCS_ENV", os.path.join(dirs.user_config_dir, "settings.env"))


class Settings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_"
        env_file = XEDOCS_ENV
        env_file_encoding = "utf-8"

    _DATABASE_INTERFACE_CLASSES = {}
    _RUNDOC_CACHE = {}

    CONFIG_DIR = dirs.user_config_dir
    DATA_DIR = dirs.user_data_dir
    DEFAULT_DATABASE = "straxen_db"
    GITHUB_TOKEN: str = None

    clock = SimpleClock()        

    def run_doc(self, run_id, fields=("start", "end")):
        key = (run_id,) + tuple(fields)
        if key in self._RUNDOC_CACHE:
            return self._RUNDOC_CACHE[key]
        
        if uconfig is None:
            raise KeyError(f"Rundb not configured.")

        rundb = xent_collection()

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


settings = Settings()
