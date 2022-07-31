import re
from typing import ClassVar

import rframe
from .._settings import settings


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class XeDoc(rframe.BaseSchema):
    _ALIAS: ClassVar = ""
    _CATEGORY: ClassVar = "general"

    _XEDOCS = {}

    class Config:
        allow_population_by_field_name = True

    def __init_subclass__(cls) -> None:

        if "_ALIAS" not in cls.__dict__:
            cls._ALIAS = camel_to_snake(cls.__name__)

        if cls._ALIAS and cls._ALIAS not in cls._XEDOCS:
            cls._XEDOCS[cls._ALIAS] = cls

    @classmethod
    def default_datasource(cls):
        """This method is called when a query method is
        called and no datasource is passed.
        """
        return settings.get_datasource_for(cls)

    @classmethod
    def default_database_name(cls):
        return "xedocs"

    @classmethod
    def default_collection_name(cls):
        return cls._ALIAS

    @classmethod
    def help(cls):
        help_str = f"""
            Schema name:   {cls.__name__}
            Alias:         {cls._ALIAS}
            Index fields:  {list(cls.get_index_fields())}
            Column fields: {list(cls.get_column_fields())}
        """
        print(help_str)


class VersionedXeDoc(XeDoc):
    _ALIAS = ""

    version: str = rframe.Index(max_length=20)

    def pre_delete(self, datasource):
        raise IndexError("Versioned documents are append-only.")
