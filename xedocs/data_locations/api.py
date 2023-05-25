import rframe
import requests
from pydantic import BaseSettings
from requests import PreparedRequest
from requests.auth import AuthBase

from ..utils import Database
from .github import GithubCredentials


class ApiAuth(AuthBase):

    def __init__(self, api=None) -> None:
        self.api = api

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        if self.api.token is None:
            self.api.login()
        r.headers["Authorization"] = f"Bearer {self.api.token}"
        return r


class XedocsApi(BaseSettings):
    class Config:
        env_prefix = "xedocs_api_"
    
    base_url: str = "https://api.xedocs.dashboards.xenonnt.org"
    version: str = "v2"
    url_template: str = "{base_url}/{version}/{category}/{name}"
    token: str = None
    
    def fetch_paths(self):
        URL = f"{self.base_url.strip('/')}/{self.version}/.paths"
        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        return dict(response.json())
    
    def login(self):
        cred = GithubCredentials.find()
        self.token = cred.token

    def get_datasets(self):
        from xedocs import find_schema

        dsets = {}
        paths = self.fetch_paths()
        for name, path in paths.items():
            schema = find_schema(name)
            url = f"{self.base_url.strip('/')}{path}"
            datasource = rframe.RestClient(
                        url,
                        auth=ApiAuth(self),
                    )
            dsets[name] = rframe.DataAccessor(schema, datasource)
        return Database(dsets)
