from typing import Any
import pandas as pd

from collections import UserDict
from pydantic import ValidationError
from rframe.data_accessor import DataAccessor


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
        return df

    @storage.setter
    def storage(self, value):
        if not callable(value):
            raise ValueError('storage must be callable')
        self.get_storage = value


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
