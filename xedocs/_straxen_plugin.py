
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
