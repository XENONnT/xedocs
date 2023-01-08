
import xedocs
from rframe import BaseSchema
from xedocs import settings

def api_client_for(schema, mode='analyst'):
    import xedocs

    url = settings.api_url_for_schema(schema, mode=mode)

    return xedocs.api.api_client(url, token=settings.API_TOKEN, authenticator=settings)


def analyst_db_api_source(schema: BaseSchema):
    return api_client_for(schema, mode='analyst')


def straxen_db_api_source(schema: BaseSchema):
    return api_client_for(schema, mode='straxen')


def register_source(schema: BaseSchema):
    if not hasattr(schema, "analyst_db_api"):
        try:
            source = api_client_for(schema)
            schema.register_datasource(source, name='analyst_db_api')
        except:
            pass

    if not hasattr(schema, "straxen_db_api"):
        try:
            source = api_client_for(schema, mode='straxen')
            schema.register_datasource(source, name='straxen_db_api')
        except:
            pass
