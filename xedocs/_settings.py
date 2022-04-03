import pandas as pd
import utilix

from pydantic import BaseSettings

from .clock import SimpleClock

class Settings(BaseSettings):
    class Config:
        env_prefix = 'XEDOCS_'

    DEFAULT_DATABASE: str = "cmt2"

    API_URL: str = 'https://api.xedocs.yossisprojects.com'
    API_AUDIENCE: str = 'https://api.cmt.xenonnt.org'
    API_WRITE: bool = False
    API_TOKEN: str = None
    API_USERNAME: str = None
    API_PASSWORD: str = None

    clock = SimpleClock()

    datasources = {}

    def default_datasource(self, name):
        if utilix.uconfig is not None:
            return utilix.xent_collection(collection=name,
                                          database=self.DEFAULT_DATABASE)

        import xedocs
        token = self.API_TOKEN

        if token is None:
            readonly = not self.API_WRITE
            token = xedocs.api_token(self.API_USERNAME,
                                     self.API_PASSWORD,
                                     readonly)
            self.API_TOKEN = token

        url = self.API_URL.rstrip('/') + '/' + name
        return xedocs.api_client(url, token)


    def get_datasource_for(self, name):
        if name in self.datasources:
            return self.datasources[name]
        return self.default_datasource(name)

    def run_id_to_time(self, run_id):
        rundb = utilix.xent_collection()

        if isinstance(run_id, str):
            run_id = int(run_id)

        query = {"number": run_id}

        doc = rundb.find_one(query, projection={"start": 1, "end": 1})
        if not doc:
            raise KeyError(f"Run {run_id} not found.")

        # use center time of run
        return doc["start"] + (doc["end"] - doc["start"]) / 2

    def extract_time(self, kwargs):
        if "time" in kwargs:
            time = kwargs.pop("time")
        if "run_id" in kwargs:
            time = self.run_id_to_time(kwargs.pop("run_id"))
        else:
            return None
        return pd.to_datetime(time)


settings = Settings()
