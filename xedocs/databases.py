from .utils import Database
from .xedocs import schemas_by_category, all_schemas
from .data_locations.mongodb import MongoDB
from .data_locations.corrections_repo import CorrectionsRepo
from .data_locations.api import XedocsApi
from .data_locations.data_folder import DataFolder
from .data_locations.sqlite_corrections import SQLiteCorrections
import utilix

def straxen_db():
    # Check if sqlite is active
    if hasattr(utilix, "sqlite_backend"):
        sqlite_cfg = utilix.sqlite_backend._load_sqlite_config()
        sqlite_active = sqlite_cfg.sqlite_active()
    else:
        sqlite_active = False

    if not sqlite_active:
        # Proceed with the normal MongoDB backend
        schemas = all_schemas()
        db = MongoDB.from_utilix()
        accessors = {name: db.data_accessor(schema) for name, schema in schemas.items()}
        return Database(accessors)
    else:
        # Proceed with the local sqlite corrections backend
        db = utilix.sqlite_backend.SQLiteCorrections(sqlite_path=sqlite_cfg.xedocs_sqlite_path)
        return db.get_datasets()


def corrections_db():
    schemas = schemas_by_category()['corrections']
    db = MongoDB.from_utilix()
    accessors = {name: db.data_accessor(schema) for name, schema in schemas.items()}
    return Database(accessors)


def corrections_repo(branch=None, username=None, token=None):
    kwargs = {}
    if branch is not None:
        kwargs["branch"] = branch
    if username is not None:
        kwargs["username"] = username
    if token is not None:
        kwargs["token"] = token
    repo = CorrectionsRepo(**kwargs)
    return repo.get_datasets()


def xedocs_api(login=True):
    api = XedocsApi()
    if login:
        api.login()
    return api.get_datasets()


def default_db():
    return straxen_db()


def development_db():
    schemas = all_schemas()
    db = MongoDB.from_utilix(db_name='xedocs-dev')
    accessors = {name: db.data_accessor(schema) for name, schema in schemas.items()}
    return Database(accessors)


def local_mongo_db(**kwargs):
    schemas = all_schemas()
    db = MongoDB(**kwargs)
    accessors = {name: db.data_accessor(schema) for name, schema in schemas.items()}
    return Database(accessors)


def local_folder(path: str = None, **kwargs):
    if path is None:
        raise ValueError("Path must be set")
    repo = DataFolder(root=path, **kwargs)
    return repo.get_datasets()