"""Attempt to register URConfig protocol if straxen
is installed.
"""
import straxen

import xedocs

DB_CACHE = {}

def get_accessor(name, db=None, **kwargs):
    if db is None:
        db = "straxen_db"
    db_func = getattr(xedocs.databases, db)
    db_kwargs = {k[4:] : v for k,v in kwargs.items() if k.startswith("db__")}
    db_key = (db, )
    if len(db_kwargs):
        db_key = db_key + tuple(sorted(db_kwargs.items()))
    if db_key not in DB_CACHE:
        DB_CACHE[db_key] = db_func(**db_kwargs)
    db = DB_CACHE[db_key]
    if name not in db:
        raise KeyError(f"{db_key} database has no such collection: {name}")
    return db[name]


@straxen.URLConfig.register("xedocs")
def xedocs_protocol(
    name, db=None, sort=None, attr=None, as_list=False, **labels
):
    """URLConfig protocol for fetching values from
        a xedocs database.
    ::param name: Name of the schema.
    ::param db: Database to load the data from.
    ::param version: Version of the documents to filter by.
    ::param sort: Attribute of the documents to sort on.
    ::param attr: Attribute of the documents to return.
    ::param labels: Label values to filter by to return.
    """

    accessor = get_accessor(name, db=db, **labels)

    kwargs = straxen.filter_kwargs(accessor.find_docs, labels)
    
    if isinstance(sort, (str,list)):
        kwargs["sort"] = sort

    if not as_list:
        kwargs["limit"] = 1

    docs = accessor.find_docs(**kwargs)

    if not docs:
        raise KeyError(
            f"No matching documents found for {name}. "
            "It is possible that there is no corresponding data."
        )

    if isinstance(sort, str):
        docs = sorted(docs, key=lambda x: getattr(x, sort))
    elif sort:
        docs = sorted(docs)

    if attr is not None:
        docs = [getattr(d, attr) for d in docs]

    if not as_list:
        return docs[0]

    return docs
