
from xedocs import settings
from xedocs.schemas import XeDoc

from tinydb import TinyDB


def get_source(schema: XeDoc):
    path = settings.local_path_for_schema(schema)
    if path.exists():
        db = TinyDB(path.absolute())
        return db.table(schema._ALIAS)
