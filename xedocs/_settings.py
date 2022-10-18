import pandas as pd


try:
    import utilix

    uconfig = utilix.uconfig
    from utilix import xent_collection

except ImportError:
    uconfig = None

    def xent_collection(**kwargs):
        raise RuntimeError("utilix not configured")


from pydantic import BaseSettings

from .clock import SimpleClock


class Settings(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_"

    DEFAULT_DATABASE: str = "xedocs"

    API_URL_FORMAT: str = "{base_url}/{version}/{path}/{name}"
    API_BASE_URL: str = "https://api.xedocs.yossisprojects.com"
    API_PATH: str = "/xedocs"
    API_VERSION: str = "v1"
    API_AUDIENCE: str = "https://api.cmt.xenonnt.org"
    API_WRITE: bool = False
    API_TOKEN: str = None
    API_USERNAME: str = None
    API_PASSWORD: str = None

    clock = SimpleClock()

    datasources = {}

    def api_url_for_schema(self, schema, base_url=None, version=None, path=None):
        from xedocs.schemas import XeDoc

        if base_url is None:
            base_url = self.API_BASE_URL
        if version is None:
            version = self.API_VERSION
        if path is None:
            path = self.API_PATH
        if isinstance(schema, XeDoc):
            schema = schema._ALIAS
        return self.API_URL_FORMAT.format(
            base_url=base_url, version=version, name=schema, path=path
        ).replace("//", "/")

    def get_api_token(self):
        import xedocs

        if self.API_TOKEN is None:
            readonly = not self.API_WRITE
            token = api_login(self.API_USERNAME, self.API_PASSWORD, readonly)
            self.API_TOKEN = token

        return self.API_TOKEN

    def api_client(self, schema):
        import xedocs

        url = "/".join([self.API_BASE_URL.rstrip("/"), self.API_VERSION, schema._ALIAS])

        return xedocs.api.api_client(url, self.get_api_token())

    def default_datasource(self, schema):

        if uconfig is not None:
            database = schema.default_database_name()
            if database is None:
                database = self.DEFAULT_DATABASE
            collection = schema.default_collection_name()

            return xent_collection(collection=collection, database=database)
        return self.api_client(schema)

    def get_datasource_for(self, schema):
        if schema._ALIAS in self.datasources:
            return self.datasources[schema._ALIAS]

        return self.default_datasource(schema)

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


def api_login(
    username=None, password=None, readonly=True, audience="https://api.cmt.xenonnt.org"
):
    import xeauth

    if readonly:
        scopes = ["read:all", "write:all"]
    else:
        scopes = ["read:all"]

    xetoken = xeauth.login(
        username=username, password=password, scopes=scopes, audience=audience
    )

    return xetoken.access_token


settings = Settings()
