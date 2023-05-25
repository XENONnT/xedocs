import json
import logging
import fsspec

from pathlib import Path
from typing import Dict, List

from io import IOBase
import pandas as pd
from plum import dispatch


logger = logging.getLogger(__name__)


@dispatch
def read_records(obj: IOBase):
    """Reads a json file from an IOBase object"""
    if not obj.size:
        return []
    if not obj.readable():
        return []
    data = json.loads(obj.read())
    return data


@dispatch
def read_records(obj: List[IOBase]):
    """Reads a json file from a ist of IOBase objects"""
    docs = []
    for f in obj:
        docs.extend(read_records(f))
    return docs


@dispatch
def read_records(obj: Path):
    """Reads a json file"""
    data = json.loads(obj.read_text())
    return data


@dispatch
def read_records(obj: List[Dict]):
    """This is the expected format for a list of documents"""
    return obj


@dispatch
def read_records(obj: Dict[str,List]):
    docs = []
    for _, data in obj.items():
        docs.extend(data)
    return docs


@dispatch
def read_records(obj: Dict[str,Dict]):
    """Reads a dict of dicts, assume its tinydb format"""
    docs = []
    for data in obj.values():
        for d in data.values():
            docs.append(d)
    return docs


class JsonLoader:
    def __init__(self, path, **storage_kwargs):
        self.path = path
        self.storage_kwargs = storage_kwargs

    def read(self, schema=None) -> list[dict]:
        with fsspec.open_files(self.path, **self.storage_kwargs) as fs:
            if len(fs):
                docs = read_records(fs)
            else:
                docs =[]
        if schema is not None:
            docs = [schema(**doc).pandas_dict() for doc in docs]
            df = pd.DataFrame(docs)
            idx_names = list(schema.get_index_fields())
            if len(idx_names) == 1:
                idx_names = idx_names[0]
            df = df.set_index(idx_names)
            return df
        return docs

    def __call__(self, schema=None) -> list[dict]:
        return self.read(schema)
