
import os
import fsspec
from pydantic import BaseSettings, root_validator
import yaml

from ..utils import Database, LazyDataAccessor
from .data_folder import DataFolder



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


class GithubRepo(DataFolder):
    class Config:
        env_prefix = "XEDOCS_GITHUB_REPO_"

    protocol: str = "github"
    org: str = "XENONnT"
    repo: str = "xedocs-data"
    username: str = "__token__"
    token: str = None
    branch: str = None
    
    def abs_path(self, path):
        if isinstance(path, list):
            return [self.abs_path(p) for p in path]
        return f"github://{path.lstrip('/')}"

    def storage_kwargs(self, path):
        return {
            "org": self.org,
            "repo": self.repo,
            "username": self.username,
            "token": self.token,
            "sha": self.branch,
        }

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
