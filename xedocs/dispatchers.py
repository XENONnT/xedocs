import fsspec
import rframe
import pandas as pd

from io import IOBase
from typing import Any, List
from plum import dispatch

from xedocs.json_records import read_records

from .regex_dispatcher import RegexDispatcher


@dispatch
def json_serializable(value: Any):
    return value


@dispatch
def json_serializable(value: list):
    return [json_serializable(v) for v in value]


@dispatch
def json_serializable(value: tuple):
    return tuple(json_serializable(v) for v in value)


@dispatch
def json_serializable(value: dict):
    return {json_serializable(k): json_serializable(v) for k, v in value.items()}


@dispatch
def json_serializable(value: pd.Interval):
    return json_serializable((value.left, value.right))


@dispatch
def json_serializable(value: rframe.IntegerInterval):
    return value.left, value.right


@dispatch
def json_serializable(value: rframe.TimeInterval):
    return f"{str(value.left)} to {str(value.right)}"


read_files = RegexDispatcher('read_files')


@read_files.register(r'.*\.csv')
def read_csv_files(path, **kwargs) -> List[dict]:
    docs =[]
    
    with fsspec.open_files(path, **kwargs) as fs:
         kwargs = rframe.utils.filter_kwargs(pd.read_csv, kwargs)
         for f in fs:
            ds = pd.read_csv(f, **kwargs).to_dict(orient='records')
            docs.extend(ds)
    return docs


@read_files.register(r'.*\.json')
def read_json_files(path, **kwargs) -> List[dict]:
    with fsspec.open_files(path, **kwargs) as fs:
        docs = read_records(fs)
    return docs


@read_files.register(r'.*\.parquet')
@read_files.register(r'.*\.pq')
def read_parquet_files(path, **kwargs) -> List[dict]:
    docs =[]
    
    with fsspec.open_files(path, **kwargs) as fs:
        kwargs = rframe.utils.filter_kwargs(pd.read_parquet, kwargs)
        for f in fs:
            ds = pd.read_parquet(f, **kwargs).to_dict(orient='records')
            docs.extend(ds)
    return docs

@read_files.register(r'.*\.xlsx')
@read_files.register(r'.*\.xls')
def read_excel_files(path, **kwargs) -> List[dict]:
    docs =[]
    with fsspec.open_files(path, **kwargs) as fs:
        kwargs = rframe.utils.filter_kwargs(pd.read_excel, kwargs)
        for f in fs:
            ds = pd.read_excel(f, **kwargs).to_dict(orient='records')
            docs.extend(ds)
    return docs


@read_files.register(r'.*\.pkl')
def read_pickle_files(path, **kwargs) -> List[dict]:
    docs =[]
    with fsspec.open_files(path, **kwargs) as fs:
        kwargs = rframe.utils.filter_kwargs(pd.read_pickle, kwargs)
        for f in fs:
            ds = pd.read_pickle(f, **kwargs).to_dict(orient='records')
            docs.extend(ds)
    return docs
