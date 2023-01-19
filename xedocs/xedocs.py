"""Main module."""

from pathlib import Path
import pandas as pd

from collections import defaultdict
from typing import Dict, List, Type, Union
from rframe import DataAccessor
from tqdm.auto import tqdm

from ._settings import settings
from .schemas import XeDoc

__all__ = [
    "help",
    "get_accessor",
    "find_docs",
    "find_iter",
    "find_df",
    "find_one",
    "insert_docs",
    "list_schemas",
    "all_schemas",
    "schemas_by_category",
    "find_schema",
    "download_db",
]


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


def get_accessor(schema, db=settings.DEFAULT_DATABASE):
    schema = find_schema(schema)

    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )
    if db is None:
        db = settings.DEFAULT_DATABASE
    if isinstance(db, str):
        accessor = getattr(schema, db)
    else:
        accessor = DataAccessor(schema, db)

    return accessor


def help(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return schema.help()


def default_datasource_for(schema):
    schema = find_schema(schema)

    return settings.default_datasource_for_schema(schema)


def get_api_client(schema, database=settings.DEFAULT_DATABASE):
    interface_class = settings._DATABASE_INTERFACE_CLASSES.get("api", None)
    if interface_class is None:
        raise ValueError("No API interface class found.")
    interface = interface_class(database)
    schema = find_schema(schema)
    return interface.datasource_for_schema(schema)


def download_db(
    dbname=settings.DEFAULT_DATABASE, schemas=None, path=None, batch_size=10_000, verbose=True
):
    """Download data from a remote database to a local database."""
    import tinydb

    if schemas is None:
        schemas = list_schemas()

    if not isinstance(schemas, list):
        schemas = [schemas]

    with tqdm(total=len(schemas)) as pbar:

        for schema in schemas:
            schema = find_schema(schema)
            accessor = get_accessor(schema, dbname)
            pbar.set_description(f"Downloading {schema._ALIAS}")

            basepath = None

            if path is None:
                path = settings.DATA_DIR

            interface = settings._database_interfaces.get(dbname, {}).get(
                "local_repo", None
            )

            if interface is None:
                basepath = Path(path) / dbname / schema._CATEGORY / schema._ALIAS
            else:
                basepath = interface.base_path_for_schema(schema)

            def write_docs(docs, num=1):
                fpath = basepath / f"{num}.json"
                db = tinydb.TinyDB(fpath, create_dirs=True, indent=4)
                table = db.table(schema._ALIAS)
                table.truncate()
                table.insert_multiple(docs)

            filenum = 1
            docs = []
            with tqdm(
                total=accessor.count(), desc=schema._ALIAS, leave=verbose
            ) as pbar2:
                for doc in accessor.find_iter():
                    docs.append(doc.jsonable())
                    pbar2.update(1)
                    if len(docs) >= batch_size:
                        write_docs(docs, filenum)
                        docs = []
                        filenum += 1
                if len(docs) > 0:
                    write_docs(docs, filenum)

            pbar.update(1)
