import datetime
from typing import ClassVar, Literal
from pydantic import constr
import rframe

from xedocs import settings

from .base_corrections import BaseCorrectionSchema, TimeIntervalCorrection


class CorrectionReference(TimeIntervalCorrection):
    """A CorrectionReference document references one or
    more corrections by storing the name and labels required
    to locate the correction in a datasource
    """

    _ALIAS = ""

    # arbitrary alias for this reference,
    # this should match the straxen config name
    alias: str = rframe.Index(max_length=50)

    # the global version
    version: str = rframe.Index(max_length=20)

    # validity interval of the document
    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex()

    # Name of the correction being referenced
    correction: constr(max_length=50)

    # The attribute in the correction being referenced e.g `value`
    attribute: constr(max_length=50)

    # The index labels being referenced, eg pmt=[1,2,3], version='v3' etc.
    labels: dict

    def load(self, datasource=None, **overrides):
        """Load the referenced documents from the
        given datasource.
        """
        labels = dict(self.labels, **overrides)
        if self.correction not in BaseCorrectionSchema._CORRECTIONS:
            raise KeyError(f"Reference to undefined schema name {self.correction}")
        schema = BaseCorrectionSchema._CORRECTIONS[self.correction]
        return schema.find(datasource, **labels)

    @property
    def url_config(self):
        """Convert reference to a URLConfig URL"""
        import straxen

        url = f"{self.correction}://{self.attribute}"
        url = straxen.URLConfig.format_url_kwargs(url, **self.labels)
        return url

    @property
    def config_dict(self):
        return {self.name: self.url_config}


class BaseResourceReference(TimeIntervalCorrection):
    _ALIAS = ""

    fmt: ClassVar = "text"

    value: str

    def pre_insert(self, datasource):
        """require the existence of the resource
        being referenced prior to inserting a new
        document. This is to avoid typos etc.
        """
        self.load()
        super().pre_insert(datasource)

    def load(self, **kwargs):
        import straxen

        kwargs.setdefault("fmt", self.fmt)

        return straxen.get_resource(self.value, **kwargs)

    @property
    def url_config(self):
        return f"resource://{self.value}?fmt={self.fmt}"


class BaseMap(BaseResourceReference):
    _ALIAS = ""

    algorithm: Literal["cnn", "gcn", "mlp"] = rframe.Index()

    value: str
