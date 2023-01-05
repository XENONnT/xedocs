"""Main module."""

import pandas as pd

from collections import defaultdict
from typing import ClassVar, Dict, List, Type, Union
from rframe import DataAccessor

from ._settings import settings
from .schemas import XeDoc


def find_docs(schema, datasource=None, **labels):
    """find documents by labels

    Args:
        schema (Union[XeDoc,str]): A Xedocs schema or name/alias of one.
        datasource (optional): compatible datasource or name of known source. Defaults to None.
        **labels: label selections
    Returns:
        List[XeDoc]: a list of documents matching selection.
    """

    accessor = get_accessor(schema, datasource)

    return accessor.find_docs(**labels)


def find_iter(schema, datasource=None, **labels):
    """find documents by labels, return iterator

    Args:
        schema (Union[XeDoc,str]): A Xedocs schema or name/alias of one.
        datasource (optional): compatible datasource or name of known source. Defaults to None.
        **labels: label selections
    Returns:
        Iterator[XeDoc]: an iterator over documents matching selection.
    """

    accessor = get_accessor(schema, datasource)

    return accessor.find_iter(**labels)


def find_df(schema, datasource=None, **labels):
    """find dataframe by labels

    Args:
        schema (Union[XeDoc,str]): A Xedocs schema or name/alias of one.
        datasource (optional): compatible datasource or name of known source. Defaults to None.
        **labels: label selections
    Returns:
        DataFrame: a pandas dataframe matching selection.
    """

    accessor = get_accessor(schema, datasource)

    return accessor.find_df(**labels)


def find_one(schema, datasource=None, **labels):
    """find dataframe by labels

    Args:
        schema (Union[XeDoc,str]): A Xedocs schema or name/alias of one.
        datasource (optional): compatible datasource or name of known source. Defaults to None.
        **labels: label selections
    Returns:
        Optional[XeDoc]: The first document matching selection or None.
    """

    accessor = get_accessor(schema, datasource)

    return accessor.find_one(**labels)


def insert_docs(schema: str, docs: Union[list, dict, pd.DataFrame], datasource=None):
    if isinstance(docs, pd.DataFrame):
        docs = docs.reset_index().to_dict(orient="records")
    if not isinstance(docs, list):
        docs = [docs]
    accessor = get_accessor(schema, datasource)

    return accessor.insert(docs)


def list_schemas() -> List[str]:
    return list(XeDoc._XEDOCS)


def all_schemas() -> Dict[str, Type[XeDoc]]:
    return dict(XeDoc._XEDOCS)


def schemas_by_category() -> Dict[str,Dict[str, Type[XeDoc]]]:
    d = defaultdict(dict)
    for name, schema in all_schemas().items():
        d[schema._CATEGORY][name] = schema
    return d


def find_schema(name) -> Type[XeDoc]:
    
    if isinstance(name, type) and issubclass(name, XeDoc):
        return name

    if not isinstance(name, str):
        raise TypeError(f"Schema name must be a string or XeDoc class, not {type(name)}")

    if schema is not None:
        return schema
    
    for schema in XeDoc._XEDOCS.values():
        if schema.__name__ == name:
            return schema
    
    raise KeyError(f"Correction with name {name} not found.")


def get_accessor(schema, db='analyst_db'):
    schema = find_schema(schema)

    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )
    if db is None:
        db = 'analyst_db'
    if isinstance(db, str):
        accessor = getattr(schema, db)
    else:
        accessor = DataAccessor(schema, db)

    return accessor


def help(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return schema.help()


def get_api_client(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return settings.api_client(schema)

