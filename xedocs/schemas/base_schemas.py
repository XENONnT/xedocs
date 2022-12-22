import re
from typing import ClassVar

import rframe
from .._settings import settings


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class XeDoc(rframe.BaseSchema):
    __STAGING_DB__: ClassVar[str] = "xedocs-dev"
    __PRODUCTION_DB__: ClassVar[str] = "xedocs"

    _ALIAS: ClassVar = ""
    _CATEGORY: ClassVar = "general"

    _XEDOCS = {}

    class Config:
        allow_population_by_field_name = True

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if "_ALIAS" not in cls.__dict__:
            cls._ALIAS = camel_to_snake(cls.__name__)

        if cls._ALIAS and cls._ALIAS not in cls._XEDOCS:
            cls._XEDOCS[cls._ALIAS] = cls
            import xedocs
            xedocs.register_default_storage(cls)   

    @classmethod
    def default_datasource(cls):
        """This method is called when a query method is
        called and no datasource is passed.
        """
        import xedocs
        return xedocs.get_datasource_for(cls)

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

    def __repr__(self):
        idx_str = ", ".join(
            [f"{attr}={getattr(self, attr)}" for attr in self.get_index_fields()]
        )
        values_str = ", ".join(
            [f"{attr}={getattr(self, attr)}" for attr in self.get_column_fields()]
        )

        header = f"Xenon {type(self).__name__} Document"
        repr_str = f"""
        {header}
        {len(header)*'-'}
 
        Category:      {self._CATEGORY}
        Alias:         {self._ALIAS}
        Index:         {idx_str}
        Values:        {values_str}
        """
        return repr_str


class VersionedXeDoc(XeDoc):
    _ALIAS = ""

    version: str = rframe.Index(max_length=20)
