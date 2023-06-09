
import os
from typing import List, Union
import fsspec
from pydantic import BaseSettings, root_validator
import yaml
from plum import dispatch
from ..dispatchers import read_files
from ..utils import Database, LazyDataAccessor
from ..json_records import JsonLoader



class FileLoader:
    def __init__(self, paths: Union[str, List[str]], **kwargs) -> None:
        if not isinstance(paths, (list, str)):
            raise ValueError(f"Invalid path: {paths}")
        if isinstance(paths, str):
            paths = [paths]
        self.paths = paths
        self.kwargs = kwargs
    
    def load(self) -> List[dict]:
        docs = []
        for path in self.paths:
            docs.extend(read_files(path, **self.kwargs))
        return docs

    def __call__(self) -> List[dict]:
        return self.load()


class DataFolder(BaseSettings):
    
    __loader_class__ = FileLoader

    class Config:
        env_prefix = "XEDOCS_DATA_FOLDER_"
    
    root: str = None
    config_path: str = "datasets.yml"


    def storage_kwargs(self, path):
        return {}

    def abs_path(self, path):
        if isinstance(path, list):
            return [self.abs_path(p) for p in path]
        if not os.path.isabs(path):
            path = os.path.join(self.root, path)
        return path
    
    @property
    def datasets_config(self):
        return self.read_config()

    def get_datasets(self):
        import xedocs

        dsets = {}

        for _, cfg in self.datasets_config.items():
            schema = xedocs.find_schema(cfg['schema'])
            path = self.abs_path(cfg['path'])
            kwargs = self.storage_kwargs(path)
            datasource = self.__loader_class__(path, **kwargs)
            dsets[schema._ALIAS] = LazyDataAccessor(schema, datasource=datasource)
        return Database(dsets)
    
    def read_config(self):
        path = self.abs_path(self.config_path)
        kwargs = self.storage_kwargs(path)
        with fsspec.open(path, **kwargs) as f:
            config = yaml.safe_load(f)
        return config
