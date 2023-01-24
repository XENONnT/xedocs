"""Attempt to register URConfig protocol if straxen
is installed.
"""
import straxen
from xedocs import settings


@straxen.URLConfig.register("xedocs")
def xedocs_protocol(
    name, db=settings.DEFAULT_DATABASE, sort=None, attr=None, as_list=False, **labels
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

    kwargs = straxen.filter_kwargs(labels, accessor.find_docs)
    
    if isinstance(sort, (str,list)):
        kwargs["sort"] = sort

    if not as_list:
        kwargs["limit"] = 1

    docs = accessor.find_docs(**kwargs)

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
