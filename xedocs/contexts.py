from collections import defaultdict


from rframe import DataAccessor
from xedocs import all_schemas, schemas_by_category


class XedocsContext:
    _schemas: dict
    _overrides: dict
    _db_name: str

    def __init__(self, schemas: dict = None, db_name=None, overrides=None):

        self._db_name = db_name

        if schemas is None:
            schemas = all_schemas()
        self._schemas = schemas

        if overrides is None:
            overrides = {}
        self._overrides = overrides

    def get_accessor(self, schema, name=None):
        if name is None:
            name = schema._ALIAS
        if name in self._overrides:
            return DataAccessor(schema, self._overrides[name])
        return getattr(schema, self._db_name, None)

    def __getitem__(self, key):
        schema = self._schemas.get(key, None)
        if schema is None:
            raise KeyError(f"No schema named {key} found")

        if isinstance(schema, dict):
            return XedocsContext(
                schema, db_name=self._db_name, overrides=self._overrides
            )

        accessor = self.get_accessor(schema, name=key)

        if accessor is None:
            raise KeyError(f"No accessor named {key} found")

        return accessor

    def __getattr__(self, attr):
        if attr in self._schemas.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return super().__dir__() + list(self._schemas.keys())


def straxen_db(schemas=None, datasource_overrides=None, by_category=False):
    if schemas is None:
        if by_category:
            schemas = schemas_by_category()
        else:
            schemas = all_schemas()

    return XedocsContext(schemas, db_name="straxen_db", overrides=datasource_overrides)


def analyst_db(schemas=None, datasource_overrides=None, by_category=False):
    if schemas is None:
        if by_category:
            schemas = schemas_by_category()
        else:
            schemas = all_schemas()

    return XedocsContext(schemas, db_name="analyst_db", overrides=datasource_overrides)
