"""Main module."""

import pandas as pd

from collections import defaultdict
from typing import ClassVar, Dict, List, Type, Union


from ._settings import settings
from .schemas import XeDoc


def find_docs(schema, datasource=None, **labels):
    if isinstance(schema, str):
        schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )
    """Find a document in a datasource."""
    # labels, extra = schema.extract_labels(**kwargs)
    return schema.find(datasource, **labels)


def find_df(schema, datasource=None, **labels):
    if isinstance(schema, str):
        schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc or the name of a known schema."
        )
    """Find a document in a datasource."""
    return schema.find_df(datasource, **labels)


def find_one(schema, datasource=None, **kwargs):
    if isinstance(schema, str):
        schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc or the name of a known schema."
        )
    """Find a document in a datasource."""
    labels, extra = schema.extract_labels(**kwargs)
    return schema.find_one(datasource, **labels)


def insert_docs(schema: str, docs: Union[list, dict, pd.DataFrame], datasource=None):
    if isinstance(docs, pd.DataFrame):
        docs = docs.reset_index().to_dict(orient="records")
    if not isinstance(docs, list):
        docs = [docs]
    if isinstance(schema, str):
        schema = find_schema(schema)

    inserted = []
    for data in docs:
        doc = schema(**data)
        doc.save(datasource)
        inserted.append(doc)

    return inserted


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
    schema = XeDoc._XEDOCS.get(name, None)
    if schema is not None:
        return schema
    for schema in XeDoc._XEDOCS.values():
        if schema.__name__ == name:
            return schema
    raise KeyError(f"Correction with name {name} not found.")


def help(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return schema.help()


def get_api_client(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return settings.api_client(schema)


try:
    """Attempt to register URConfig protocol if straxen
    is installed.
    """
    import straxen

    @straxen.URLConfig.register("xedocs")
    def xedocs_protocol(
        name, db="production_db", sort=None, attr=None, as_list=False, **labels
    ):
        """URLConfig protocol for fetching values from
            a xedocs database.
        ::param name: Name of the schema.
        ::param context: Context of the document.
        ::param version: Version of the documents to filter by.
        ::param sort: Attribute of the documents to sort on.
        ::param attr: Attribute of the documents to return.
        ::param labels: Label values to filter by to return.
        """
        import xedocs

        # Find the document schema
        schema = xedocs.find_schema(name)

        accessor = getattr(schema, db)

        if sort is not None:
            labels['sort'] = sort

        docs = accessor.find_docs(**labels)

        if not docs:
            raise KeyError(f"No matching documents found for {name}.")

        if isinstance(sort, str):
            docs = sorted(docs, key=lambda x: getattr(x, sort))
        elif sort:
            docs = sorted(docs)

        if attr is not None:
            docs = [getattr(d, attr) for d in docs]

        if not as_list:
            return docs[0]

        return docs

except ImportError:
    pass
