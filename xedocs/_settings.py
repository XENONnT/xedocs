import os
from pathlib import Path
import appdirs
import logging
import pandas as pd

from rframe import BaseSchema


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

    DATABASES = ["development_db", "straxen_db"]
    DEFAULT_DATABASE = "straxen_db"
    CONFIG_DIR = dirs.user_config_dir
    DATA_DIR = dirs.user_data_dir

    clock = SimpleClock()

    _database_interfaces = {}

    def database_interfaces(self, database: str):
        interfaces = self._database_interfaces.get(database, {})
        interfaces = dict(
            sorted(interfaces.items(), key=lambda x: x[1].settings.PRIORITY)
        )

        return interfaces

    def iter_sources_for_schema(
        self, schema: BaseSchema, interfaces=None, databases=None
    ):
        if databases is None:
            databases = self.DATABASES
        for dbname in databases:
            interfaces = self.database_interfaces(dbname)
            for iname, interface in interfaces.items():
                if interfaces is not None and iname not in interfaces:
                    continue
                source = interface.datasource_for_schema(schema)
                if source is None:
                    continue
                yield (dbname, iname, source)

    def register_databases(self, schema: BaseSchema, databases=None, interfaces=None):
        for dbname, iname, source in self.iter_sources_for_schema(
            schema, interfaces=interfaces, databases=databases
        ):
            for name in (dbname, f"{dbname}_{iname}"):
                if hasattr(schema, name):
                    continue
                schema.register_datasource(source, name=name)

    def default_datasource_for_schema(self, schema, databases=None, interfaces=None):
        if databases is None:
            databases = [self.DEFAULT_DATABASE]
        for _, _, source in self.iter_sources_for_schema(
            schema, databases=databases, interfaces=interfaces
        ):
            return source

    def register_database_interface_class(self, name: str, interface_class):
        self._DATABASE_INTERFACE_CLASSES[name] = interface_class

        if not hasattr(interface_class, "settings"):
            return

        if interface_class.settings.PRIORITY == -1:
            return

        for database in self.DATABASES:
            if database not in self._database_interfaces:
                self._database_interfaces[database] = {}
            try:
                interface = interface_class(database=database)
                self._database_interfaces[database][name] = interface
            except Exception as e:
                logger.debug(
                    f"Could not register {database} interface for {name}. \n Error: {e}"
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
