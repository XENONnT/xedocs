

import utilix
import xedocs

from utilix import xent_collection
from rframe import BaseSchema
from xedocs import settings


def utilix_datasource(schema: BaseSchema, mode='analyst'):
    if utilix.uconfig is None:
        return None

    database = getattr(schema, f'__{mode.capitalize()}_DB__', None)
    if database is None:
        database = getattr(settings, f"{mode.capitalize()}_DB", "xedocs")
    collection = schema.default_collection_name()
    return xent_collection(collection=collection, database=database)


def analyst_db_source(schema: BaseSchema):
    return utilix_datasource(schema, mode='analyst')


def straxen_db_source(schema: BaseSchema):
    return utilix_datasource(schema, mode='straxen')
