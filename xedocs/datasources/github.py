
import tinydb

from xedocs import settings
from xedocs.schemas import XeDoc
from rframe.interfaces.tinydb import FsspecStorage


def github_source(schema: XeDoc):
    url = settings.github_url_for_schema(schema)
    db = tinydb.TinyDB(url, 
        storage=FsspecStorage,
        username=settings.GITHUB_USERNAME, 
        token=settings.GITHUB_TOKEN)
    return db.table(schema._ALIAS)
