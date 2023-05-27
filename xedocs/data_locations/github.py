
import os
import fsspec
from pydantic import BaseSettings, root_validator
import yaml

from ..utils import Database, LazyDataAccessor
from ..json_records import JsonLoader


def git_config_source(cls, **kwargs):
    """
    Get github credentials from git config
    """
    try:
        from git import config

        cfg_path = config.get_config_path("global")
        cfg = config.GitConfigParser(cfg_path)
        return dict(username=cfg.get("github", "user"),
                    token=cfg.get("github", "token"))
    except:
        return {}


class GithubCredentials(BaseSettings):
    class Config:
        env_prefix = "github_"
        secrets_dir = '/run/secrets'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):

            sources = (
                init_settings,
                env_settings,
                git_config_source,
            )
            if os.path.isdir("/run/secrets"):
                sources = sources + (file_secret_settings,)
            return sources


    username: str = "__token__"
    token: str = None

    @classmethod
    def find(cls, **kwargs):
        inst = cls(**kwargs)
        if inst.token is None:
            inst = cls.from_login()
        if inst.token is None:
            raise RuntimeError("Could not find github credentials.")
        return inst

    @classmethod
    def from_login(cls):
        from xeauth.github import GitHubAuth
        auth = GitHubAuth.device_login(scopes=["read:org", "read:user", "repo"])
        return cls(username=auth.api.username, token=auth.oauth_token)


class GithubRepo(BaseSettings):
    class Config:
        env_prefix = "XEDOCS_GITHUB_REPO_"
    
    org: str = "XENONnT"
    repo: str = "xedocs-data"
    config_path: str = "datasets.yml"
    username: str = "__token__"
    token: str = None
    branch: str = None

    @root_validator
    def get_token(cls, values):
        token = values.get('token', None)
        if token is None:
            cred = GithubCredentials.find()
            values['username'] = cred.username
            values['token'] = cred.token
        return values
    
    @property
    def datasets_config(self):
        return self.read_config()

    def get_datasets(self):
        import xedocs

        dsets = {}

        for name, cfg in self.datasets_config.items():
            schema = xedocs.find_schema(cfg['schema'])
            url = f"github://{self.org}:{self.repo}@/{cfg['path']}"
            datasource = JsonLoader(url, sha=self.branch,
                                     username=self.username, token=self.token)
            dsets[schema._ALIAS] = LazyDataAccessor(schema, datasource=datasource)
        return Database(dsets)
    
    def read_config(self):
        URL = f"github://{self.org}:{self.repo}@/{self.config_path}"
        with fsspec.open(URL, sha=self.branch,
                          username=self.username, token=self.token) as f:
            config = yaml.safe_load(f)
        return config
