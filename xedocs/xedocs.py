"""Main module."""

from typing import ClassVar

from ._settings import settings
from .schemas import XeDoc


def find(schema, datasource=None, **kwargs):
    if isinstance(schema, str):
        schema = find_schema(schema)
    if not issubclass(schema, XeDoc):
        raise TypeError(
            "Schema must be a subclass of XeDoc" "or the name of a known schema."
        )
    """Find a document in a datasource."""
    labels, extra = schema.extract_labels(**kwargs)
    return schema.find(datasource, **labels)


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


def list_schemas():
    return list(XeDoc._XEDOCS)


def all_schemas():
    return dict(XeDoc._XEDOCS)


def find_schema(name):
    schema = XeDoc._XEDOCS.get(name, None)
    if schema is None:
        raise KeyError(f"Correction with name {name} not found.")
    return schema


def help(schema):
    if isinstance(schema, str):
        schema = find_schema(schema)
    return schema.help()


try:
    '''Attempt to register URConfig protocol if straxen
    is installed.
    '''
    from straxen import URLConfig

    @URLConfig.register("xedocs")
    def xedocs_protocol(name, version="ONLINE", sort=None, attr=None, **kwargs):
        """URLConfig protocol for fetching values from
        correction documents.
        """
        docs = find(name, version=version, **kwargs)

        if not docs:
            raise KeyError(f"No matching documents found for {name}.")

        if isinstance(sort, str):
            docs = sorted(docs, key=lambda x: getattr(x, sort))
        elif sort:
            docs = sorted(docs)

        if attr is not None:
            docs = [getattr(d, attr) for d in docs]

        if len(docs) == 1:
            return docs[0]

        return docs

except ImportError:
    pass
