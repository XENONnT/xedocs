import datetime
import time

import pytz
import pandas as pd


class SimpleClock:
    utc: bool
    tz_aware: bool
    cutoff_offset: float

    def __init__(self, utc=True, tz_aware=True, cutoff_offset=3600) -> None:
        self.utc = utc
        self.tz_aware = tz_aware
        self.cutoff_offset = cutoff_offset

    def current_datetime(self):
        if self.utc:
            now = datetime.datetime.utcnow()
        else:
            now = datetime.datetime.now()
        return self.normalize_tz(now)

    def cutoff_datetime(self, buffer=0.0):
        offset = datetime.timedelta(seconds=self.cutoff_offset + buffer)
        return self.current_datetime() + offset

    def normalize_tz(self, dt: datetime.datetime) -> datetime.datetime:
        if isinstance(dt, str):
            dt = pd.to_datetime(dt, utc=self.utc)
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        if dt.tzinfo is not None:
            if dt.tzinfo.utcoffset(dt) is not None and self.utc:
                dt = dt.astimezone(pytz.utc)
        elif self.utc:
            dt = dt.replace(tzinfo=pytz.utc)
        if not self.tz_aware:
            dt = dt.replace(tzinfo=None)
            
        dt = dt.replace(microsecond=int(dt.microsecond / 1000) * 1000)
    
        return dt

    def after_cutoff(self, dt, buffer=0.0):
        cutoff = self.cutoff_datetime(buffer)
        dt = self.normalize_tz(dt)
        return dt > cutoff

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not hasattr(v, "after_cutoff"):
            raise TypeError("Clock must implement `after_cutoff`")

        if not hasattr(v, "cutoff_datetime"):
            raise TypeError("Clock must implement `cutoff_datetime`")

        if not hasattr(v, "current_datetime"):
            raise TypeError("Clock must implement `current_datetime`")

        if not hasattr(v, "normalize_tz"):
            raise TypeError("Clock must implement `normalize_tz`")

        return v


class FrozenClock(SimpleClock):
    now: datetime.datetime

    def __init__(self, now: datetime.datetime, utc=True, cutoff_offset=3600) -> None:
        super().__init__(utc=utc, cutoff_offset=cutoff_offset)
        self.now = self.normalize_tz(now)

    def current_datetime(self):
        return self.now
