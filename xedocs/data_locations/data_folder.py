
import os
import yaml
import fsspec

from pydantic import BaseSettings, validator

from ..utils import Database, LazyFileAccessor


class DataFolder(BaseSettings):
    
    class Config:
        env_prefix = "XEDOCS_DATA_FOLDER_"

    root: str = None
    protocol: str = "file"
    config_path: str = "datasets.yml"

    @validator("root", pre=True)
    def expand_user(cls, value):
        if isinstance(value, str):
            value = os.path.expanduser(value)
        return value

    def storage_kwargs(self, path):
        return {}

    def abs_path(self, path):
        if isinstance(path, list):
            return [self.abs_path(p) for p in path]
        path = os.path.expanduser(path)
        if not os.path.isabs(path) and self.root is not None:
            path = os.path.join(self.root, path)
        return path

    @property
    def datasets_config(self):
        return self.read_config()

    def get_datasets(self):
        import xedocs

        dsets = {}
        for _, cfg in self.datasets_config.items():
            schema = cfg.get('schema', None)
            if schema is None:
                continue
            schema = xedocs.find_schema(schema)
            path = cfg.get('path', None)
            if path is None:
                continue
            path = self.abs_path(path)

            kwargs = self.storage_kwargs(path)
            dsets[schema._ALIAS] = LazyFileAccessor(schema,
                                                    path, 
                                                    **kwargs)
        return Database(dsets)

    def read_config(self):
        path = self.abs_path(self.config_path)
        kwargs = self.storage_kwargs(path)
        
        with fsspec.open(path, **kwargs) as f:
            config = yaml.safe_load(f)
        return config
