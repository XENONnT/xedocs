import datetime
import re
from typing import ClassVar
from pydantic import validator

import pandas as pd
import rframe

from ..._settings import settings

from ..base_schemas import XeDoc


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class BaseCorrectionSchema(XeDoc):
    """Base class for all correction schemas.
    This class ensures:
        - the _NAME attribute is always unique
        - schema includes a version index
        - changing already set values is disallowed

    """

    _NAME: ClassVar = ""
    _CORRECTIONS = {}

    version: str = rframe.Index()

    created_date: datetime.datetime = datetime.datetime.utcnow()
    comments: str = ""

    def __init_subclass__(cls) -> None:

        if cls._NAME:
            if cls._NAME not in cls._CORRECTIONS:
                cls._CORRECTIONS[cls._NAME] = cls

        super().__init_subclass__()


    def pre_update(self, datasource, new):
        """This method is called if the `new` document is
        being saved and self was found to already exist in
        the datasource. By default we check that all values
        are the same. The reason this execption is needed is
        because the found document may not actually exist in
        the datasource and may be interpolated, so we allow
        updating documents with identical values.
        Otherwise we raise an error, preventing the update.
        """

        if not self.same_values(new):
            index = ", ".join([f"{k}={v}" for k, v in self.index_labels.items()])
            raise IndexError(f"Values already set for {index}")


class TimeIntervalCorrection(BaseCorrectionSchema):
    """Base class for time-interval corrections
        - Adds an Interval index of type datetime
        - Enforces rules on updating intervals:
          Can only change the right side of an interval
          if right side is None and the new right side is
          after the cutoff time (default is 2 hours after current time).
    The cutoff is set to prevent values changing after already being used
    for processing data.
    """
    class Config:
        allow_population_by_field_name = True
        
    _NAME = ""

    time: rframe.Interval[datetime.datetime] = rframe.IntervalIndex(alias='run_id')

    @validator('time', pre=True)
    def run_id_to_time(cls, v):
        """Convert run id to time"""
        if isinstance(v, (str, int)):
            try:
                v = settings.run_id_to_time(v)
            except:
                pass
        return v

    @classmethod
    def url_protocol(cls, attr, **labels):
        labels["time"] = settings.extract_time(labels)
        return super().url_protocol(attr, **labels)

    def pre_update(self, datasource, new):
        """Since intervals can extend beyond the current time,
        we want to allow changes to the end time shortening the interval
        to a point in the future since these values have not yet
        been used for processing.
        """
        current_left = self.time.left
        current_right = self.time.right
        new_left = new.time.left
        new_right = new.time.right

        clock = settings.clock
        cutoff = clock.cutoff_datetime(buffer=60)

        if clock.after_cutoff(current_left) and clock.after_cutoff(new_left):
            # current and new interval are completely in the future
            # all changes are allowed
            return

        if current_right > new_right:
            # Interval is being shortened.
            # We only allow shortening intervals that extend beyong the cutoff time
            assert clock.after_cutoff(
                current_right
            ), f"Can only shorten intervals \
                                                        that ends after {cutoff}"

            # The resulting interval must extend beyong the cutoff time
            assert clock.after_cutoff(
                new_right
            ), f"Can only shorten an interval \
                                                    to end after {cutoff}"

        # Only allow changes to the right side of the interval
        assert (
            current_left == new_left
        ), f"Can only change endtime of existing interval. \
                                           start time must be {self.time.left}"

        # Only allow changes to the interval, not the values
        assert self.same_values(new), f"Values already set for {self.index_labels}."


def can_extrapolate(doc):
    # only extrapolate ONLINE versions
    # and up until the current time.
    if doc["version"] == "ONLINE":
        ts = pd.to_datetime(doc["time"]).to_pydatetime()
        clock = settings.clock
        return not clock.after_cutoff(ts)

    return False


class TimeSampledCorrection(BaseCorrectionSchema):
    """Base class for time-sampled corrections
        - Adds an interpolating index of type datetime
        - Enforces rules on inserting new data points
    Since extrapolation is allowed for ONLINE versions
    Inserting new points before the cutoff is disallowed
    This is to prevent setting values for times already
    processed using the extrapolated values.
    When inserting an ONLINE value after the cutoff, a
    new document with equal values to the extrapolated values
    is inserted at the current time to prevent the inserted document
    from affecting the interpolated values that have already been used
    for processing.
    """
    class Config:
        allow_population_by_field_name = True
        
    _NAME = ""

    time: datetime.datetime = rframe.InterpolatingIndex(extrapolate=can_extrapolate,
                                                        alias='run_id')

    @validator('time', pre=True)
    def run_id_to_time(cls, v):
        """Convert run id to time"""
        if isinstance(v, (str, int)):
            try:
                v = settings.run_id_to_time(v)
            except:
                pass
        return v

    @classmethod
    def url_protocol(cls, attr, **labels):
        labels["time"] = settings.extract_time(labels)
        return super().url_protocol(attr, **labels)

    def pre_insert(self, datasource):
        # Inserting ONLINE versions can affect the past
        # since extrapolation until the current time is allowed
        # extrapolation will just give the last value,
        # verses interpolation which is calculated from the last
        # value and also the newly inserted value.
        # For this reason, when inserting ONLINE versions
        # an additional document is inserted with the current time
        # and values equal to the latest existing document.
        # This sets all values from the latest document time until now
        # permanently to the values that would have been used in processing.
        if self.version == "ONLINE":
            clock = settings.clock
            cutoff = clock.cutoff_datetime(buffer=60)

            assert clock.after_cutoff(
                self.time
            ), f"Can only insert online \
                                                    values after {cutoff}."

            new_index = self.index_labels
            new_index["time"] = clock.cutoff_datetime(buffer=1)

            existing = self.find(datasource, **new_index)
            # If cutoff time is already set, the values may have been
            # used already for processing. We add a sample at the
            # cutoff time to force interpolation and extrapolation
            # to match from the last existing sample until the cutoff.
            if existing:
                new_doc = existing[0]
                new_doc.save(datasource)
