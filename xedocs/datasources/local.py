
from xedocs import settings
from xedocs.schemas import XeDoc

from tinydb import TinyDB


def get_local_source_for(schema: XeDoc, db='analyst_db'):
    path = settings.local_path_for_schema(schema, db=db)
    if path.exists():
        db = TinyDB(path.absolute())
        return db.table(schema._ALIAS)


def analyst_db_local_source(schema: XeDoc):
    return get_local_source_for(schema, db='analyst_db')


def straxen_db_local_source(schema: XeDoc):
    return get_local_source_for(schema, db='straxen_db')
