"""Main module."""

from pathlib import Path
import pandas as pd

from collections import defaultdict
from typing import Dict, List, Type, Union
from rframe import DataAccessor
from tqdm.auto import tqdm

from ._settings import settings
from .schemas import XeDoc
from .data_locations.mongodb import MongoDB


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


def insert_docs(schema: str, docs: Union[list, dict, pd.DataFrame], datasource=None, dry=False):
    # Currently stuck on how to deal with instances of schemas
    if datasource == 'straxen_db': # switch to straxen_db
        mongo_username = MongoDB().username
        if mongo_username == 'corrections_expert':
            # If statements only trigger
            target_version = "ONLINE"
            # Note to self: This is done in a very dumb way, fix later
            ONLINE_check = True
            if isinstance(docs, pd.DataFrame):
                ONLINE_check = (docs['version'] == target_version).all()

            elif isinstance(docs, dict):
                ONLINE_check = all(item['version'] == target_version for item in docs)

            else:
                if isinstance(docs, list):
                    if isinstance(docs[0], list) or isinstance(docs[0], dict):
                        # It could be a list of dicts, or list or schemas...
                        # This can be an actual list or a list of docs
                        # these cannot be treated the same
                        ONLINE_check = all(item['version'] == target_version for item in docs)
                    else:
                        # This assumes the last choice is a schema, if not other things will yield errors?
                        # This is kinda sloppy...
                        ONLINE_check = all(item.version == target_version for item in docs)
                elif hasattr(docs, 'version'):
                    if docs.version != target_version: # if version isnt ONLINE
                        ONLINE_check = False
                else:
                    ONLINE_check = all(item.version == target_version for item in docs)

            if not ONLINE_check:
                raise ValueError("You are attempting to modify the a straxen_db correction whose version is not ONLINE")

    if isinstance(docs, pd.DataFrame):
        docs = docs.reset_index().to_dict(orient="records")
    if not isinstance(docs, list):
        docs = [docs]
    accessor = get_accessor(schema, datasource)

    return accessor.insert(docs, dry=dry)


def list_schemas() -> List[str]:
    return list(XeDoc._XEDOCS)


def all_schemas() -> Dict[str, Type[XeDoc]]:
    return dict(XeDoc._XEDOCS)


def schemas_by_category() -> Dict[str, Dict[str, Type[XeDoc]]]:
    d = defaultdict(dict)
    for name, schema in all_schemas().items():
        d[schema._CATEGORY][name] = schema
    return d


def find_schema(name) -> Type[XeDoc]:

    if isinstance(name, type) and issubclass(name, XeDoc):
        return name

    if not isinstance(name, str):
        raise TypeError(
            f"Schema name must be a string or XeDoc class, not {type(name)}"
        )

    schema = XeDoc._XEDOCS.get(name, None)

    if schema is not None:
        return schema

    for schema in XeDoc._XEDOCS.values():
        if schema.__name__ == name:
            return schema

    raise KeyError(f"Correction with name {name} not found.")


def get_accessor(schema, db=None):
    import xedocs

    schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )

    if db is None:
        db = settings.DEFAULT_DATABASE
    if isinstance(db, str):
        db = getattr(xedocs.databases, db)
    if callable(db):
        db = db()
    return db[schema._ALIAS]


def help(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return schema.help()


def default_datasource_for(schema):
    schema = find_schema(schema)
    accessor = get_accessor(schema)
    return accessor.storage


def get_api_client(schema):
    from .databases import xedocs_api
    schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )
    db = xedocs_api()
    return db[schema._ALIAS]


def sync_dbs(from_db, to_db, schemas=None, dry=False):
    import xedocs

    if isinstance(from_db, str):
        from_db = getattr(xedocs.databases, from_db)()

    if isinstance(to_db, str):
        to_db = getattr(xedocs.databases, to_db)()

    results = {}
    for name, accessor in tqdm(from_db.items(), desc="Syncing databases"):
        if schemas is None or name in schemas:
            sort=None
            if "time" in accessor.schema.get_index_fields():
                sort = "time"
            docs = accessor.find_docs(sort=sort)
            if name not in to_db:
                continue
            results[name] = to_db[name].insert(docs, raise_on_error=False, dry=dry)

    return results
