
from rframe import BaseSchema

from ._settings import settings, uconfig, xent_collection


def api_client(schema, mode='analyst'):
    import xedocs

    url = settings.api_url_for_schema(schema, mode=mode)

    return xedocs.api.api_client(url, token=settings.API_TOKEN, authenticator=settings)


def utilix_datasource(schema: BaseSchema, mode='analyst'):
    if uconfig is None:
        return None

    database = getattr(schema, f'__{mode.capitalize()}_DB__', None)
    if database is None:
        database = getattr(settings, f"{mode.capitalize()}_DB", "xedocs")
    collection = schema.default_collection_name()
    return xent_collection(collection=collection, database=database)


def default_datasource(schema, mode='analyst'):
    datasource = utilix_datasource(schema, mode=mode)
    if datasource is None:
        datasource = api_client(schema, mode=mode)
    return datasource        


def get_datasource_for(schema, mode='analyst'):
    if schema._ALIAS in settings.datasources:
        return settings.datasources[schema._ALIAS]

    return default_datasource(schema, mode=mode)


def register_default_storage(schema: BaseSchema):
    if uconfig is not None:
        if not hasattr(schema, "analyst_db"):
            try:
                schema.register_datasource(utilix_datasource(schema), name='analyst_db')
            except:
                pass
        if not hasattr(schema, "straxen_db"):
            try:
                schema.register_datasource(utilix_datasource(schema, mode='straxen'), name='straxen_db')
            except:
                pass

    if not hasattr(schema, "analyst_db_api"):
        try:
            schema.register_datasource(api_client(schema), name='analyst_db_api')
        except:
            pass

    if not hasattr(schema, "straxen_db_api"):
        try:
            schema.register_datasource(api_client(schema, mode='straxen'), name='straxen_db_api')
        except:
            pass
