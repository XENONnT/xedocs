import parse
import fsspec

import pandas as pd

from typing import Any, Union
from collections import UserDict
from pydantic import ValidationError
from rframe.data_accessor import DataAccessor
from typing import List
from plum import dispatch

from .dispatchers import read_files


def docs_to_wiki(schema, docs, title=None, columns=None):
    """Convert a list of documents to a dokuwiki table

    :param title: title of the table.
    """
    if title is None:
        title = schema._ALIAS.replace("_", " ").capitalize() + " Table"

    if columns is None:
        columns = list(schema.get_index_fields()) + list(schema.get_column_fields())

    table = "^ %s " % title + "^" * (len(columns) - 1) + "^\n"
    table += "^ " + " ^ ".join(columns) + " ^\n"

    for doc in docs:
        table += "| " + " | ".join([str(getattr(doc, col)) for col in columns]) + " |\n"
    return table


def docs_to_dataframe(schema, docs, columns=None):
    if columns is None:
        columns = list(schema.__fields__)
    else:
        columns = list(columns)

    docs = [doc.pandas_dict() for doc in docs]
    df = pd.json_normalize(docs)

    if len(df):
        df = df[columns]
    else:
        df = df.reindex(columns=list(columns))

    index_fields = [name for name in schema.get_index_fields() if name in columns]

    if len(index_fields) == 1:
        index_fields = index_fields[0]

    return df.set_index(index_fields)


class LazyDataAccessor(DataAccessor):
    __storage__ = None

    @property
    def storage(self):
        if self.__storage__ is None:
            self.__storage__ = self.get_storage()
        if not isinstance(self.__storage__, list):
            return self.__storage__
        docs = []
        for doc in self.__storage__:
            if not isinstance(doc, dict):
                continue
            try:
                doc = self.schema(**doc).pandas_dict()
                docs.append(doc)
            except ValidationError:
                continue

        df = pd.DataFrame(docs, columns=list(self.schema.__fields__))
        idx_names = list(self.schema.get_index_fields())
        if not all([n in df.columns for n in idx_names]):
            return df
        if len(idx_names) == 1:
            idx_names = idx_names[0]
        df = df.set_index(idx_names)
        self.__storage__ = df
        return df

    @storage.setter
    def storage(self, value):
        if not callable(value):
            raise ValueError('storage must be callable')
        self.get_storage = value


def remove_prefix(text, prefix, sep="/"):
    if text.startswith(prefix):
        text = text[len(prefix):]
    if sep is not None and text.startswith(sep):
        text = text[len(sep):]
    return text


class LazyFileAccessor(DataAccessor):
    loaded: set
    pattern: str
    root: str
    urlpaths: List[str]
    storage_options: dict
    
    def __init__(self, schema, urlpaths, root=None, pattern=None, **kwargs):
        if isinstance(urlpaths, str):
            urlpaths = [urlpaths]
        self.urlpaths = urlpaths
        self.root = root
        self.pattern = pattern
        self.loaded = set()
        self.storage_options = kwargs
        storage = schema.empty_dframe()
        super().__init__(schema, storage, False)

    def load_files(self, **labels):
        dfs = []
        index_fields = list(self.schema.get_index_fields())
        if len(index_fields) == 1:
            index_fields = index_fields[0]
        for urlpath in self.urlpaths:
            fs, _, paths = fsspec.get_fs_token_paths(urlpath, storage_options=self.storage_options)
            for path in self.filter_paths(paths, **labels):
                if path in self.loaded:
                    continue
                records = read_files(path, **self.storage_options)
                df = pd.json_normalize(records).set_index(index_fields)
                dfs.append(df)
                self.loaded.add(path)
        self.storage = pd.concat([self.storage] + dfs).sort_values(index_fields)

    def _find(self, skip=None, limit=None, sort=None, **labels):
        self.load_files(**labels)
        return super()._find(skip=skip, limit=limit, sort=sort, **labels)

    def filter_paths(self, paths, **kwargs):
        if self.pattern is None:
            return paths
        if self.root is not None and self.pattern.startswith(self.root):
            self.pattern = remove_prefix(self.pattern, self.root)
        pattern = parse.compile(self.pattern)
        result = []
        for path in paths:
            if self.root is not None and path.startswith(self.root):
                p = remove_prefix(path, self.root)
            else:
                p = path
            r = pattern.parse(p)
            if r is None:
                continue
            for k,v in kwargs.items():
                if not isinstance(v, list):
                    v = [v]
                label = r.named.get(k, None)
                if label is None:
                    continue
                if k in self.schema.__fields__:
                    index = self.schema.index_for(k)
                    label = index.validate_label(label)
                    v = index.validate_label(v)
                if label not in v:
                    break
            else:
                result.append(path)
        return result

    def _min(self, **kwargs):
        self.load_files()
        return super()._min()

    def _max(self, **kwargs):
        self.load_files()
        return super()._max(**kwargs)

    def _count(self, **kwargs):
        self.load_files()
        return super()._count(**kwargs)

    def _unique(self, **kwargs):
        self.load_files()
        return super()._unique(**kwargs)

    def insert(self, docs, raise_on_error=True, dry=False):
        raise NotImplementedError

    def delete(self, docs, raise_on_error=True):
        raise NotImplementedError


class Database(UserDict):
    def __getattr__(self, attr):
        if attr in self.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return list(self.keys())

    def __getitem__(self, key: Any) -> Any:
        if hasattr(key, "_ALIAS"):
            key = key._ALIAS
        return super().__getitem__(key)
