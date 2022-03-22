import re
from typing import ClassVar

import rframe
from .._settings import settings

def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class XeDoc(rframe.BaseSchema):
    _NAME: ClassVar = ""
    _XEDOCS = {}

    def __init_subclass__(cls) -> None:

        if "_NAME" not in cls.__dict__:
            cls._NAME = camel_to_snake(cls.__name__)

        if cls._NAME:
            if cls._NAME not in cls._XEDOCS:
                cls._XEDOCS[cls._NAME] = cls
    @classmethod
    def default_datasource(cls):
        """This method is called when a query method is
        called and no datasource is passed.
        """
        return settings.get_datasource_for(cls._NAME)

    @classmethod
    def default_collection_name(cls):
        return cls._NAME

    @classmethod
    def help(cls):
        help_str = f"""
            Schema name: {cls._NAME}
            Index fields: {list(cls.get_index_fields())}
            Column fields: {list(cls.get_column_fields())}
        """
        print(help_str)


class VersionedXeDoc(XeDoc):
    version: str = rframe.Index()
